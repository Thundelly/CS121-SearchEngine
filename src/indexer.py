import ssl
import os
from pprint import pprint
from datetime import datetime

import nltk
from nltk.corpus.reader import wordlist
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer


class Indexer:
    def __init__(self, folder_name, file_handler, file_count_offset):
        # Download the nltk library before indexing.
        self.download_nltk_library()
        self.doc_id_list = []
        self.doc_id = 1
        self.folder_name = folder_name
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

    def index(self, restart=False):
        # reset the files
        if restart:
            self.file_handler.clear_files()

        # Update current status
        last_ran_timestamp = datetime.now()
        self.file_handler.set_index_status(False, last_ran_timestamp)

        index_id = 0
        index_dict = dict()

        for file in self.file_handler.walk_files(self.folder_name, '.json'):
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

    def merge_indexes(self, file1, file2, outputfile):
        index1 = open(file1, 'r')
        index2 = open(file2, 'r')
        output = open(outputfile, 'w')

        line1 = index1.readline().strip('\n')
        line2 = index2.readline().strip('\n')

        while True:
            # If end of file 1 is reached, read the rest from file 2 and then break
            if line1 == '':
                while True:
                    if line2 == '':
                        break
                    output.write(line2 + '\n')
                    line2 = index2.readline().strip('\n')
                break

            # If end of file 2 is reached, read the rest from file 1 and then break
            if line2 == '':
                while True:
                    if line1 == '':
                        break
                    output.write(line1 + '\n')
                    line1 = index1.readline().strip('\n')
                break

            # get the two tuples from the two lines
            tup1 = eval(line1)
            tup2 = eval(line2)

            # keep writing the first index's contents while the first line's token
            # is smaller than the second line's
            while tup1[0] < tup2[0]:
                output.write(line1 + '\n')
                line1 = index1.readline().strip('\n')
                if line1 == '':
                    break
                tup1 = eval(line1)

            # keep writing the second index's contents while the second line's
            # token is smaller than the first line's
            while tup1[0] > tup2[0]:
                output.write(line2 + '\n')
                line2 = index2.readline().strip('\n')
                if line2 == '':
                    break
                tup2 = eval(line2)

            # at the end of these two loops, the first token should either be
            # smaller than or equal to the second token (or either of the two have
            # ended)

            # if the tokens are equal, merge the contents
            if tup1[0] == tup2[0]:
                new_contents = {**tup1[1], **tup2[1]}
                output.write(str((tup1[0], new_contents)) + '\n')
                line1 = index1.readline().strip('\n')
                line2 = index2.readline().strip('\n')

        index1.close()
        index2.close()
        output.close()

if __name__ == '__main__':
    indexer = Indexer('DEV')
    # indexer.index()
    indexer.index(restart=True)
