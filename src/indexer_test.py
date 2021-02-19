from indexer import Indexer
from file_handler import FileHandler


file_handler = FileHandler()
indexer = Indexer(file_handler, 10000)

# indexer.merge_indexes('./db')
