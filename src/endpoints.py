from flask import jsonify, make_response
from flask_restful import Resource, reqparse


class Search(Resource):
    def __init__(self, search_engine):
        # Receive search engine from the api app
        self.search_engine = search_engine

    # Handle HTTP POST request to the api
    # at /search endpoint
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)

        # Parse the arguments
        args = parser.parse_args()
        # Get query from the arguments
        query = args['query']

        # Get result from the search engine
        result = self.search_engine.search(query)

        # Return response in JSON format
        response = jsonify(result)
        response.status_code = 200

        return response
