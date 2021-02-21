from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from endpoints import Search


app = Flask(__name__)
api = Api(app)
CORS(app)


api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run()
