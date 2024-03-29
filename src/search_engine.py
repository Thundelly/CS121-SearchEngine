from datetime import datetime
from typing import Type

from indexer import Indexer
from file_handler import FileHandler
from query import Query

from nltk.corpus import stopwords


class SearchEngine:
    """
    If need to reindex, please change the 
    status to False in "index_status.log" file
    """

    def __init__(self):
        # Make an instance of file handler
        self.file_handler = FileHandler()
        # Make an instance of indexer
        self.indexer = Indexer(self.file_handler, file_count_offset=10000)

        # Check if the indexing is completed. If not, index the documents
        if not self.file_handler.get_index_status():
            self.index()

        # Open files 
        self.fp_dict = self.file_handler.load_json('./db/fp_locations.json')
        self.doc_id_dict = self.file_handler.load_json('./db/doc_id.json')
        self.final_index = open('./db/index.txt')

        cached_words = self.cache_stop_words()
        # Cached words are added to the query instance to check during query time
        self.query = Query(self.file_handler, self.indexer, cached_words)


    def cache_stop_words(self):
        cached_words = {}
        stop_words = set(stopwords.words('english'))

        # For every index, cache the stop words
        for line in self.final_index:
            index = Query.fast_eval(line)

            if index[0] in stop_words:
                cached_words[index[0]] = index[1]

        return cached_words


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
        process_time = end_time - start_time

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, process_time))

    def search(self):

        # Gets query from the user
        # Start time is calculated as soon as the query is received.
        start_time = self.query.get_query()
        # Process the query
        self.query.process_query()
        # Get result of the query
        result = self.query.get_result()

        end_time = datetime.now()
        process_time = end_time - start_time

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {} ms\n".format(
            start_time, end_time, process_time.total_seconds() * 1000))
    
    def run(self):
        while True:
            self.search()

if __name__ == '__main__':
    search_engine = SearchEngine()
    search_engine.run()