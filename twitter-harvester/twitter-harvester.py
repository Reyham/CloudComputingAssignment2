import sys
import os
import time
import json
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

'''

<<<<<<< HEAD
This script harvests tweets in Australia using the the twitter APIs referenced on this page:
=======
This script harvests tweets in Australia (and only geo-tagged tweets) using the the twitter APIs referenced on this page: 
>>>>>>> 109fd47a6b0842be18fef752a49d585f426d8165
https://developer.twitter.com/en/docs/api-reference-index

It takes in three arguments: the query filename, output filename and the desired result size (possibly a few thousand or million) as command line arguments.
e.g. "python twitter-harvester.py search output.json query-config.txt 50"
e.g. "python twitter-harvester.py stream output.json"
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

<<<<<<< HEAD
=======
"pip install tweepy" for the tweepy package.
Alternatively, "pip install git+https://github.com/tweepy/tweepy.git".
   
>>>>>>> 109fd47a6b0842be18fef752a49d585f426d8165
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

# API keys and tokens. (Set these keys and tokens to your own if possible to avoid rate limits)

API_KEY = 'JaPsT25AdrztzNThyujhdY16w'
API_SECRET = 'tCKxQnjJPwlieC6qFrZjdvpX9RMY68fXdKR7mZHo7fKsWtxk9k'
ACCESS_TOKEN = '1252018342069583872-lBzju61OboRigAImgA61lDOYN6Wevm'
ACCESS_SECRET = 'P78iLHd5Y6ZivLPWJ9APFmcXBSniiuUxybiqjSwt9nHjV'

# Stream API class.

class TwitterListener(StreamListener):

    def __init__(self, output_file):
        super().__init__()
        self.output_file = output_file

    def on_data(self, data):
        try:
            with open(self.output_file, 'a') as f:
                f.write(data.rstrip())
                f.write("\n")
                return True
        except BaseException as e:
            print("Error: %s" % str(e))
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
 
# Main. 
 
if __name__ == "__main__":

    # Input validation.

    arguments = sys.argv
    arguments.pop(0)
<<<<<<< HEAD

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

=======
    
    # Check there are arguments.
    
    if len(arguments) < 1:
        print("Example commandline configurations: ")
        print("python twitter-harvester.py stream output.json")
        print("python twitter-harvester.py search output.json query-config.txt 50")
        sys.exit()
    
    # Check whether first argument is either search or stream.
    
    if arguments[API_TYPE] == SEARCH_TYPE:
        
        # Check there are four arguments.
        
        if len(arguments) != SEARCH_ARGS:
            print("Example search configurations: \n")
            print("python twitter-harvester.py search query-config.txt output.json 50")
            sys.exit()
        
        # Check the fourth argument is an integer.
        
        try:
            int(arguments[RESULT_SIZE])
        except ValueError:
            print("Second argument must be an integer.\n")
            sys.exit()
        
        with open(arguments[QUERY_FILE], 'r') as f:
            query = f.readline().rstrip()
        
        print("Searching using query: ")
        print(query)
    
    elif arguments[API_TYPE] == STREAM_TYPE:
        
        # Check there are two arguments.
        
        if len(arguments) != STREAM_ARGS:
            print("Example stream configurations: \n")
            print("python twitter-harvester.py stream output.json")
            sys.exit()
    
    else:
        print("First argument should be either stream or search.")
        sys.exit()
        
    
>>>>>>> 109fd47a6b0842be18fef752a49d585f426d8165
    # Set up twitter API.

    auth = OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
<<<<<<< HEAD


    api = tweepy.API(auth)

    result = tweepy.Cursor(api.search, q = query, geocode = AUS_GEOCODE).items(int(arguments[RESULT_SIZE]))

    with open(arguments[RESULT_FILE], 'a') as f:
        for tweet in result:
            f.write(json.dumps(tweet._json))
            f.write("\n")

    '''
    twitter_stream = Stream(auth, TwitterListener(output_file = arguments[RESULT_FILE]))
    print("Stream start.")
    twitter_stream.filter(locations = AUS_BOUNDS)
    '''
=======
    
    api = tweepy.API(auth_handler = auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
    
    # Collect tweets.
    
    if arguments[API_TYPE] == STREAM_TYPE:
        print("Starting stream.")
        twitter_stream = Stream(auth, TwitterListener(output_file = arguments[RESULT_FILE]))
        twitter_stream.filter(locations = AUS_BOUNDS)
    
    elif arguments[API_TYPE] == SEARCH_TYPE:
        
        print("Starting search.")
        
        total_tweets_collected = 0
        since_id = 0
        
        with open(arguments[RESULT_FILE], 'a') as f:
            try:
                print("Creating request...")
                result = tweepy.Cursor(api.search, q = query, geocode = AUS_GEOCODE, result_type = 'recent', count = 100, since_id = since_id).items()
                
                for tweet in result:
                
                    # Check if tweet has the coordinates or place attributes.
                    if tweet.coordinates is not None or tweet.place is not None:
                        f.write(json.dumps(tweet._json))
                        f.write("\n")
                        total_tweets_collected += 1
                        print(total_tweets_collected)
                    
                    if tweet.id > since_id:
                        since_id = tweet.id
                    
                    if total_tweets_collected >= int(arguments[RESULT_SIZE]):
                        break
            
            except tweepy.TweepError as e:
                print("Tweepy error: " + str(e))
        
        with open('since_id.txt', 'w') as f:
            f.write(str(since_id));
        
    print("Done.")
>>>>>>> 109fd47a6b0842be18fef752a49d585f426d8165
