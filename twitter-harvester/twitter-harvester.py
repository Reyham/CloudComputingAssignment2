import sys
import os
import time
import json
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

'''

This script harvests tweets in Australia using the the twitter APIs referenced on this page: 
https://developer.twitter.com/en/docs/api-reference-index

It takes in three arguments: the query filename, output filename and the desired result size as command line arguments.
e.g. "python twitter-harvester.py query-config.txt output.json 50"
Results are stored as a JSON file output. 
The final part of the script starts a collection stream of all the tweets in Australia.

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
DESIRED_TOTAL_TWEETS = 5000000
QUERY_FILE = 0
RESULT_FILE = 1
RESULT_SIZE = 2
NUMBER_OF_ARGUMENTS = 3

# API keys and tokens.

API_KEY = 'JaPsT25AdrztzNThyujhdY16w'
API_SECRET = 'tCKxQnjJPwlieC6qFrZjdvpX9RMY68fXdKR7mZHo7fKsWtxk9k'
ACCESS_TOKEN = '1252018342069583872-lBzju61OboRigAImgA61lDOYN6Wevm'
ACCESS_SECRET = 'P78iLHd5Y6ZivLPWJ9APFmcXBSniiuUxybiqjSwt9nHjV'

class TwitterListener(StreamListener):
    
    def __init__(self, output_file):
        super().__init__()
        self.output_file = output_file
    
    def on_data(self, data):
        try:
            with open(self.output_file, 'a') as f:
                f.write(data)
                return True
        except BaseException as e:
            print("Error: %s" % str(e))
        return True
    
    def on_error(self, status_code):
        if status_code == 420:
            return False

if __name__ == "__main__":
    
    # Input validation.
    
    arguments = sys.argv
    arguments.pop(0)
    
    # Check there are three arguments.
    
    if len(arguments) != NUMBER_OF_ARGUMENTS:
        print("Needs an input file, output file and the desired size of the result.\n")
        sys.exit()
    
    # Check the third argument is an integer.
    
    try:
        int(arguments[RESULT_SIZE])
    except ValueError:
        print("Second argument must be an integer.\n")
        sys.exit()
    
    with open(arguments[QUERY_FILE], 'r') as f:
        query = f.readline().rstrip()
    
    print("Searching using query: ")
    print(query)
    
    # Set up twitter API.
    
    auth = OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    
    api = tweepy.API(auth)
    
    totalTweetsCollected = 0
    
    # Collect tweets.
    
    while (totalTweetsCollected <= DESIRED_TOTAL_TWEETS):
        try:
            result = tweepy.Cursor(api.search, q = query, geocode = AUS_GEOCODE).items(int(arguments[RESULT_SIZE]))
            
            with open(arguments[RESULT_FILE], 'a') as f:
                for tweet in result:
                    f.write(json.dumps(tweet._json))
                    f.write("\n")
                    totalTweetsCollected += 1
            
            '''
            twitter_stream = Stream(auth, TwitterListener(output_file = arguments[RESULT_FILE]))
            print("Stream start.")
            twitter_stream.filter(locations = AUS_BOUNDS)
            '''
        
        except tweepy.RateLimitError:
            print("Hit twitter API limit, waiting 16 minutes...")
            time.sleep(60 * 16);
        
        except tweepy.error.TweepError:
            print("Caught tweepy error: %s \n" % tweepy.error.response.text)
            
        
    