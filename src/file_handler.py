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
        pass

if __name__ == '__main__':

    file_handler = FileHandler()
    file_handler.write_to_file([])
