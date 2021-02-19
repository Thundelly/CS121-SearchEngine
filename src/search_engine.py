import os
from indexer import Indexer
from datetime import datetime
from file_handler import FileHandler


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

        self.fp_dict = self.file_handler.json_load('./db/fp_locations.json')
        self.final_index = open('./db/final_index.txt')
        self.doc_id = self.file_handler.json_load('./db/doc_id.json')

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
        size = len(self.file_handler.json_load('./db/doc_id.json'))
        d = self.indexer.calculate_tf_idf('./db/index.txt', './db/partial_tf_idf.txt', size)
        self.indexer.normalize_tf_idf('./db/partial_tf_idf.txt', './db/final_index.txt', d)
        end_time = datetime.now()
        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))

    def fp_locations(self):
        start_time = datetime.now()
        self.indexer.get_fp_locations('./db/final_index.txt', './db/fp_locations.json')
        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))

    def search(self, s):
        # s: string input from search
        start_time = datetime.now()

        tokens = self.indexer.tokenize(s)
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
                    print(self.doc_id[str(sorted_tup[i][0])])
                except IndexError:
                    break
        else:
            print('No results found')

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time - start_time))


if __name__ == '__main__':
    search_engine = SearchEngine()
    while True:
        s = input("What is your query?: ")
        search_engine.search(s)

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
