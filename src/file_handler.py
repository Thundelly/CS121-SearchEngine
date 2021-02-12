import os


class FileHandler:
    def __init__(self):
        pass

    def walk_files(self, folder):
        for path, dirs, files in os.walk(folder, topdown=True):
            for filename in files:
                if filename.endswith('.json'):
                    yield path + '/' + filename

    def write_to_file(self, index_list):
        for index in index_list:
            word = index.split(',', 1)[0]