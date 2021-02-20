import pprint


class Query:
    def __init__(self, file_handler, indexer):
        self.fp_dict = file_handler.load_json('./db/fp_locations.json')
        self.doc_id_dict = file_handler.load_json('./db/doc_id.json')
        self.final_index = open('./db/index.txt')

        self.indexer = indexer
        self.query_tokens = None
        self.merged_posting = dict()

    def peek_posting(self, iterable):
        try:
            next_iter = next(iterable)

        except StopIteration:
            return None

        return next_iter

    def get_intersecting_posting(self, posting1, posting2):
        posting1_iter = iter(posting1)
        posting2_iter = iter(posting2)
        intersection = dict()

        p1 = self.peek_posting(posting1_iter)
        p2 = self.peek_posting(posting2_iter)

        while p1 != None and p2 != None:
            if p1 == p2:
                score1 = posting1[p1]
                score2 = posting2[p2]
                intersection[p1] = (score1[0] + score2[0],
                                    1 if score1[1] == 1 or score2[1] == 1 else 0)

                p1 = self.peek_posting(posting1_iter)
                p2 = self.peek_posting(posting2_iter)

            elif p1 > p2:
                p2 = self.peek_posting(posting2_iter)

            else:
                p1 = self.peek_posting(posting1_iter)

    def get_query(self):
        query = input("Please enter the query: ")
        self.query_tokens = self.indexer.tokenize(query)

        return query

    def process_query(self):
        self.merged_posting.clear()

        if self.query_tokens != None:
            for token in self.query_tokens:
                try:
                    fp = self.fp_dict[token]
                    self.final_index.seek(fp)
                    
                    # if the merged_posting is empty
                    if not self.merged_posting:
                        self.merged_posting = eval(self.final_index.readline())[1]
                    else:
                        self.merged_posting = self.get_intersecting_posting(
                            eval(self.final_index.readline())[1],
                            self.merged_posting
                        )

                except KeyError:
                    print(f'No token {token} found.')

    def get_result(self):
        if self.merged_posting:
            sorted_tup = sorted(self.merged_posting.items(), key=lambda item: item[1], reverse=True)
            for i in range(5):
                try:
                    found_doc_id = sorted_tup[i][0]
                    print(self.doc_id_dict[str(found_doc_id)])   # print the url of the found doc id
                except IndexError:
                    break
        else:
            print('No results found')


