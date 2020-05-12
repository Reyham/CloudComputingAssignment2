import pycurl, datetime, json, sys
from io import BytesIO
from urllib.parse import urlencode
from tweet_processor import TweetProcessor
from couch_setup import CouchDBInstance
import time



def retrieve_tweets(city, start_year, start_month, start_day, end_year, end_month, end_day, id):
    buffer = BytesIO()


    start_key = [city, start_year, start_month, start_day]
    end_key = [city, end_year, end_month, end_day]
    retries = 5
    vals = {'start_key' : start_key,
            'end_key':end_key,
            'reduce':"false",
            'include_docs':"true",
            'limit': 5}

    if id is not None:
        print("idd")
        vals['start_key_doc_id'] = id

    params_ = urlencode(vals)
    # weirdly, urllib uses single quotes to encase strings, but couch needs double quotes. took me forever to debug :(

    params = params_.replace('%27', '%22')
    url = "http://45.113.232.90/couchdbro/twitter/_design/twitter/_view/summary"
    c = pycurl.Curl()

    print(params)

    c.setopt(c.URL, url+"?"+params)
    c.setopt(c.HTTPGET, 1)
    c.setopt(c.USERPWD,"readonly:ween7ighai9gahR6")
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    return json.loads(buffer.getvalue().decode('utf-8'))
    '''
    while retries > 0:
        try:
            c.perform()
            success = True
        except pycurl.error:
            retries -= 1
            time.sleep(5)
            print(pycurl.error)
    if success:
        return json.loads(buffer.getvalue().decode('utf-8'))
    else:
        return None
    '''

def read_id(city):
    try:
        with open("./cloud_skip/" + city + "_offset.txt", "r+") as f:
            x = int(f.read().strip())
            return x
    except (IOError, ValueError) as e:
        print(e)
        return None


def write_id(city, id):
    try:
        with open("./cloud_skip/" + city + "_offset", "w+") as f:
            f.write(str(id))
    except IOError:
        return None

def harvest_cloud_city_tweets(city, tp):
    limit = 50
    couchdb = CouchDBInstance()

    now = datetime.datetime.now()
    past = now - datetime.timedelta(days=1)

    max_id = read_id(city)
    print("start", max_id)

    print('harvesting tweets for city: ', city)

    res = retrieve_tweets(city, past.year, past.month, past.day, now.year, now.month, now.day, max_id)

    if res == None:
        print("Cannot retrieve tweets for ", city)
        return None

    while (now.year != 2020 or now.month != 1 or now.day != 1):
        # process and insert tweets into couchdb
        # pagination is way too slow so we have to make do with keys
        if res is None or 'rows' not in res:
            now = past
            past = now - datetime.timedelta(days=1)
            continue

        max_id = 0
        last_id = -1
        x = 1
        while ('rows' in res and len(res['rows']) > 1):
            max_id = 0
            for tweet in res['rows']:
                if tweet['doc']['id'] > max_id:
                    max_id = tweet['doc']['id']

            # identify and remove tweet with max_id
            print(max_id)
            res_ = list(filter(lambda x: x['doc']['id'] != max_id, res['rows']))
            print(res_)


            for tweet in res_:
                # move out to process ALL TWEETS EXCEPT THE MAX ID TWEET
                processed_tweet = tp.process_archived_status(tweet)
                if processed_tweet is not None:
                    couchdb.insertTweet(processed_tweet)


            # fetch new results, for the same day and city
            print("NEW_TWEETS", max_id)
            res = retrieve_tweets(city, past.year, past.month, past.day, now.year, now.month, now.day, max(ids))


        now = past
        past = now - datetime.timedelta(days=1)

        res = retrieve_tweets(city, past.year, past.month, past.day, now.year, now.month, now.day, None)
        write_id(city, most_recent_id)


'''
vals = {'start_key' : ["adelaide", 2020, 1, 1],
        'end_key': ["adelaide", 2020, 5,1],
        'reduce':"false",
        'include_docs':"true",
        'start_doc_id':1212161563605356544,
        'limit': 10}

params_ = urlencode(vals)
# weirdly, urllib uses single quotes to encase strings, but couch needs double quotes. took me forever to debug :(

params = params_.replace('%27', '%22')
url = "http://45.113.232.90/couchdbro/twitter/_design/twitter/_view/summary"
c = pycurl.Curl()

c.setopt(c.URL, url+"?"+params)
c.setopt(c.HTTPGET, 1)
c.setopt(c.USERPWD,"readonly:ween7ighai9gahR6")
c.perform()
c.close()
'''
