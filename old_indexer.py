from bs4 import BeautifulSoup
import json

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer

import os
import ssl
import math


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

    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in re_tokens if len(token) != 1]

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


def merge_indexes(file1, file2, outputfile):
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


# file is the index with the frequencies (probably the last merged.txt)
# outputfile is the file where you wanna write the new index to
# size is the size of the corpus (55393)
def calculate_tf_idf(file, outputfile, size):
    freq_index = open(file, 'r')
    tf_idf_index = open(outputfile, 'w')

    # this dict gets the square root of the sum of all squares of td-idf scores
    # in the doc. (we need this for normalizing)
    tf_idf_normalizers = dict()

    new_dict = dict()
    count = 1

    # loops through freq_index line by line
    while True:
        line = freq_index.readline().strip('\n')
        if line == '':
            break
        tup = eval(line)

        # doc_freq is the number of documents the token appears in (basically i
        # just took the length of the dict associated with the token
        doc_freq = len(tup[1])
        for doc_id, data in tup[1].items():
            # actually calculates the tf-idf bullshit
            tf_idf = data[0] * math.log((1 + size) / (1 + doc_freq)) + 1
            # stores the td_idf score to new_dict[doc_id]
            new_dict[doc_id] = (tf_idf, data[1])

            # adds the square of the tf_idf score to the normalizers
            if doc_id not in tf_idf_normalizers:
                tf_idf_normalizers[doc_id] = tf_idf * tf_idf
            else:
                tf_idf_normalizers[doc_id] += (tf_idf * tf_idf)

        # writes the new line (with new_dict containing the tf-idf scores) to
        # outputfile
        tf_idf_index.write(str((tup[0], new_dict)) + '\n')

        # clears new_dict for the next loop (next line)
        new_dict.clear()

        # just keeping track of how many lines we looped through (tbh u can
        # delete if u want)
        count += 1
        if count % 1000 == 0:
            print(f'{count} words calculated!')

    freq_index.close()
    tf_idf_index.close()

    # square roots all of the values of normalizers
    for doc_id in tf_idf_normalizers.keys():
        tf_idf_normalizers[doc_id] = math.sqrt(tf_idf_normalizers[doc_id])

    # returns the normalizers dict (we need this for the normalize function!)
    return tf_idf_normalizers


# normalizer is the dict returned from the calculate_tf_idf function
def normalize_tf_idf(file, outputfile, normalizer):
    tf_idf_index = open(file, 'r')
    final_index = open(outputfile, 'w')

    new_dict = dict()
    count = 1
    while True:
        line = tf_idf_index.readline().strip('\n')
        if line == '':
            break
        tup = eval(line)

        # basically the new tf_idf score is the old tf_idf score divided by
        # the square root of sum of squares of all tf_idf scores in the doc.
        # this ensures that the score is always between 0-1 i think
        for doc_id, data in tup[1].items():
            new_dict[doc_id] = (data[0] / normalizer[doc_id], data[1])

        final_index.write(str((tup[0], new_dict)) + '\n')
        new_dict.clear()

        # used to keep track of how many lines looped (tbh u can delete if u
        # want also)
        count += 1
        if count % 1000 == 0:
            print(f'{count} words normalized!')

    tf_idf_index.close()
    final_index.close()


def main():
    download_nltk_library()

    loop_corpus('DEV')

    merge_indexes('pi0.txt', 'pi1.txt', 'merged1.txt')
    print('1st merge done')
    merge_indexes('merged1.txt', 'pi2.txt', 'merged2.txt')
    print('2nd merge done')
    merge_indexes('merged2.txt', 'pi3.txt', 'merged3.txt')
    print('3rd merge done')
    merge_indexes('merged3.txt', 'pi4.txt', 'merged4.txt')
    print('4th merge done')
    merge_indexes('merged4.txt', 'pi5.txt', 'merged5.txt')
    print('5th merge done')


if __name__ == "__main__":
    d = calculate_tf_idf('merged5.txt', 'tf_idf.txt', 55393)
    normalize_tf_idf('tf_idf.txt', 'final_index.txt', d)