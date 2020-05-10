import twitter_harvester
import sys
from couch_setup import CouchDBInstance
from multiprocessing import Process

'''
    Main entry point to setup couchdb, and start harvesting tweets
    Configurations –– harvest with stream API, standard API, or both!

    Ex: python run.py stream
        python run.py search
        python run.py both
'''

def do_search(type):
    print("Starting search: ", type)
    twitter_harvester.start_search(type=type)

def start_processes(type):
    procs = []
    if type == "both":
        procs.append(Process(target=do_search, args=("stream",)))
        procs.append(Process(target=do_search, args=("search",)))
    elif type == "search":
        procs.append(Process(target=do_search, args=("search",)))
    elif type == "stream":
        procs.append(Process(target=do_search, args=("stream",)))
    else:
        print("USAGE: python run.py <stream/search/both>")

    for p in procs:
        p.start()

    for p in procs:
        p.join()

if __name__ == '__main__':
    if len(sys.argv) == 0:
        print("USAGE: python run.py <stream/search/both>")
        sys.exit(1)

    db = CouchDBInstance('http://127.0.0.1:5984')
    print("AURIN data loaded into Couchdb")

    type = sys.argv[1]
    start_processes(type)
