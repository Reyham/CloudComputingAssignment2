
import json, geojson
from cloudant.design_document import DesignDocument
from cloudant.query import Query, QueryResult
from cloudant.database import CouchDatabase
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View
import aurin_json as aj

DB_NAME = "db6"
# DB_NAME = "db6"
USERNAME = "admin"
PASSWORD = "1234" # change this?
DB_URL = 'http://127.0.0.1:5984'

# iterate through q1 data
client = CouchDB(user=USERNAME, auth_token=PASSWORD, url=DB_URL, connect=True, auto_renew=True, use_basic_auth=True)
db = CouchDatabase(client, DB_NAME)

q = Query(db, selector={'doc_type': {'$eq': 'q1_data'}, 'sa3_code16' : {'$exists' : True}})

q1result = {x['sa3_code16']: x['gini_coefficient_no'] for x in q.result} #gini

q = Query(db, selector={'doc_type': {'$eq': 'q2_data'}, 'sa2_code16' : {'$exists' : True}})

q2result = {} # politics
for r in q.result:
    libvote = r['tpp_liberal_national_coalition_votes']
    labvote = r['tpp_australian_labor_party_votes']
    if libvote != 0 and labvote != 0:
        prop = libvote/(libvote+labvote)
    else:
        prop = 0
    q2result[r['sa2_code16']] = round(prop,2)


q = Query(db, selector={'doc_type': {'$eq': 'q3_data'}, 'sa2_code16' : {'$exists' : True}})


q3result = {x['sa2_code16']: x['trust_1_3_pc_synth'] for x in q.result if x['trust_1_3_pc_synth'] is not None} #trust

q = Query(db, selector={'doc_type': {'$eq': 'q4_data'}, 'sa2_code16' : {'$exists' : True}})
q4result = {str(x['sa2_code16']): x['total_migration_rate'] for x in q.result if x['total_migration_rate'] is not None} #trust


# load geojson file
with open("shpfiles/geojson/sa2_geojson.geojson") as json_file:
    data = json.load(json_file)
    f = data.pop("features")
    new_d = {"type": "FeatureCollection", "name": "sa2_geojson2",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4283"}}}

    new_f = []
    print("processing..")
    for x in f:
        y = x

        props = y.pop("properties")
        sa2code = props["SA2_MAIN16"]
        sa3code = props["SA3_CODE16"]

        if sa3code in q1result:
            props["gini_coefficient_no"] = q1result[sa3code]
        if sa2code in q2result:
            props["liberal_vote"] = q2result[sa2code]
        if sa2code in q3result:
            props["trust_1_3_pc_synth"] = q3result[sa2code]
        if sa2code in q4result:
            props["total_migration_rate"] = q4result[sa2code]

        y["properties"] = props
        new_f.append(y)

    new_d["features"] = new_f

    with open("shpfiles/geojson/aurin_json.geojson","w") as json_write:
        json.dump(new_d, json_write)
        print("done!")
