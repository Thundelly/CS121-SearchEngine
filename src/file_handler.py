import os
from bs4 import BeautifulSoup
from datetime import datetime

try:
    import orjson as json
except ImportError:
    try:
        import ujson as json
    except ImportError:
        import json


class FileHandler:
    def __init__(self):
        if not os.path.exists('./db'):
            os.mkdir('./db')

    def walk_files(self, folder, file_extension=None):
        """
        Walks through directories and files.
        Checks if files are json files. 
        Yields the path to a json file. 
        """
        for path, dirs, files in os.walk(folder, topdown=True):
            for filename in files:
                if file_extension != None:
                    if filename.endswith(file_extension):
                        yield path + '/' + filename
                else:
                    yield path + '/' + filename

    def parse_file(self, filename):
        """
        Truns json file into str text. 
        Returns both regular text and important text.
        """
        # opens json file and uses orjson to load the file
        with open(filename, 'r') as f:
            file_info = json.loads(f.read())

            # parses the content of the file useing BeautifulSoup
            # uses lxml for better perfomance
            content = file_info['content']
            soup = BeautifulSoup(content, 'lxml')

            text = soup.text

            # find all the important text from the specified tags
            weighted = []
            for s in soup.find_all(['b', 'strong', 'h1', 'h2', 'h3', 'title']):
                weighted.append(s.getText().strip() + ' ')

        return (file_info['url'], text, ''.join(weighted))

    def write_to_file(self, index_id, index_dict):
        with open(f'./db/pi{index_id}.txt', 'w') as file:
            for line in sorted(index_dict.items()):
                file.write(str(line) + '\n')

    def clear_files(self):
        # print("CLEARING INDEX FILES")
        for file in self.walk_files('db'):
            with open(file, 'r+') as file:
                file.truncate(0)

        # print("CLEARING DOC ID FILE")
        with open('./db/doc_id.txt', 'w+') as file:
            file.truncate(0)

    def set_index_status(self, completed, timestamp):

        with open('index_status.log', 'w+') as log:
            log.write(f'completed={completed}\nlast_run={timestamp}')

    def get_index_status(self):

        with open('index_status.log', 'r') as log:
            status = log.readline()[10:].strip('\n')

            if status == 'True':
                return True
            elif status == 'False':
                return False

    def remove_merge_temp_files(self, current_temp):
        if current_temp == 0:
            os.remove('./db/temp1.txt')
            os.rename('./db/temp0.txt', './db/index.txt')
        else:
            os.remove('./db/temp0.txt')
            os.rename('./db/temp1.txt', './db/result.txt')

    def clear_merge_temp_files(self):
        with open('./db/temp0.txt', 'r+') as temp0, open('./db/temp1.txt', 'r+') as temp1:
            temp0.truncate(0)
            temp1.truncate(0)

    def json_dump(self, d, filename):
        """
        Dumps dict d to a file
        """
        json.dump(d, filename)

    def json_load(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)


if __name__ == '__main__':
    file_handler = FileHandler()
    file_handler.clear_files()
