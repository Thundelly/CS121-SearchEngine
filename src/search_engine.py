import os
from indexer import Indexer
from datetime import datetime
from file_handler import FileHandler


class SearchEngine:
    def __init__(self):
        self.file_handler = FileHandler()
        self.indexer = Indexer(self.file_handler, file_count_offset=10000)

        print("INDEX:", self.file_handler.get_index_status())

        if not self.file_handler.get_index_status():
            self.index()
            self.merge()

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


if __name__ == '__main__':
    search_engine = SearchEngine()
    # search_engine.merge()
