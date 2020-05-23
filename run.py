from twitter_harvester import twitter_harvester_search
from twitter_harvester import twitter_harvester_archived_tweets
import sys
from couch_setup import CouchDBInstance
from multiprocessing import Process
from twitter_harvester.tweet_processor import TweetProcessor

'''
    Main entry point to setup couchdb, and start harvesting tweets
    Configurations –– harvest with stream API, standard API, or both!

    Ex: nohup python3 -u  run.py stream &
        nohup python3 -u run.py search &
        nohup python3 -u run.py cloud &
        node ../front_end/index.js
'''

def do_search(type):
    print("Starting search: ", type)
    if type == "search" or type == "stream":
        twitter_harvester_search.start_search(type=type)



def start_processes(types):
    procs = []
    for type in types:
        if type == "search":
            procs.append(Process(target=do_search, args=("search",)))
        elif type == "stream":
            procs.append(Process(target=do_search, args=("stream",)))
        elif type == "cloud":
            print("Starting couchdb tweet repo search")
            tp = TweetProcessor("search")
            # harvest the data richard provided
            cities = ["melbourne", "brisbane", "sydney", "canberra", "adelaide", "hobart", "perth"]
            # one process for each city
            for c in cities:
                procs.append(Process(target=twitter_harvester_archived_tweets.harvest_cloud_city_tweets,
                            args=(c,tp,)))
        else:
            print("USAGE: python run.py <stream> <search> <cloud>")
            break

    for p in procs:
        p.start()

    for p in procs:
        p.join()

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("USAGE: python run.py <stream> <search> <cloud>")
        sys.exit(1)

    db = CouchDBInstance('http://127.0.0.1:5984')
    db.insert_AURIN_if_not_exists()

    types = sys.argv[1:]
    start_processes(types)
