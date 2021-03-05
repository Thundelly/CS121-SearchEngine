import math
import re
import nltk
from nltk.corpus import stopwords

class Query:
    def __init__(self, file_handler, indexer, cached_words):
        self.fp_dict = file_handler.load_json('./db/fp_locations.json')
        self.doc_id_dict = file_handler.load_json('./db/doc_id.json')
        self.final_index = open('./db/index.txt')

        self.indexer = indexer
        self.query_tokens = dict()
        self.posting = dict()

        self.stop_words = set(stopwords.words('english'))
        self.cached_words = cached_words


    def get_query(self, query):
        # query = input("\nPlease enter the query: ")
        self.query_tokens = self.indexer.tokenize(query)

        # Removes stop words if it is less than 80% of the query
        filtered_tokens = [t for t in self.query_tokens if t not in self.stop_words]
        if len(filtered_tokens) > len(self.query_tokens) * .2:
            self.query_tokens = filtered_tokens
        # print(self.query_tokens)

    def process_query(self):
        """
        Processes the query and gets a list of websites and their scores based
        on cosine similarity, importance score, and the amount of words from
        the query appear in the document.
        """
        # Check if the tokens list is empty. If it is, don't continue.
        if self.query_tokens:
            # Gets the frequencies of the tokens in the query
            token_freq = self.indexer.compute_word_frequencies(self.query_tokens)

            # Gets all the tf-idf scores for each word in the query
            query_scores = dict()
            # Gets all the tf-idf scores for each word for each document.
            # The format is {doc_id: {token: score}}
            document_term_scores = dict()
            # Gets the square root of the sum of squares of the query's scores
            normalizer = 0

            # Loop through each token in the query
            for token, tf in token_freq.items():
                try:

                    # Check if the word is already cached. If so, load that word
                    if token in self.cached_words:
                        token_posting = self.cached_words[token]

                    # Look for the word in the index if the word is not already cached.
                    else:
                        # Get the postings for the token from the index
                        fp = self.fp_dict[token]
                        self.final_index.seek(fp)
                        token_posting = Query.fast_eval(self.final_index.readline())[1]

                    # Get the scores and put them into document_term_scores
                    for doc_id, score in token_posting.items():
                        if doc_id not in document_term_scores:
                            document_term_scores[doc_id] = dict()
                        document_term_scores[doc_id][token] = score

                    # get the log tf score multiplied by the idf
                    query_scores[token] = (1 + math.log(tf)) * math.log(len(self.doc_id_dict) / len(token_posting))
                    # Add the square of that to normalizer
                    normalizer += query_scores[token] * query_scores[token]

                # If the token doesn't exist, ignore it
                except KeyError:
                    print(f'No token {token} found.')

            # Square root the sum of squares to get the final normalizer
            normalizer = math.sqrt(normalizer)

            # Normalizes the query scores by dividing it by the square root of
            # the sum of squares
            for token in query_scores.keys():
                query_scores[token] = query_scores[token] / normalizer

            # Loops from the number of query terms to 0 (for soft conjunction
            # check)
            for i in range(len(query_scores), 0, -1):
                # Loops through each document in document_term_scores
                for doc_id, term_scores in document_term_scores.items():
                    # This is the score that decides the rank
                    final_score = 0.0

                    # Only gets documents that have the same number of query
                    # terms as i (for soft conjunction check)
                    if len(term_scores) == i:
                        # Add all the query scores multiplied by their
                        # respective document scores (lnc.ltc)
                        for token, score in query_scores.items():
                            try:
                                final_score += (score * term_scores[token][0])
                                final_score += term_scores[token][1]
                            # If the query term doesn't exist in the document,
                            # ignore it.
                            except KeyError:
                                pass
                        # Adds the result to the final posting. The posting's
                        # format is: {doc id: (final score, how many query
                        # terms it has)}
                        self.posting[doc_id] = (final_score, len(term_scores))

                # If there are more than 10 documents found, end. Otherwise,
                # check for documents that have 1 fewer query term and repeat.
                # (for soft conjunction check).
                if len(self.posting) >= 10:
                    break

    def get_result(self):
        result = {}

        if self.posting:
            # prioritize docs containing the most query terms, then prioritize importance, then cosine similarity
            sorted_tup = sorted(self.posting.items(),
                                key=lambda item: (item[1][1], item[1][0]), reverse=True)

            print('\n\n===== Top 10 Results =====\n\n')
            for i in range(10):
                try:
                    found_doc_id = sorted_tup[i][0]
                    # print the url of the found doc id
                    # print(self.doc_id_dict[str(found_doc_id)], found_doc_id, sorted_tup[i][1])
                    result[str(i)] = self.doc_id_dict[str(found_doc_id)]


                except IndexError:
                    break

            self.posting.clear()
            result['error_status'] = False
            result['error_message'] = ''

            return result

        else:
            print('No results found')
            result['error_status'] = True
            result['error_message'] = 'No results found.'

            return result

    @staticmethod
    def fast_eval(line):
        # fast_eval is tailored specifically to the index so it is faster than
        # the normal eval function
        new_str = re.sub("'|,|{|:|}|\(|\)", "", line.strip())
        str_list = new_str.split()
        token = str_list[0]
        scores_dict = dict()
        for i in range(1, len(str_list), 3):
            scores_dict[int(str_list[i])] = (float(str_list[i + 1]), int(str_list[i + 2]))

        return (token, scores_dict)

