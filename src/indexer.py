from bs4 import BeautifulSoup

import ssl
import os
import json

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

from src.file_handler import FileHandler


class Indexer:
    def __init__(self):
        # Download the nltk library before indexing.
        self.download_nltk_library()
        self.index_list = []
        self.doc_id_list = []

        self.file_handler = FileHandler()

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

    def tokenize(text):
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

    def parse_file(self, filename):
        with open(filename, 'r') as f:
            file_info = json.loads(f.read())
            content = file_info['content']
            soup = BeautifulSoup(content, 'lxml')

            text = ''
            weighted = ''

            text = soup.text

            for s in soup.find_all(['b', 'strong', 'h1', 'h2', 'h3', 'title']):
                weighted += s.getText().strip() + ' '

        return (self.tokenize(text), self.tokenize(weighted))

    def index(self, filename):
        doc_id = 0

        for file in self.file_handler.walk_files():
            normalText, importantText = self.parse_file(file)
            
            for word in set(normalText):
                self.index_list.append('{}, {}, {}, {}\n'.format(word, doc_id, normalText.count(word), word in importantText))




        with open(filename, 'w') as f:
            for i in self.walk_files():
                normalText, importantText = self.parse_file(i)
                count += 1
                for word in set(normalText):
                    f.write('{}, {}, {}, {}\n'.format(count, word,
                                                      normalText.count(word), word in importantText))




if __name__ == '__main__':
    indexer = Indexer()
    print(indexer.index("word.txt"))


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
