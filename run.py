import twitter_harvester
from couch_setup import CouchDBInstance
from multiprocessing import Process

def do_search(type):
    print("Starting search: ", type)
    twitter_harvester.start_search(type=type)

if __name__ == '__main__':
    # setup couch
    db = CouchDBInstance('http://127.0.0.1:5984')
    print("AURIN data loaded into Couchdb")

    # standard API in one process, stream API in another
    stream_proc = Process(target=do_search, args=("stream",))
    standard_proc = Process(target=do_search, args=("search",))

    #stream_proc.start()
    standard_proc.start()

    #stream_proc.join()
    standard_proc.join()
