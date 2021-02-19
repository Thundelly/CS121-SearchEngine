import mmap
from datetime import datetime


start_time = datetime.now()

with open('./db/index.txt', 'r+b') as index:
    mm = mmap.mmap(index.fileno(), 0)

    query = bytes('hello', 'utf-8')

    while True:
        line = mm.readline()

        if line == b'':
            break

end_time = datetime.now()

print("\nStart Time : {}\nEnd Time : {}\nTime elapsed : {}\n".format(
    start_time, end_time, end_time-start_time))
