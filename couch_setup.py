import uuid
import aurin_json
from cloudant import couchdb, replicator
from cloudant.design_document import DesignDocument

'''
    Given a database url, this class setups as a database, and demonstrates
    how to make a replica with cloudant
'''

class CouchDBInstance():
    def __init__(self, url):
        self.create_db(url)



    def insert(self, db, json):
        partition_key = "partition1"
        document_key = str(uuid.uuid4())
        json['_id'] = ':'.join((partition_key, document_key))
        db.create_document(json)


    def delete_all(self, db):
        for document in db:
            document.delete()




    def create_db(self, db_url):
        with couchdb("admin", '1234', url=db_url, connect=True, auto_renew=True) as client:
            db = client.create_database("db")
            if not db.exists():
                print("Error, could not create database")
                return

            # create json_query indexes
            db.create_query_index(fields=["sa2_code16", "sa3_code16, doc_type"])

            # create reduce functions to aggregate twitter results (using cURL bc it's easier)


            # dummy for replica
            # db1 = client.create_database("db1")

            # create replicas
            # replicator.Replicator(client).create_replication(db, db1, continuous=True)


            # test upload
            x = aurin_json.setup_geo_economy_data()
            y = aurin_json.setup_geo_trust_data()
            z = aurin_json.setup_geo_election_data()
            q = aurin_json.setup_migration_data()

            for geodata in x + y + z + q:
                self.insert(db, geodata)

            print("Completed AURIN data upload to CouchDB")

# populate db with aurin data for each scenario
i = CouchDBInstance('http://127.0.0.1:5984')
