import os
from indexer import Indexer
from datetime import datetime
from file_handler import FileHandler
import sys
import json


class SearchEngine:
    def __init__(self):
        self.file_handler = FileHandler()
        self.indexer = Indexer(self.file_handler, file_count_offset=10000)

        try:
            if not self.file_handler.get_index_status():
                self.index()
                self.merge()
        except:
            self.file_handler.set_index_status(False, datetime.now())
            self.index()
            self.merge()
            self.tf_idf()
            self.fp_locations()

    def index(self):
        start_time = datetime.now()
        self.indexer.index('./DEV', restart=True)
        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time-start_time))

    def merge(self):
        start_time = datetime.now()
        self.indexer.merge_indexes('./db')
        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time-start_time))

    def tf_idf(self):
        start_time = datetime.now()
        # NOTE: change the value once we filter urls
        d = self.indexer.calculate_tf_idf('./db/index.txt', './db/partial_tf_idf.txt', 55393)
        self.indexer.normalize_tf_idf('./db/partial_tf_idf.txt', './db/final_index.txt', d)
        end_time = datetime.now()
        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))

    def fp_locations(self):
        start_time = datetime.now()
        self.indexer.get_fp_locations('./db/final_index.txt', './db/fp_locations.txt')
        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

if __name__ == '__main__':
    search_engine = SearchEngine()

    """f = open('./db/fp_locations.txt', 'r')
    g = open('./db/final_index.txt')

    fp_locations = json.load(f)
    print(sys.getsizeof(fp_locations), 'bytes')

    start_time = datetime.now()
    location = fp_locations['master']
    g.seek(location)
    eval(g.readline().strip('\n'))

    location = fp_locations['of']
    g.seek(location)
    eval(g.readline().strip('\n'))

    location = fp_locations['softwar']
    g.seek(location)
    eval(g.readline().strip('\n'))

    location = fp_locations['engine']
    g.seek(location)
    eval(g.readline().strip('\n'))

    end_time = datetime.now()
    print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
        start_time, end_time, end_time - start_time))

    f.close()"""
