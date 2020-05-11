import sys
import os
import time, functools
import json, re
import tweepy
import nltk
import logging, time
import nltk.data
from multiprocessing import Process
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from shpprocess import SHPProcessor
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from couch_setup import CouchDBInstance
nltk.download('punkt')
nltk.download('vader_lexicon')
'''

This file contains methods to harvest tweets in Australia (and only geo-tagged tweets) using the the twitter APIs referenced on this page:
https://developer.twitter.com/en/docs/api-reference-index

Noted by developer.twitter.com:
- "Limit your searches to 10 keywords and operators".
- "The Search API is not complete index of all Tweets, but instead an index of recent Tweets.
   The index includes between 6-9 days of Tweets".

Query operator reference:
https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators

TODO:
- Filter results by month/week/date so we avoid duplicates on multiple calls.

"pip install tweepy" for the tweepy package.
Alternatively, "pip install git+https://github.com/tweepy/tweepy.git".

'''

# Query parameters.

AUS_GEOCODE = '-28.071981,134.078631,2137km'
AUS_BOUNDS = [112.62,-44.12,154.11,-10.84]
API_TYPE = 0
DB_URL = 'http://127.0.0.1:5984'
RESULT_FILE = 1
QUERY_FILE = 2
RESULT_SIZE = 3
STREAM_ARGS = 2
SEARCH_ARGS = 4
STREAM_TYPE = 'stream'
SEARCH_TYPE = 'search'

# API keys and tokens. (Set these keys and tokens to your own if possible to avoid rate limits)

API_KEY = 'a72kdQ5oX4rHeEuFxocnso92k'
API_SECRET = 'YeNIi26sjDGSzIkzNcxxW6lXLSXpkJKBRZtmPDeJnxpE9RvsBj'
ACCESS_TOKEN = '1251717183920472065-OLi7brCOdt9hqHfoBM2zl8VrQvSgP8'
ACCESS_SECRET = 'J0uLQohJhxZxq1iOZjiDxa9cpOg8tgKhP23wuDc6Nlb76'


# Class to process tweets
class TweetProcessor():
    def __init__(self, type):

        self.shp = SHPProcessor("SA2")
        self.covid_words = self.get_covid_words()
        print("SHP files processed")
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.analyser = SentimentIntensityAnalyzer()
        self.type=type

    # process tweets: add location, add sentiment, covid19 relevance
    def process_status(self, tweet):

        if tweet.coordinates is not None or tweet.place is not None:
            tweet_json = tweet._json
            location_data = {}


            # add SA2/SA3 field
            if tweet.coordinates is not None:
                new_coords = {}
                new_coords["Longitude"] = tweet.coordinates['coordinates'][0]
                new_coords["Latitude"] = tweet.coordinates['coordinates'][1]
                d = self.shp.match_coordinates(new_coords)
                location_data = self.shp.filter_json(d)
            elif tweet.place.bounding_box.coordinates is not None:
                    place = tweet.place.bounding_box.coordinates[0]
                    d = self.shp.match_bounding_box({"coordinates":place})
                    dj = json.loads(d)
                    if len(dj["features"]) == 0:
                        return None
                    else:
                        location_data = self.shp.filter_json(d)

            # no valid sa2/sa2 found, discard the tweet
            if location_data is None:
                return None


            tweet_with_location = {**tweet_json, **location_data}
            tweet_with_location['doc_type'] = "tweet"

            #get tweet text (need extra work if this is truncated)
            if self.type == STREAM_TYPE:
                if tweet.truncated:
                    body = tweet.extended_tweet["full_text"]
                else:
                    body = tweet.text
            elif self.type == SEARCH_TYPE:
                body = tweet.full_text


            # now look for covid-19 relevance
            t_ = list(map(lambda x: x.lower(), body.split()))
            text = list(map(lambda x: x[1:] if x.startswith('#') else x, t_))
            covid_relevant = False
            covid_words_set = set(self.covid_words)
            tweet_set = set(text)

            for x in self.covid_words:
                if len(x.split()) > 1:
                    x_ = set(x.split())
                    if x_ <= tweet_set:
                        covid_relevant = True
                        break
                elif x in text:
                    covid_relevant = True
                    break

            tweet_with_location['covid_relevant'] = covid_relevant
            if tweet.lang == "en":
                 # punkt sentence detector
                sentences = self.sent_detector.tokenize(body.strip())
                sentences_remove_userrefs = list(map(lambda x: self.remove_user(x), sentences))
                sentences_remove_urls = list(filter(lambda x: self.url_free(x),sentences_remove_userrefs))
                if len(sentences_remove_urls) > 0:

                    best_sentence = max(sentences_remove_urls, key=len)
                    try:
                        tweet_scores = self.analyser.polarity_scores(best_sentence)
                        tweet_with_location["score"] = tweet_scores["compound"]
                    except ValueError:
                        # no score
                        return tweet_with_location

            return tweet_with_location

        return None

    def remove_user(self, x):
        no_user = re.sub("@[_A-Za-z0-9]+","", x)
        no_hashtag = re.sub('[#]', '', no_user)
        stripped = no_hashtag.strip()
        return stripped

    def url_free(self, string):
        url_strings = ['http', 't.co', 'www']
        for x in url_strings:
            if x in string:
                return False
        return True

    def get_covid_words(self):
        words = []
        with open("twitter-harvester/covid_words.txt", "r") as f:
            for line in f.readlines():
                words.append(line.strip())
        return words



