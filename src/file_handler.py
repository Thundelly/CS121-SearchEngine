import os
from bs4 import BeautifulSoup

try:
    import orjson as json
except ImportError:
    try:
        import ujson as json
    except ImportError:
        import json


class FileHandler:
    def __init__(self):
        pass

    def walk_files(self, folder, file_extension=None):
        """
        Walks through directories and files.
        Checks if files are json files. 
        Yields the path to a json file. 
        """
        for path, dirs, files in os.walk(folder, topdown=True):
            for filename in files:
                if file_extension != None:
                    if filename.endswith('.json'):
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

    def write_doc_id(self, doc_id_list):
        """
        Writes doc_id_list to doc_id.txt 
        """
        with open('doc_id.txt', 'a') as f:
            f.write(doc_id_list)

    # def write_to_file(self, index_list):
    #     for index in index_list:
    #         if index != '':
    #             char = index[0]
    #             if char.isnumeric():
    #                 with open('./db/num.txt', 'a') as file:
    #                     file.write(index)
    #             else:
    #                 with open('./db/{}.txt'.format(char), 'a') as file:
    #                     file.write(index)

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
        with open('doc_id.txt', 'r+') as file:
            file.truncate(0)


if __name__ == '__main__':
    file_handler = FileHandler()
    file_handler.clear_files()
