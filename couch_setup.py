import uuid
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
# DB_NAME = database
DB_NAME = "db6"
USERNAME = "admin"
PASSWORD = "1234"
PARTITION_KEY = "partition1"
DB_URL = 'http://127.0.0.1:5984'

class CouchDBInstance():
    def __init__(self, url=DB_URL):
        self.create_db(db_url=url, db_name=DB_NAME)

        client = CouchDB(user=USERNAME, auth_token=PASSWORD, url=url, connect=True, auto_renew=True, use_basic_auth=True)
        self.db = CouchDatabase(client, DB_NAME, fetch_limit=100, partitioned=False)


    def insertAURIN(self, db, json):
        partition_key = PARTITION_KEY
        document_key = str(uuid.uuid4())
        json['_id'] = ':'.join((partition_key, document_key))
        db.create_document(json)


    def insertTweet(self, tweet):
        # query if tweet exists
        q = Query(self.db, use_index="_design/tweet_id", selector={'tweet_id': {'$eq': tweet["tweet_id"]}})
        result = q.result[:]
        if len(result) > 0:
            return
        else:
            partition_key = PARTITION_KEY
            document_key = str(uuid.uuid4())
            tweet['_id'] = ':'.join((partition_key, document_key))
            self.db.create_document(tweet)

    def delete_all(self, db):
        for document in db:
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


    # create db if not exists
    # connect to name database locally, <admin, admin>
    def create_db(self, db_name, db_url, name="admin", password="1234"):
        with couchdb(user=name, passwd=password, url=db_url, connect=True, auto_renew=True) as client:
            dbs = client.all_dbs()

            if db_name not in dbs:
                print("creating db")
                db = client.create_database(DB_NAME)
                dd = DesignDocument(db, document_id="cloud_views")

                # create json_query indexes
                try:
                    db.create_query_index(design_document_id="sa2_code16", fields= ["sa2_code16"])
                    db.create_query_index(design_document_id="sa3_code16", fields = ["sa3_code16"])
                    db.create_query_index(design_document_id="gcc_code16", fields = ["gcc_code16"])
                    db.create_query_index(design_document_id="tweet_id", fields=["tweet_id"])
                    db.create_query_index(design_document_id="doc_type", fields=["doc_type"])

                    # create replicas
                    # replicator.Replicator(client).create_replication(db, db1, continuous=True)

                    # add aurin_data
                    print("adding aurin data...")
                    x = aurin_json.setup_geo_economy_data()
                    y = aurin_json.setup_geo_trust_data()
                    z = aurin_json.setup_geo_election_data()
                    q = aurin_json.setup_migration_data()

                    for geodata in x + y + z + q:
                        self.insertAURIN(db, geodata)

                    # add views

                    return db_name
                except Error:
                    print("Error, could not create database")
                    return
            else:
                return db_name






# populate db with aurin data for each scenario
# i = CouchDBInstance('http://127.0.0.1:5984')
# i.insertTweet({})