# Stream API class.

class TwitterListener(StreamListener):

    def __init__(self, couchdb):
        super().__init__()
        self.processor = TweetProcessor(STREAM_TYPE)
        self.couchdb = couchdb


    def process_and_insert_tweet(self, status):
        status = self.processor.process_status(status)
        if status == None:
            return True
        self.couchdb.insertTweet(status)


    def on_status(self, status):
        p = Process(target=self.process_and_insert_tweet, args=(status,))
        p.start()
        return True


    def on_error(self, status_code):
        if status_code == 420:
            return False
        return True




# Error handling.

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print("Rate limit hit, waiting...")
            time.sleep(60 * 16)
            continue
        except tweepy.error.TweepError:
            print("Caught tweepy error: %s \n" % tweepy.error.response.text)
        except StopIteration:
            print("StopIteration Exception.")
            break


def start_search(type="search", filename="twitter-harvester/query-config.txt", num=50, q=1):

    '''
        Change DBURL if necessary. This WILL take few minutes one first try, since it sets up aurin data
    '''
    couchdb = CouchDBInstance(DB_URL)

    if type == SEARCH_TYPE:
        processor = TweetProcessor(SEARCH_TYPE)

        with open(filename, 'r') as f:
            query = f.readline().rstrip()
        print("Searching using query: ")
        print(query)

    auth = OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    api = tweepy.API(auth_handler = auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

    if type == STREAM_TYPE:
        print("Starting stream.")
        twitter_stream = Stream(api.auth, TwitterListener(couchdb=couchdb), tweet_mode="extended")
        twitter_stream.filter(locations = AUS_BOUNDS) # no other filters available


    elif type == SEARCH_TYPE:
        max_id = 0
        with open('max_id.txt', 'r') as f:
            max_id = int(f.read().strip())

        total_tweets_collected = 0

        print("searching with standard API")
        try:
            print("Creating standard api search request...")
            # result = tweepy.Cursor(api.search, q = query, geocode = AUS_GEOCODE, result_type = 'recent', count = 100, max = max_id).items()
            for page in  tweepy.Cursor(api.search, q = query, geocode = AUS_GEOCODE, result_type = 'recent', max = max_id, tweet_mode="extended").pages():
                for tweet in page:
                    tweet_with_location = processor.process_status(tweet)

                    if tweet_with_location is None:
                        continue

                    # insert into couchdb
                    couchdb.insertTweet(tweet_with_location)

                    total_tweets_collected += 1

                    if tweet.id < max_id:
                        max_id = tweet.id

                with open('max_id.txt', 'w') as f:
                    f.write(str(max_id))


        except tweepy.TweepError as e:
            print("Tweepy error: " + str(e))


    print("Done.")
