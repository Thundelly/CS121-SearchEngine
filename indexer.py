from bs4 import BeautifulSoup
import json

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

import os
import ssl


ALPHANUMERIC = 'abcdefghijklmnopqrstuvwxyz0123456789'



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


def parse_file(filename):
    with open(filename, 'r') as f:
        file_info = json.loads(f.read())
        content = file_info['content']
        soup = BeautifulSoup(content, 'html.parser')

        text = ''
        weighted = ''

        text = soup.text

        for tag in ['b', 'strong', 'h1', 'h2', 'h3', 'title']:
            for s in soup.find_all(tag):
                weighted += s.getText().strip() + ' '

        return (tokenize(text), tokenize(weighted))


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
    tokens = [lemmatizer.lemmatize(w) for w in re_tokens]

    return tokens


def main():
    download_nltk_library()
    print(parse_file('DEV/archive_ics_uci_edu/00db3b44bb015e65e2675829c71f4269b5d9fbaf282e89fb931f492b35dca268.json'))

    count = 0
    download_nltk_library()

    folder = 'DEV'
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith('.json'):
                parse_file(os.path.join(root, filename))
    print(count)



if __name__ == "__main__":
    main()
