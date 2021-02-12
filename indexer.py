

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

from bs4 import BeautifulSoup

import re
import ssl
import os
import json

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

def set_up_ssl():
    """
    Sets up connection for NLTK library download.
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context


def download_nltk_library():
    """
    Download NLTK libraray.
    Wordnet: Word map that checks for plural / root words
    Stopwords: Default conventional English stop words list
    """
    # Set path for nltk library.
    nltk.data.path.append('./nltk_data/')

    if not os.path.exists('./nltk_data/corpora'):
        # Set up ssl for nltk library download.
        set_up_ssl()
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

def parse_file(filename):
    with open(filename, 'r') as f:
        file_info = json.loads(f)
        content = file_info['content']
        soup = BeautifulSoup(content, 'lxml')

        text = ''
        weighted = ''

        text = soup.text

        for s in soup.find_all(['b', 'strong', 'h1', 'h2', 'h3', 'title']):
            weighted += s.getText().strip() + ' '

    return (tokenize(text), set(tokenize(weighted)))


def index(filename):
    count = 0
    with open(filename, 'w') as f: 
        for i in walk_files('DEV'):
            normalText, importantText = parse_file(i)
            count += 1
            for word in set(normalText): 
                f.write('{}, {}, {}, {}\n'.format(count, word, normalText.count(word), word in importantText))


def walk_files(folder):
    for path, dirs, files in os.walk(folder, topdown=True):
        for filename in files:
            if filename.endswith('.json'):
                yield path + '/' + filename
            

