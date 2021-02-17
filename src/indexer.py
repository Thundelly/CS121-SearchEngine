import ssl
import os
from pprint import pprint
from datetime import datetime

import nltk
from nltk.corpus.reader import wordlist
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer


class Indexer:
    def __init__(self, file_handler, file_count_offset):
        # Download the nltk library before indexing.
        self.download_nltk_library()
        self.doc_id_list = []
        self.doc_id = 1
        self.file_handler = file_handler

        self.file_count_offset = file_count_offset

    def populate_index_list(self, index_list):
        for i in range(0, 27):
            index_list.append([])

    def set_up_ssl(self):
        """
        Sets up connection for NLTK library download.
        """
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

    def download_nltk_library(self):
        """
        Download NLTK libraray.
        Wordnet: Word map that checks for plural / root words
        Stopwords: Default conventional English stop words list
        """
        # Set path for nltk library.
        nltk.data.path.append('./nltk_data/')

        if not os.path.exists('./nltk_data/corpora'):
            # Set up ssl for nltk library download.
            self.set_up_ssl()
            # Download wordnet from nltk library.
            nltk.download('wordnet', download_dir='./nltk_data/')
            # Download stopwords from nltk library.
            nltk.download('stopwords', download_dir='./nltk_data/')

    def tokenize(self, text):
        """
        Takes a string of text and tokenize it using NLTK library.
        """
        # Regex tokenizer. Checks for alphanumeric characters.
        re_tokenizer = RegexpTokenizer('[a-zA-Z0-9]+')
        re_tokens = re_tokenizer.tokenize(text.lower())

        stemmer = SnowballStemmer(language='english')
        tokens = [stemmer.stem(token)
                  for token in re_tokens if len(token) != 1]

        return tokens

    def add_doc_id(self, url):
        """
        Appends a new url to the doc_id_list and increments the doc_id
        If the list len is larger than ...., then call write_doc_id function
        """
        self.doc_id_list.append(f'{self.doc_id}, {url}\n')
        self.doc_id += 1

        if len(self.doc_id_list) > self.file_count_offset:
            self.dump_doc_id(self.doc_id_list)
            self.doc_id_list.clear()

    def compute_word_frequencies(self, token_list):
        frequencies = dict()
        # Looping through each token in tokenList: O(n)
        for token in token_list:
            # Adding/setting key and values in a dict: O(1)
            if token in frequencies:
                frequencies[token] += 1
            else:
                frequencies[token] = 1

        return frequencies

    def index(self, folder_name, restart=False):
        # reset the files
        if restart:
            self.file_handler.clear_files()

        # Update current status
        last_ran_timestamp = datetime.now()
        self.file_handler.set_index_status(False, last_ran_timestamp)

        index_id = 0
        index_dict = dict()

        for file in self.file_handler.walk_files(folder_name, '.json'):
            url, normalText, importantText = self.file_handler.parse_file(file)

            normalText = self.tokenize(normalText)
            importantText = set(self.tokenize(importantText))

            # Find frequencies of each word
            frequencies = self.compute_word_frequencies(normalText)

            for word, frequency in frequencies.items():
                if word not in index_dict:
                    index_dict[word] = dict()

                if word in importantText:
                    index_dict[word][self.doc_id] = (frequency, 1)
                else:
                    index_dict[word][self.doc_id] = (frequency, 0)

            # Keep record of doc id and url
            self.add_doc_id(url)

            if self.doc_id % 100 == 0:
                print(f'Looped through {self.doc_id} pages!')

            # Offload every 10,000 pages
            if self.doc_id % self.file_count_offset == 0:
                print(
                    f'Looped through {self.doc_id} pages. Offloading to pi{index_id}')
                self.file_handler.write_to_file(index_id, index_dict)
                index_dict.clear()
                index_id += 1
                print('Done with offloading, continuing.')

        # Final offload
        print(f'Looped through every page. Offloading to pi{index_id}')
        self.file_handler.write_to_file(index_id, index_dict)
        index_dict.clear()

        # Set index status to True
        self.file_handler.set_index_status(True, last_ran_timestamp)

        # dumping doc id list
        self.dump_doc_id(self.doc_id_list)
        self.doc_id_list.clear()

    def dump_doc_id(self, doc_id_list):
        temp_doc_id = ''.join(doc_id_list)
        self.file_handler.write_doc_id(temp_doc_id)

    def merge_indexes(self, folder_path):
        files_to_be_merged = []

        # For every partial index files in the folder,
        # add to the list to be merged.
        for file in self.file_handler.walk_files(folder_path, '.txt'):
            if 'pi' in file:
                files_to_be_merged.append(file)

        current_temp = 0
        
        # Create two temp files
        try:
            open('./db/temp0.txt', 'x')
            open('./db/temp1.txt', 'x')
        # If files already exist, clear the files
        except FileExistsError:
            self.file_handler.clear_merge_temp_files()

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
        self.file_handler.remove_merge_temp_files(current_temp)
        print("Index merge complete.")
