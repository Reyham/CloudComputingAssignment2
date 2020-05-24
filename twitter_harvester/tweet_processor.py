import nltk, re, json, time, sys
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from twitter_harvester.shpprocess import SHPProcessor

import pathlib
path = str(pathlib.Path(__file__).parent.absolute())

nltk.download('punkt')
nltk.download('vader_lexicon')
'''
    WE ADD THE FOLLOWING FIELDS TO TWEETS (in process_status)
    [score] -> sentiment calculate_sentiment(body)
    [covid_relevant] -> relevance to covid is_covid_relevant(body)
    [tweet_id] -> couchdb doesn't like us using an id/id_str field, so use this instead

'''
STREAM_TYPE = 'stream'
SEARCH_TYPE = 'search'
CLOUD_TYPE = 'cloud'

# Class to process tweets
class TweetProcessor():
    def __init__(self, type):

        self.shp = SHPProcessor("SA2")
        self.covid_words = self.get_covid_words()
        print("SHP files processed")
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.analyser = SentimentIntensityAnalyzer()
        self.type=type

    # parsing json tweets from richard means handling k,v pairs, not attributes from tweepy Cursor
    def process_archived_status(self, kv):
        tweet = kv['doc']
        if tweet['coordinates'] is not None or tweet['place'] is not None:
            location_data = {}
            if tweet['coordinates'] is not None:
                new_coords = {}
                new_coords["Longitude"] = tweet['coordinates']['coordinates'][0]
                new_coords["Latitude"] = tweet['coordinates']['coordinates'][1]
                d = self.shp.match_coordinates(new_coords)
                location_data = self.shp.filter_json(d)
            elif tweet['place']['bounding_box']['coordinates'] is not None:
                place = tweet['place']['bounding_box']['coordinates'][0]
                d = self.shp.match_bounding_box({"coordinates":place})
                dj = json.loads(d)
                if len(dj["features"]) == 0:
                    return None
                else:
                    location_data = self.shp.filter_json(d)

            # no valid sa2/sa2 found, discard the tweet
            if location_data is None:
                return None

            tweet_with_location = {**tweet, **location_data}
            tweet_with_location['doc_type'] = "tweet"

            if 'full_text' in tweet:
                body = tweet['full_text']
            else:
                body = tweet['text']

            tweet_with_location['covid_relevant'] = self.is_covid_relevant(body)

            if tweet['lang'] == 'en':
                score = self.calculate_sentiment(body)
                if score is not None:
                    tweet_with_location['score'] = score
            try:
                id = tweet_with_location.pop('_id')
                tweet_with_location.pop('id')
                tweet_with_location['tweet_id'] = int(id)
                tweet_with_location['tweet_id_str'] = tweet_with_location.pop('id_str')
                tweet_with_location['doc_source'] = "couchdb"

            except ValueError:
                return None
            return tweet_with_location
        return None

    # process tweets from tweepy cursor: add location, add sentiment, covid19 relevance
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
            tweet_with_location['covid_relevant'] = self.is_covid_relevant(body)
            if tweet.lang == "en":
                score = self.calculate_sentiment(body)
                if score is not None:
                    tweet_with_location['score'] = score
            tweet_with_location['tweet_id'] = tweet_with_location.pop('id')
            tweet_with_location['tweet_id_str'] = tweet_with_location.pop('id_str')
            return tweet_with_location

        return None

    def calculate_sentiment(self, body):
        sentences = self.sent_detector.tokenize(body.strip())
        sentences_remove_userrefs = list(map(lambda x: self.remove_user(x), sentences))
        sentences_remove_urls = list(filter(lambda x: self.url_free(x),sentences_remove_userrefs))
        if len(sentences_remove_urls) > 0:
            best_sentence = max(sentences_remove_urls, key=len)
            tweet_scores = self.analyser.polarity_scores(best_sentence)
            if "compound" in tweet_scores:
                return tweet_scores["compound"]
        return None



    def is_covid_relevant(self, body):
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
        return covid_relevant


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
        with open(path + "/covid_words.txt", "r") as f:
            for line in f.readlines():
                words.append(line.strip())
        return words
