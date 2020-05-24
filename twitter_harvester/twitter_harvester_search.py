import sys
import os, multiprocessing
import time, functools
import json, re
import tweepy
import nltk
import logging, time
import nltk.data
from twitter_harvester.tweet_processor import TweetProcessor
from multiprocessing import Process
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from couch_setup import CouchDBInstance
from urllib3.exceptions import ProtocolError

import pathlib
path_ = pathlib.Path(__file__).parent.absolute()
parent_ = path_.parent.absolute()

path = str(path_)
parent_path = str(parent_)


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
RESULT_FILE = 1
QUERY_FILE = 2
RESULT_SIZE = 3
STREAM_ARGS = 2
SEARCH_ARGS = 4
STREAM_TYPE = 'stream'
SEARCH_TYPE = 'search'
CLOUD_TYPE = 'cloud'

# API keys and tokens. (Set these keys and tokens to your own if possible to avoid rate limits)

API_KEY = 'a72kdQ5oX4rHeEuFxocnso92k'
API_SECRET = 'YeNIi26sjDGSzIkzNcxxW6lXLSXpkJKBRZtmPDeJnxpE9RvsBj'
ACCESS_TOKEN = '1251717183920472065-OLi7brCOdt9hqHfoBM2zl8VrQvSgP8'
ACCESS_SECRET = 'J0uLQohJhxZxq1iOZjiDxa9cpOg8tgKhP23wuDc6Nlb76'


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



def start_search(type="search", num=50, q=1):

    '''
        Change DBURL if necessary. This WILL take few minutes one first try, since it sets up aurin data
    '''
    couchdb = CouchDBInstance()

    if type == SEARCH_TYPE:
        processor = TweetProcessor(SEARCH_TYPE)
        filename = path + "/query-config.txt"

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
        while True:
            try:
                twitter_stream.filter(locations = AUS_BOUNDS) # no other filters available
            except ProtocolError:
                continue

    elif type == SEARCH_TYPE:
        max_id = 0
        with open(path + '/max_id.txt', 'r') as f:
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

                with open(path + '/max_id.txt', 'w') as f:
                    f.write(str(max_id))


        except tweepy.TweepError as e:
            print("Tweepy error: " + str(e))

    elif type == CLOUD_TYPE:
        cities = ("adelaide", "brisbane", "canberra", "melbourne", "hobart", "sydney", "perth")
        # spawn child processes for all cities



    print("Done.")
