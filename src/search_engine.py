from file_handler import FileHandler
from indexer import Indexer
from datetime import datetime
import time


class SearchEngine:
    def __init__(self):
        self.indexer = Indexer('./DEV')
        pass

    def run(self):
        start_time = datetime.now()

        self.indexer.index(restart=True)

        end_time = datetime.now()

        print("Start Time: {}\nEnd Time: {}\nTime elapsed: {}".format(
            start_time, end_time, end_time-start_time))


if __name__ == '__main__':
    search_engine = SearchEngine()
    search_engine.run()
