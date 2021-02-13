import os
from file_handler import FileHandler

HEADER = 'Natcha Jengjirapas: 85939811, Eric Ko: 88335453, Ali Cassim Malam: 26643054, Timothy Soo Sin: 44999512'

class Report:
    def __init__(self, doc_id, db_folder):
        self.doc_id = doc_id
        self.db_folder = db_folder
        self.unique_token = 0
        self.file_size = 0
        self.token_set = set()
        self.file_handler = FileHandler()

    def make_report_m1(self):
        with open('reportM1.txt', 'w') as f:
            f.write('{}\n\nNumber of indexed documents: {}\n'\
            'Number of unique words: {}\n'\
            'Size of index: {} kb'.format(
                HEADER, self.doc_id, self.unique_token, self.file_size/1000))

    def get_unique_tokens(self):
        for i in self.file_handler.walk_files(self.db_folder):
            self.file_size += os.path.getsize(i)
            with open(i, 'r') as f:
                for word in f:
                    self.token_set.add(word.split(',')[0])
            self.unique_token += len(self.token_set)
            self.token_set.clear()

        print(self.unique_token)
        print(self.file_size/1000)


if __name__ == '__main__':
    report = Report(1,'db')
    report.get_unique_tokens()
    report.make_report_m1()