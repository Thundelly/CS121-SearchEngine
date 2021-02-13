import ssl
import os
from pprint import pprint

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

from file_handler import FileHandler

class Indexer:
    def __init__(self, folder_name):
        # Download the nltk library before indexing.
        self.download_nltk_library()
        self.index_list = []
        self.doc_id_list = []
        self.folder_name = folder_name
        self.file_handler = FileHandler()
        self.populate_index_list()
        self.doc_id = 0

    def populate_index_list(self):
        for i in range(0, 27):
            self.index_list.append([])

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

        # Lemmatizer. Checks for word roots words.
        # Includes root words of verbes, and plural forms.
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(w, pos="v") for w in re_tokens]
        # Check for tokens that are single characters and exclude them
        tokens = [token for token in tokens if len(token) != 1]

        return tokens

    def add_doc_id(self, url): 
        """
        Appends a new url to the doc_id_list and increments the doc_id
        If the list len is larger than ...., then call write_doc_id function
        """
        self.doc_id_list.append('{}, {}\n'.format(self.doc_id, url))
        self.doc_id += 1

        if len(self.doc_id_list) > 0:
            self.file_handler.write_doc_id(self.doc_id_list)
            self.doc_id_list.clear()

    def index(self):
        index_count = 0

        for file in self.file_handler.walk_files(self.folder_name):
            url_name, normalText, importantText = self.file_handler.parse_file(file)
            
            self.add_doc_id(url_name)
            normalText = self.tokenize(normalText)
            importantText = set(self.tokenize(importantText))

            for word in set(normalText):
                # print(word)

                if word[0].isnumeric():
                    # print('\t\tNUMBER')
                    self.index_list[26].append('{}, {}, {}, {}\n'.format(
                        word, self.doc_id, normalText.count(word), word in importantText))
                    index_count += 1
                else:
                    # print('\t\tCHAR')
                    index = ord(word[0]) - 97
                    self.index_list[index].append('{}, {}, {}, {}\n'.format(
                        word, self.doc_id, normalText.count(word), word in importantText))
                    index_count += 1
                
                if index_count == 20:
                    index_count = 0

            break   # break the loop just for one file

        pprint(self.index_list)

if __name__ == '__main__':
    indexer = Indexer('DEV')
    print(indexer.index())


# parsing
# posting
# sorting
# retreving
# dictionary

''' 
index 
-> read json file
-> parsing 
-> build index
-> write to a file 
-> get files in every directory 

Total json files : 55393
'''
