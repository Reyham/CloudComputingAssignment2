import uuid, time
from cloudant import couchdb, replicator
from cloudant.design_document import DesignDocument
from cloudant.query import Query, QueryResult
from cloudant.database import CouchDatabase
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View
'''
    Given a database url, this class setups as a database, and demonstrates
    how to make a replica with cloudant

    CouchDBInstance is the main interface with CouchDB. The class contains
    methods to insert tweets, setup AURIN data
'''
DB_NAME = "database"
# DB_NAME = "db6"
USERNAME = "admin"
PASSWORD = "admin" # change this?
PARTITION_KEY = "partition1"
DB_URL = 'http://127.0.0.1:5984'

class CouchDBInstance():
    def __init__(self, url=DB_URL):
        client = CouchDB(user=USERNAME, auth_token=PASSWORD, url=DB_URL, connect=True, auto_renew=True, use_basic_auth=True)
        self.db = CouchDatabase(client, DB_NAME, fetch_limit=100, partitioned=False)


    def insertTweet(self, tweet):

        q = Query(self.db, use_index="_design/tweet_id", selector={'tweet_id': {'$eq': tweet["tweet_id"]}})
        result = q.result[:]

        if len(result) > 0:
            return
        else:

            partition_key = PARTITION_KEY
            document_key = str(uuid.uuid4())
            tweet['_id'] = ':'.join((partition_key, document_key))
            self.db.create_document(tweet)

    def delete_all(self):
        for document in self.db:
            document.delete()



    def loadView(self, filename):
        map = ""
        reduce = ""
        with open(filename) as ddoc:
            val = ""
            nnl = False
            for x in ddoc.readlines():
                val = val + x.strip()

                if x.strip() == "" and not nnl: # newline
                    map = val
                    val = reduce
                    nnl = True # one map reduce per file
                if nnl:
                    reduce = val
            return (map, reduce)


# populate db with aurin data for each scenario
#i = CouchDBInstance('http://127.0.0.1:5984')
#i.insert_AURIN_if_not_exists()
