#!/usr/bin/env python
import sys
sys.path.append("..")
import json
from itertools import islice
from tweet_processor import TweetProcessor
from couch_setup import CouchDBInstance

couch_db = CouchDBInstance()
tp = TweetProcessor("search")

n= 10
def insert_to_couch(tweet):
    status = tp.process_archived_status(tweet)
    if status is None:
        return True
    couch_db.insertTweet(status)

if __name__ == "__main__":
    
    DATASET = 'twitter-melb.json'
    from itertools import islice
    # skip line 1
    with open(DATASET, "r", encoding='utf-8') as f:
        list(islice(f, 1))
        while True:
            next_n_lines = list(islice(f, n))
            # print(next_n_lines, "\n")
            if not next_n_lines:
                break
            for tweet in next_n_lines:
                j = json.loads(tweet.rstrip(",\n"))
                insert_to_couch(j)
