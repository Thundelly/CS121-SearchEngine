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

        weighted = []
        text = soup.text

        for tag in ['b', 'strong', 'h1', 'h2', 'h3', 'title']:
            for s in soup.find_all(tag):
                weighted.append(s.getText().strip() + ' ')

        return file_info['url'], tokenize(text), tokenize(''.join(weighted))


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


def compute_word_frequencies(token_list: [str]) -> {str: int}:
    frequencies = dict()
    # Looping through each token in tokenList: O(n)
    for token in token_list:
        # Adding/setting key and values in a dict: O(1)
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1
    return frequencies


def loop_corpus(folder):
    count = 1
    partial_index_id = 0
    index = dict()
    file_numbers = dict()

    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith('.json'):
                data = parse_file(os.path.join(root, filename))
                # adds {number (document id): url} to file_numbers
                file_numbers[count] = data[0]
                frequencies = compute_word_frequencies(data[1])
                for word, frequency in frequencies.items():
                    if word not in index:
                        index[word] = dict()
                    # the key is the document id and its element is the tuple
                    # first value of the tuple is the frequency of the word
                    # if the word is in the important list, set the second
                    # value of the tuple to 1, else 0
                    if word in data[2]:
                        index[word][count] = (frequency, 1)
                    else:
                        index[word][count] = (frequency, 0)
                count += 1

            if count % 100 == 0:
                print(f'Looped through {count} pages!')
            # offloading every 10k pages
            if count % 10000 == 0:
                print(f'Looped through {count} pages. Offloading to pi{partial_index_id}.')
                with open(f'pi{partial_index_id}.txt', 'w') as f:
                    for line in sorted(index.items()):
                        f.write(str(line) + '\n')
                index.clear()
                partial_index_id += 1
                print('Done with offloading, continuing.')

    # final offload
    print(f'Looped through every page. Offloading to pi{partial_index_id}.')
    with open(f'pi{partial_index_id}.txt', 'w') as f:
        for line in sorted(index.items()):
            f.write(str(line) + '\n')
    index.clear()



def main():
    download_nltk_library()

    loop_corpus('DEV')


if __name__ == "__main__":
    main()
