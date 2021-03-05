from flask import jsonify, make_response
from flask_restful import Resource, reqparse



class Search(Resource):
    def __init__(self, search_engine):
        self.search_engine = search_engine
        self.log_file = open('./api_log.log', 'a+')

    def __exit__(self):
        self.log_file.close()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)

        args = parser.parse_args()
        query = args['query']

        result = self.search_engine.search(query)

        response = jsonify(result)
        response.status_code = 200

        return response
