from indexer import Indexer
from file_handler import FileHandler


file_handler = FileHandler()
indexer = Indexer(file_handler, 10000)

def merge_posting(line1, line2):
    d = {k : v for k, v in sorted({** line1, **line2}.items())}
    return d


with open('./db_test/pi0.txt', 'r') as f:
    line1 = eval(f.readline())[1]
    line2 = eval(f.readline())[1]

    merged = merge_posting(line1, line2)

print(merged)