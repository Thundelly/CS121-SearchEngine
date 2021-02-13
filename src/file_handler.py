import os
import orjson as json
from bs4 import BeautifulSoup


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
            weighted = ''
            for s in soup.find_all(['b', 'strong', 'h1', 'h2', 'h3', 'title']):
                weighted += s.getText().strip() + ' '

        return (text, weighted)

    def write_to_file(self, index_list):
        for index in index_list:
            if index != '':
                char = index[0]
                if char.isnumeric():
                    with open('./db/num.txt', 'a') as file:
                        file.write(index)
                else:
                    with open('./db/{}.txt'.format(char), 'a') as file:
                        file.write(index)

    def clear_files(self):
        print("CLEARING FILES")
        for file in self.walk_files('db'):
            with open(file, 'r+') as file:
                file.truncate(0)


if __name__ == '__main__':

    file_handler = FileHandler()
