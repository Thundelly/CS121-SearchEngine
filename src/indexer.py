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

from urllib.parse import urldefrag

class Indexer:
    def __init__(self, file_handler, file_count_offset):
        # Downloads the nltk library before indexing.
        self.download_nltk_library()
        # This is a dict where the key is the doc id and its value is the URL
        self.doc_id_dict = dict()
        # The doc id is defaulted to 1
        self.doc_id = 1
        # The file handler is an object from file_handler.py that handles all
        # the files.
        self.file_handler = file_handler

        # file_count_offset is the number of documents to parse before
        # offloading to a partial index. This number should be defaulted to
        # 10,000 in search_engine.py
        self.file_count_offset = file_count_offset

    def set_up_ssl(self) -> None:
        """
        Sets up connection for NLTK library download.
        """
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

    def download_nltk_library(self) -> None:
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

    def tokenize(self, text: str) -> [str]:
        """
        Takes a string of text and tokenizes it using NLTK library.
        """
        # Regex tokenizer. Checks for alphanumeric characters.
        re_tokenizer = RegexpTokenizer('[a-zA-Z0-9]+')
        re_tokens = re_tokenizer.tokenize(text.lower())

        # returns a stemmed list of tokens
        stemmer = SnowballStemmer(language='english')
        tokens = [stemmer.stem(token) for token in re_tokens]
        return tokens

    def add_doc_id(self, url: str):
        """
        Appends a new url to the doc_id_list and increments the doc_id
        If the list len is larger than ...., then call write_doc_id function
        """
        self.doc_id_dict[str(self.doc_id)] = url 
        self.doc_id += 1

    def compute_word_frequencies(self, token_list: [str]) -> {str: int}:
        """
        Takes a list of tokens and returns a dict containing the token as a
        key and its frequency as its value.
        """
        frequencies = dict()
        # Looping through each token in tokenList: O(n)
        for token in token_list:
            # Adding/setting key and values in a dict: O(1)
            if token in frequencies:
                frequencies[token] += 1
            else:
                frequencies[token] = 1

        return frequencies

    def index(self, folder_name: str, restart=False) -> None:
        """
        This is the main function that indexes the corpus. It writes every
        word, frequency per document, and importance score to multiple partial
        indexes.
        """
        # Clears all relevant files if the restart boolean is set to true. Will
        # not happen if the corpus already exists unless the user manually
        # alters index_status.log
        if restart:
            self.file_handler.clear_files()

        # index_id is the id of the partial index. It goes up after every
        # offload.
        index_id = 0

        # This is the dict that stores the partial index. It is dumped and
        # cleared each offload
        index_dict = dict()

        # This is the set of websites (defragged) travelled.
        traversed = set()

        # Loops through each file that ends in '.json' in the corpus
        for file in self.file_handler.walk_files(folder_name, '.json'):
            # Gets the url, contents, and 3 tiers of important words from the
            # file. important1 is bold/strong text, important2 are headers, and
            # important3 is the title text.
            url, normalText, important1, important2, important3 = self.file_handler.parse_file(file)

            # Removes the fragments from the url.
            url = urldefrag(url)[0]

            # If the defragged url already exists in the traversed set, it is
            # removed.
            if url not in traversed:
                # The contents of the document are tokenized into normalText
                normalText = self.tokenize(normalText)
                # The text considered important are tokenized and put into a
                # set. (We don't count the frequency of important text since we
                # already got the frequencies in normalText).
                important1 = set(self.tokenize(important1))
                important2 = set(self.tokenize(important2))
                important3 = set(self.tokenize(important3))

                # Find frequencies of each word and put it in a dict
                frequencies = self.compute_word_frequencies(normalText)

                # Loop through each word in the dict
                for word, frequency in frequencies.items():

                    # Calculates the importance score. If the word appears in
                    # bold or strong text, add 1 to the importance. If the word
                    # is a header, add 2 and if the word is a title, add 3. The
                    # max importance score for a word is 6 (if it is all 3).
                    importance = 0
                    if word in important1:
                        importance += 1
                    if word in important2:
                        importance += 2
                    if word in important3:
                        importance += 3

                    # If the word is not in the partial index, add it. The word
                    # is the key and its value is an empty dict.
                    if word not in index_dict:
                        index_dict[word] = dict()
                    # The frequency and importance score of the word is added
                    # to the dict within the partial index.
                    # i.e. {apple (word): {123 (doc_id): 2 (frequency), 1 (importance}}
                    index_dict[word][self.doc_id] = (frequency, importance)

                # Keep record of doc id and url
                self.add_doc_id(url)

                # Add url to the traversed set
                traversed.add(url)

            # Print a message every 100 documents traversed (just a message for
            # the user to keep track).
            if self.doc_id % 100 == 0:
                print(f'Looped through {self.doc_id} pages!')

            # If enough pages have been traversed to reach the offset count
            # (default 10,000), write the partial index to a txt file and clear
            # it from memory.
            if self.doc_id % self.file_count_offset == 0:
                print(
                    f'Looped through {self.doc_id} pages. Offloading to pi{index_id}')
                self.file_handler.write_to_file(index_id, index_dict)
                index_dict.clear()
                # Increments index_id to signify that the new dict will be part
                # of the next partial index.
                index_id += 1
                print('Done with offloading, continuing.')

        # Final offload
        print(f'Looped through every page. Offloading to pi{index_id}')
        self.file_handler.write_to_file(index_id, index_dict)
        index_dict.clear()

        # Writes the doc_id list to a json file.
        self.file_handler.dump_json(self.doc_id_dict, './db/doc_id.json')
        self.doc_id_dict.clear()

    def merge_indexes(self, folder_path: str) -> None:
        """
        Merges all partial indexes into one giant index. If the indexes contain
        the same words, merge their results together.
        """
        files_to_be_merged = []

        # For every partial index files in the folder,
        # add to the list to be merged.
        for file in self.file_handler.walk_files(folder_path, '.txt'):
            if 'pi' in file:
                files_to_be_merged.append(file)
        
        files_to_be_merged.sort(reverse=True)
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
                    temp_dict = self.merge_posting(eval(line1)[1], eval(line2)[1])
                    output_temp.write(
                        str((word1, temp_dict)) + '\n')
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
        self.file_handler.remove_partial_indexes()
        print("Index merge complete.")


    def calculate_tf_idf(self, file, outputfile, size):
        """
        Calculates tf-idf lnc score. Stores the result
        in the outputfile.

        Gets 1 + ln(term frequency)
        Does not calculate idf (that is done with queries using ltc)

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

        normalizers = dict()
        temp_dict = dict()
        count = 1

        for line in inverted_index:
            # gets the tuple item from inverted index file
            tup = eval(line.strip('\n'))

            for doc_id, tf_value in tup[1].items():
                lnc_value = 1 + math.log(tf_value[0])
                temp_dict[doc_id] = (lnc_value, tf_value[1])

                if doc_id not in normalizers:
                    normalizers[doc_id] = lnc_value * lnc_value
                else:
                    normalizers[doc_id] += (lnc_value * lnc_value)

            # writes the lnc value to the output file and
            # clears temp_dict for the next loop (next line)
            tf_idf_index.write(str((tup[0], temp_dict)) + '\n')
            temp_dict.clear()

            # keeps track of the current status while running this function
            count += 1
            if count % 1000 == 0:
                print(f'{count} words calculated!')

        inverted_index.close()
        tf_idf_index.close()

        # square roots all of the values of normalizers
        for doc_id in normalizers.keys():
            normalizers[doc_id] = math.sqrt(normalizers[doc_id])

        # returns the normalizers dict (we need this for the normalize function!)
        return normalizers
    
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

        self.file_handler.remove_tf_idf_indexes()

    def get_fp_locations(self, index_file, fp_file):
        """
        Gets the file pointer location of each word's line in the index using
        the tell function and writes it to a dict. This dict is then dumped
        as a json.
        Input Parameter:
        index_file -> the outputfile from the normalize_tf_idf function (the
        final index)
        fp_file -> the file to store the result of the file pointer locations
        Return Value:
        None
        """

        # Update current status
        last_ran_timestamp = datetime.now()
        self.file_handler.set_index_status(False, last_ran_timestamp)

        index = open(index_file, 'r')
        fp_locations = open(fp_file, 'w')

        # fp_dict is the dict that stores the file pointer locations.
        # key: token, element: file pointer location int
        fp_dict = dict()
        count = 1

        while True:
            # check where the file pointer is at currently
            fp = index.tell()

            # then read the line
            line = index.readline().strip('\n')

            # end loop if the end of the file is reached
            if line == '':
                break

            tup = eval(line)

            # adds the file pointer location to fp_dict's token key
            fp_dict[tup[0]] = fp

            # keeptracks of the current status while running this function
            count += 1
            if count % 10000 == 0:
                print(f"{count} words' file locations found!")

        # dumps the dict as a json
        print("Dumping the file pointer dict...")
        self.file_handler.dump_json(fp_dict, fp_locations)

        index.close()
        fp_locations.close()

        # Set index status to True
        self.file_handler.set_index_status(True, last_ran_timestamp)

    def merge_posting(self, posting1, posting2):
        d = {k : v for k, v in sorted({** posting1, **posting2}.items())}
        return d


if __name__ == '__main__':
    test = Indexer(FileHandler(), file_count_offset=10000)
    line1 = {14300: (1, 0), 14435: (1, 0), 14447: (4, 1), 14462: (8, 1), 14572: (1, 0), 14609: (1, 0), 14793: (1, 0), 14828: (46, 1), 14860: (1, 0), 14865: (2, 0), 14893: (3, 0)}
    line2 = {14301: (1, 0)}
    test.merge_posting(line1, line2)