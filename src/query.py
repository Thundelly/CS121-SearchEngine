import math
import re

class Query:
    def __init__(self, file_handler, indexer):
        self.fp_dict = file_handler.load_json('./db/fp_locations.json')
        self.doc_id_dict = file_handler.load_json('./db/doc_id.json')
        self.final_index = open('./db/index.txt')

        self.indexer = indexer
        self.query_tokens = dict()
        self.posting = dict()

    def get_query(self):
        query = input("\nPlease enter the query: ")
        self.query_tokens = self.indexer.tokenize(query)
        print(self.query_tokens)

    def process_query(self):
        if self.query_tokens:

            token_freq = dict()
            for token in self.query_tokens:
                if token in token_freq:
                    token_freq[token] += 1
                else:
                    token_freq[token] = 1

            query_scores = dict()
            document_term_scores = dict()
            normalizer = 0

            for token, tf in token_freq.items():
                try:
                    fp = self.fp_dict[token]
                    self.final_index.seek(fp)
                    token_posting = Query.fast_eval(self.final_index.readline())[1]

                    for doc_id, score in token_posting.items():
                        if doc_id not in document_term_scores:
                            document_term_scores[doc_id] = dict()
                        document_term_scores[doc_id][token] = score

                    query_scores[token] = (1 + math.log(tf)) * math.log(len(self.doc_id_dict) / len(token_posting))
                    normalizer += query_scores[token] * query_scores[token]

                except KeyError:
                    print(f'No token {token} found.')

            normalizer = math.sqrt(normalizer)
            for token in query_scores.keys():
                query_scores[token] = query_scores[token] / normalizer

            for doc_id, term_scores in document_term_scores.items():
                final_score = 0.0
                for token, score in query_scores.items():
                    try:
                        final_score += (score * term_scores[token][0])
                        final_score += term_scores[token][1]
                    except KeyError:
                        pass
                # len(term_scores) is how many query terms appear in the doc
                self.posting[doc_id] = (final_score, len(term_scores))

    def get_result(self):
        if self.posting:
            # prioritize docs containing the most query terms, then prioritize importance, then cosine similarity
            sorted_tup = sorted(self.posting.items(),
                                key=lambda item: (item[1][1], item[1][0]), reverse=True)

            print('\n\n===== Top 10 Results =====\n\n')
            for i in range(10):
                try:
                    found_doc_id = sorted_tup[i][0]
                    # print the url of the found doc id
                    print(self.doc_id_dict[str(found_doc_id)], found_doc_id, sorted_tup[i][1])

                except IndexError:
                    break

            self.posting.clear()

        else:
            print('No results found')

    @staticmethod
    def fast_eval(line):
        new_str = re.sub("'|,|{|:|}|\(|\)", "", line.strip())
        str_list = new_str.split()
        token = str_list[0]
        scores_dict = dict()
        for i in range(1, len(str_list), 3):
            scores_dict[int(str_list[i])] = (float(str_list[i + 1]), int(str_list[i + 2]))

        return (token, scores_dict)
