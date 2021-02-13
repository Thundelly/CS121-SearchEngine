import os
import orjson as json
from bs4 import BeautifulSoup

class FileHandler:
    def __init__(self):
        pass                

    def walk_files(self, folder):
        """
        Walks through directories and files.
        Checks if files are json files. 
        Yields the path to a json file. 
        """
        for path, dirs, files in os.walk(folder, topdown=True):
            for filename in files:
                if filename.endswith('.json'):
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
        pass


if __name__ == '__main__':

    file_handler = FileHandler()
