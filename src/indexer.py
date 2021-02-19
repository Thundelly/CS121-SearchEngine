import ssl
import os
import math
from pprint import pprint
from datetime import datetime
from file_handler import FileHandler

import nltk
from nltk.corpus.reader import wordlist
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer


class Indexer:
    def __init__(self, folder_name, file_handler, file_count_offset):
        # Download the nltk library before indexing.
        self.download_nltk_library()
        self.doc_id_dict = dict()
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
        self.doc_id_dict[str(self.doc_id)] = url 
        self.doc_id += 1

        # if len(self.doc_id_dict) > self.file_count_offset:
        #     self.file_handler.write_doc_id(self.doc_id_dict)
        #     self.doc_id_dict.clear()

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
        self.file_handler.write_doc_id(self.doc_id_dict)
        self.doc_id_dict.clear()
        

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

    def calculate_tf_idf(self, file, outputfile, size):
        """
        Calculates tf_idf score by multiplying the term frequency (tf)
        and inverse document frequency (idf). Stores the result 
        in the outputfile.

        idf score has the following formula:
        log(1 + n / (1 + d(t))) + 1

        Input Parameter: 
        file -> the inverted index file
        outputfile -> the file to store the tf_idf values
        size -> the number of files in corpus

        Return Value: 
        A normalized dictionary contains doc_id and 
        its lenght (square root of all td-idf^2 scores)
        """
        
        inverted_index = open(file, 'r')
        tf_idf_index = open(outputfile, 'w')
        
        tf_idf_normalizers = dict()
        temp_dict = dict()
        count = 1

        for line in inverted_index:
            # gets the tuple item from inverted index file 
            tup = eval(line.strip('\n'))
            
            # gets the number of documents in the corpus that contain the word
            # uses it to calculate idf value 
            doc_freq = len(tup[1])
            idf_value = math.log((size + 1) / (doc_freq + 1)) + 1
    
            # stores the tf_idf value into the temp dictionary 
            # and add (tf_idf)^2 to the tf_idf_normalizers 
            for doc_id, tf_value in tup[1].items():
                tf_idf = tf_value[0] * idf_value
                temp_dict[doc_id] = (tf_idf, tf_value[1])

                if doc_id not in tf_idf_normalizers:
                    tf_idf_normalizers[doc_id] = tf_idf * tf_idf
                else:
                    tf_idf_normalizers[doc_id] += (tf_idf * tf_idf)

            # writes the tf_idf value to the output file and
            # clears temp_dict for the next loop (next line)
            tf_idf_index.write(str((tup[0], temp_dict)) + '\n')
            temp_dict.clear()

            # keeptracks of the current status while running this function
            count += 1
            if count % 1000 == 0:
                print(f'{count} words calculated!')

        inverted_index.close()
        tf_idf_index.close()

        # square roots all of the values of normalizers
        for doc_id in tf_idf_normalizers.keys():
            tf_idf_normalizers[doc_id] = math.sqrt(tf_idf_normalizers[doc_id])

        # returns the normalizers dict (we need this for the normalize function!)
        return tf_idf_normalizers
    
    def normalize_tf_idf(self, file, outputfile, normalizer):
        """
        Normalizes tf_idf value by dividing the old tf_idf value with its lenght 
        (square root of all td-idf^2 scores) from calculate_tf_idf function.

        Input Parameter:
        file -> the outputfile from the calculate_tf_idf function 
        outputfile -> the file to store the result of the normalized tf_idf value  
        normalizer -> the returned dictionary from the calculate_if_idf function 

        Return Value: 
        None
        """
        tf_idf_index = open(file, 'r')
        final_index = open(outputfile, 'w')

        temp_dict = dict()
        count = 1

        for line in tf_idf_index:
            tup = eval(line.strip('\n'))

            # normalizes the tf_idf value and stores it inside the temp dictionary
            for doc_id, data in tup[1].items():
                temp_dict[doc_id] = (data[0] / normalizer[doc_id], data[1])

            # writes the normalized tf_idf value to the output file and
            # clears temp_dict for the next loop (next line)
            final_index.write(str((tup[0], temp_dict)) + '\n')
            temp_dict.clear()

            # keeptracks of the current status while running this function
            count += 1
            if count % 1000 == 0:
                print(f'{count} words normalized!')

        tf_idf_index.close()
        final_index.close()

        # def get_word(self, )

if __name__ == '__main__':
    indexer = Indexer('DEV', FileHandler(), file_count_offset=10)
    # indexer.index()
    indexer.index(restart=True)
    # d = indexer.calculate_tf_idf('test.txt', 'output.txt', 12)
    # indexer.normalize_tf_idf('output.txt', 'final.txt', d)
    print(d)
