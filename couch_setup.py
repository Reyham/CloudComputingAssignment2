import uuid, time
import aurin_json
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

    def insert_AURIN_if_not_exists(self):
        q = Query(self.db, use_index="_design/tweet_id", selector={'doc_type': {'$eq': "has_all_aurin"}})
        result = q.result[:]
        print(result)
        if len(result) == 0:
            print("commencing AURIN spatial data upload!")
            x = aurin_json.setup_geo_economy_data()
            y = aurin_json.setup_geo_trust_data()
            z = aurin_json.setup_geo_election_data()
            q = aurin_json.setup_migration_data()

            for geodata in x + y + z + q:
                self.insertAURIN(geodata)

            print("AURIN upload complete!")
            # insert marker to prevent duplicate upload of data
            json = {"doc_type":"has_all_aurin"}
            self.insertAURIN(json)
        else:
            print("AURIN data already loaded!")


    def insertAURIN(self, json):
        partition_key = PARTITION_KEY
        document_key = str(uuid.uuid4())
        json['_id'] = ':'.join((partition_key, document_key))
        self.db.create_document(json)


    def insertTweet(self, tweet):
        # query if tweet exists
        #print(tweet)
        #t1 = time.time()
        q = Query(self.db, use_index="_design/tweet_id", selector={'tweet_id': {'$eq': tweet["tweet_id"]}})
        result = q.result[:]
        #if len(result) > 0:
        #print("not inserting", tweet["tweet_id"], result[0]["tweet_id"], result[0]["created_at"])
        #t2 = time.time()
        #print(t2-t1, "DIFF")
        if len(result) > 0:
            # print("FOUND", tweet, "\n", result, "\n")
            return
        else:
            # t1 = time.time()
            # print("inserting!")
            partition_key = PARTITION_KEY
            document_key = str(uuid.uuid4())
            tweet['_id'] = ':'.join((partition_key, document_key))
            self.db.create_document(tweet)
            # t2 = time.time()
            # print(t2-t1, "DIFF")
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
