from src.file_handler import FileHandler
from src.indexer import Indexer


class SearchEngine:
    def __init__(self):
        self.file_handler = FileHandler()
        self.indexer = Indexer()

if __name__ == '__main__':
    search_engine = SearchEngine()
