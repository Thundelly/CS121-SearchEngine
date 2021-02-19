import os
from bs4 import BeautifulSoup

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
            file_info = json.load(f)

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

    # def write_doc_id(self, doc_id_dict):
    #     """
    #     Writes doc_id_list to doc_id.txt 
    #     """
    #     with open('./db/doc_id.json', 'wb') as f:
    #         json.dump(doc_id_dict, f)

    def write_to_file(self, index_id, index_dict):
        with open(f'./db/pi{index_id}.txt', 'w') as file:
            for line in sorted(index_dict.items()):
                file.write(str(line) + '\n')

    def clear_files(self):
        # print("CLEARING INDEX FILES")
        for file in self.walk_files('db'):
            with open(file, 'r+') as file:
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

    def remove_partial_indexes(self):
        for file in self.walk_files('./db', '.txt'):
            if 'pi' in file:
                os.remove(file)

    def remove_tf_idf_indexes(self):
        for file in self.walk_files('./db', '.txt'):
            if 'tf_idf' in file:
                os.remove(file)

    def read_set(self, filename):
        """
        Read file line by line and return a set object 
        """
        with open(filename) as f:
            while True:
                line = f.readline().strip('\n')
                if line:
                    break
                yield eval(line)

    def count_number_of_line(self, filename):
        count = 0

        with open(filename, 'r') as file:
            for line in file:
                count += 1

        return count

    def merge_indexes(self, folder_path):
        files_to_be_merged = []

        # For every partial index files in the folder,
        # add to the list to be merged.
        for file in self.walk_files(folder_path, '.txt'):
            if 'pi' in file:
                files_to_be_merged.append(file)

        current_temp = 0

        # Create two temp files
        try:
            open('./db/temp0.txt', 'x')
            open('./db/temp1.txt', 'x')
        # If files already exist, clear the files
        except FileExistsError:
            self.clear_merge_temp_files()

        while files_to_be_merged:
            print(f"{len(files_to_be_merged)} more files to merge!")

            file = files_to_be_merged.pop()

            # input_temp and output_temp will alternate between temp0 and temp.
            if current_temp == 0:
                file = open(file, 'r')
                input_temp = open('./db/temp0.txt', 'r')
                output_temp = open('./db/temp1.txt', 'w')

            elif current_temp == 1:
                file = open(file, 'r')
                input_temp = open('./db/temp1.txt', 'r')
                output_temp = open('./db/temp0.txt', 'w')

            # Get each line
            line1 = file.readline().strip('\n')
            line2 = input_temp.readline().strip('\n')

            while True:

                # If the first file is empty, add the content of the
                # second file to the output_temp
                if line1 == '':
                    while True:
                        if line2 == '':
                            break
                        output_temp.write(line2 + '\n')
                        line2 = input_temp.readline().strip('\n')
                    break

                # If the second file is empty, add the content of the
                # first file to the output_temp
                if line2 == '':
                    while True:
                        if line1 == '':
                            break
                        output_temp.write(line1 + '\n')
                        line1 = file.readline().strip('\n')
                    break

                # If the files are not empty, get the first word
                # in each files to be merged
                word1 = eval(line1)[0]
                word2 = eval(line2)[0]

                # Check for lexicographical order and add
                # the words that comes first to the output_temp
                while word1 > word2:
                    output_temp.write(line2 + '\n')
                    line2 = input_temp.readline().strip('\n')
                    if line2 == '':
                        break
                    word2 = eval(line2)[0]

                while word2 > word1:
                    output_temp.write(line1 + '\n')
                    line1 = file.readline().strip('\n')
                    if line1 == '':
                        break
                    word1 = eval(line1)[0]

                # If the words are exactly the same, add the indexes of
                # both words and combine. Then add to the output_temp
                if word1 == word2:
                    output_temp.write(
                        str((word1, {**eval(line1)[1], **eval(line2)[1]})) + '\n')
                    line1 = file.readline().strip('\n')
                    line2 = input_temp.readline().strip('\n')

            file.close()
            input_temp.close()
            output_temp.close()

            # Alternate between the temp files
            if current_temp == 0:
                current_temp = 1
            else:
                current_temp = 0

        # Last merged file will be the final index
        # and remove the temp files
        self.remove_merge_temp_files(current_temp)
        self.remove_partial_indexes()
        print("Index merge complete.")

    def dump_json(self, dict, filename):
        """
        Dumps dictionary dict to a file
        """
        try:
            with open(filename, 'w') as f:
                json.dump(dict, f)

        except TypeError:
            json.dump(dict, filename)


    def load_json(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
