from indexer import Indexer
from indexer_debug import IndexerDebug
from datetime import datetime
from file_handler import FileHandler

class SearchEngine:
    def __init__(self):
        self.file_handler = FileHandler()

        self.indexer = Indexer('./DEV', self.file_handler, file_count_offset=5000)
        self.indexer_debug = IndexerDebug('./DEV', self.file_handler, file_count_offset=5000)

    def run(self):
        start_time = datetime.now()
        self.indexer.index(restart=True)
        end_time = datetime.now()

        print("\nStart Time 1: {}\nEnd Time 1: {}\nTime elapsed 1: {}\n".format(
            start_time, end_time, end_time-start_time))

    def run2(self):
        start_time = datetime.now()
        self.indexer_debug.index(restart=True)
        end_time = datetime.now()

        print("\nStart Time 2: {}\nEnd Time 2: {}\nTime elapsed 2: {}\n".format(
            start_time, end_time, end_time-start_time))

if __name__ == '__main__':
    search_engine = SearchEngine()
    # search_engine.run()
    search_engine.run2()
