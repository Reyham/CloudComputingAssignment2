import pycurl, datetime, json
from io import BytesIO
from urllib.parse import urlencode
from tweet_processor import TweetProcessor
from couch_setup import CouchDBInstance
import time



def retrieve_tweets(city, start_year, start_month, start_day, end_year, end_month, end_day):
    buffer = BytesIO()


    start_key = [city, start_year, start_month, start_day]
    end_key = [city, end_year, end_month, end_day]
    retries = 5
    vals = {'start_key' : start_key,
            'end_key':end_key,
            'reduce':"false",
            'include_docs':"true"}

    params_ = urlencode(vals)
    # weirdly, urllib uses single quotes to encase strings, but couch needs double quotes. took me forever to debug :(

    params = params_.replace('%27', '%22')
    url = "http://45.113.232.90/couchdbro/twitter/_design/twitter/_view/summary"
    c = pycurl.Curl()

    c.setopt(c.URL, url+"?"+params)
    c.setopt(c.HTTPGET, 1)
    c.setopt(c.USERPWD,"readonly:ween7ighai9gahR6")
    c.setopt(c.WRITEDATA, buffer)
    success = False
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


def harvest_cloud_city_tweets(city, tp):
    limit = 50
    couchdb = CouchDBInstance()

    now = datetime.datetime.now()
    past = now - datetime.timedelta(days=1)

    print('harvesting tweets for city: ', city)

    res = retrieve_tweets(city, past.year, past.month, past.day, now.year, now.month, now.day)
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

        for tweet in res['rows']:
            processed_tweet = tp.process_archived_status(tweet)
            if processed_tweet is not None:
                couchdb.insertTweet(processed_tweet)

        now = past
        past = now - datetime.timedelta(days=1)

        res = retrieve_tweets(city, past.year, past.month, past.day, now.year, now.month, now.day)
