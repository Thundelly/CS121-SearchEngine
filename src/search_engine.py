from file_handler import FileHandler
from indexer import Indexer


class SearchEngine:
    def __init__(self):
        self.indexer = Indexer('./DEV')
        pass

    def run(self):
        self.indexer.index(restart=True)

if __name__ == '__main__':
    search_engine = SearchEngine()
    search_engine.run()
