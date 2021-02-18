import os
from indexer import Indexer
from datetime import datetime
from file_handler import FileHandler


class SearchEngine:
    def __init__(self):
        self.file_handler = FileHandler()
        self.indexer = Indexer(self.file_handler, file_count_offset=10000)

        if not self.file_handler.get_index_status():
            self.index()

    def index(self):
        start_time = datetime.now()

        self.indexer.index('./DEV', restart=True)
        self.file_handler.merge_indexes()
        normalizer = self.indexer.calculate_tf_idf(
            './db/index.txt', './db/index_tf_idf.txt', self.file_handler.count_number_of_line('./db/index.txt'))
        self.indexer.normalize_tf_idf('./db/index_tf_idf.txt', './db/index.txt', normalizer)

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time-start_time))


if __name__ == '__main__':
    search_engine = SearchEngine()

