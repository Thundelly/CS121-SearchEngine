import os
from indexer import Indexer
from datetime import datetime
from file_handler import FileHandler


class SearchEngine:
    def __init__(self):
        self.file_handler = FileHandler()
        self.indexer = Indexer('./DEV', self.file_handler, file_count_offset=10000)

        try:
            if not self.file_handler.get_index_status():
                self.index()
                self.merge()
        except:
            self.file_handler.set_index_status(False, datetime.now())
            self.index()
            self.merge()

    def index(self):
        start_time = datetime.now()
        self.indexer.index(restart=True)
        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
            start_time, end_time, end_time-start_time))


    def merge(self):
        
        start_time = datetime.now()

        self.indexer.merge_indexes('./db/pi0.txt', './db/pi1.txt', './db/merged1.txt')
        print('1st merge done')
        self.indexer.merge_indexes('./db/merged1.txt', './db/pi2.txt', './db/merged2.txt')
        print('2nd merge done')
        self.indexer.merge_indexes('./db/merged2.txt', './db/pi3.txt', './db/merged3.txt')
        print('3rd merge done')
        self.indexer.merge_indexes('./db/merged3.txt', './db/pi4.txt', './db/merged4.txt')
        print('4th merge done')
        self.indexer.merge_indexes('./db/merged4.txt', './db/pi5.txt', './db/merged5.txt')
        print('5th merge done')

        end_time = datetime.now()

        print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(start_time, end_time, end_time-start_time))


if __name__ == '__main__':
    search_engine = SearchEngine()
    # search_engine.run()
    search_engine.indexer.merge_indexes('./test/test1.txt', './test/test2.txt', './result1.txt')
