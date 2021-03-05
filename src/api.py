from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from endpoints import Search
from search_engine import SearchEngine


app = Flask(__name__)
api = Api(app)
CORS(app)

search_engine = SearchEngine()

api.add_resource(Search, '/search',
                 resource_class_kwargs={'search_engine': search_engine})

if __name__ == '__main__':
    app.run()
