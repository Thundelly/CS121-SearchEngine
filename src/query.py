import math

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
                    token_posting = eval(self.final_index.readline())[1]

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
                self.posting[doc_id] = (final_score)


    def get_result(self):
        if self.posting:
            sorted_tup = sorted(self.posting.items(),
                                key=lambda item: item[1], reverse=True)

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
