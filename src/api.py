from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from endpoints import Search
from search_engine import SearchEngine

# Create a flask api
app = Flask(__name__)
api = Api(app)
# Allow Cross Origin Access. This is used for http / https compatibility
CORS(app)

# Make an instance of a search engine
search_engine = SearchEngine()
# Add an api endpoint
# Pass the search engine instance to allow endpoint
# functions to use the engine
api.add_resource(Search, '/search',
                 resource_class_kwargs={'search_engine': search_engine})

if __name__ == '__main__':
    app.run()
