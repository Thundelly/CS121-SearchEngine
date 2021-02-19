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
        self.indexer.normalize_tf_idf('./db/index_tf_idf.txt', './db/index.txt', normalizer)
        # Get file pointer locations for each index
        self.indexer.get_fp_locations('./db/index.txt', './db/fp_locations.json')

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time-start_time))

    def search(self, query):
        # query: string input from search
        start_time = datetime.now()

        tokens = self.indexer.tokenize(query)
        scores = dict()
        for token in tokens:
            try:
                fp = self.fp_dict[token]
                self.final_index.seek(fp)
                tup = eval(self.final_index.readline().strip('\n'))
                for doc_id, score_tup in tup[1].items():
                    if doc_id not in scores:
                        scores[doc_id] = score_tup[0]
                    else:
                        scores[doc_id] += score_tup[0]
            except KeyError:
                print(f'No token {token} found.')

        if scores:
            sorted_tup = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            for i in range(5):
                try:
                    found_doc_id = sorted_tup[i][0]
                    print(self.doc_id_dict[str(found_doc_id)])   # print the url of the found doc id
                except IndexError:
                    break
        else:
            print('No results found')

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))

    def run(self):
        while True:
            s = input("What is your query?: ")
    
            if s == ':q':
                break

            self.search(s)


if __name__ == '__main__':
    search_engine = SearchEngine()
    search_engine.run()

