from indexer import Indexer
from file_handler import FileHandler


file_handler = FileHandler()
indexer = Indexer(file_handler, 10000)


def merge_posting(posting1, posting2):
    posting1 = eval(posting1)[1]
    posting2 = eval(posting2)[1]

    d = {k: v for k, v in sorted({** posting1, **posting2}.items())}
    return d


def peek_posting(iterable):
    try:
        next_iter = next(iterable)

    except StopIteration:
        return None

    return next_iter


def get_posting_intersection(posting1, posting2):
    posting1 = eval(posting1)
    posting2 = eval(posting2)
    posting1_iter = iter(posting1)
    posting2_iter = iter(posting2)
    intersection = dict()

    p1 = peek_posting(posting1_iter)
    p2 = peek_posting(posting2_iter)

    while p1 != None and p2 != None:
        if p1 == p2:
            score1 = posting1[p1]
            score2 = posting2[p2]
            intersection[p1] = (score1[0] + score2[0],
                                1 if score1[1] == 1 or score2[1] == 1 else 0)

            p1 = peek_posting(posting1_iter)
            p2 = peek_posting(posting2_iter)

        elif p1 > p2:
            p2 = peek_posting(posting2_iter)

        else:
            p1 = peek_posting(posting1_iter)

    print(intersection)


with open('./db_test/pi1.txt', 'r') as f:
    line1 = f.readline()
    line2 = f.readline()

    # merged = merge_posting(line1, line2)

    intersection = get_posting_intersection(line1, line2)


# print(merged)
