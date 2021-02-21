import os
from indexer import Indexer
from datetime import datetime
from file_handler import FileHandler
from query import Query


class SearchEngine:
    """
    If need to reindex, please change the 
    status to False in "index_status.log" file
    """

    def __init__(self):
        self.file_handler = FileHandler()
        self.indexer = Indexer(self.file_handler, file_count_offset=10000)
        self.query = Query(self.file_handler, self.indexer)

        if not self.file_handler.get_index_status():
            self.index()

        self.fp_dict = self.file_handler.load_json('./db/fp_locations.json')
        self.doc_id_dict = self.file_handler.load_json('./db/doc_id.json')
        self.final_index = open('./db/index.txt')

    def index(self):
        start_time = datetime.now()

        # Index the webpages into partial indexes
        self.indexer.index('./DEV', restart=True)
        # Merge partial indexes to one single index
        self.indexer.merge_indexes('./db')
        # Calculate the tf_idf scores for each index
        normalizer = self.indexer.calculate_tf_idf(
            './db/index.txt', './db/index_tf_idf.txt', self.file_handler.count_number_of_line('./db/index.txt'))
        # Normalize the tf_idf scores
        self.indexer.normalize_tf_idf(
            './db/index_tf_idf.txt', './db/index.txt', normalizer)
        # Get file pointer locations for each index
        self.indexer.get_fp_locations(
            './db/index.txt', './db/fp_locations.json')

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time-start_time))

    def search(self):
        self.query.get_query()

        start_time = datetime.now()

        self.query.process_query()
        self.query.get_result()

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))

    def run(self):
        while True:
            self.search()


if __name__ == '__main__':
    search_engine = SearchEngine()
    search_engine.run()
