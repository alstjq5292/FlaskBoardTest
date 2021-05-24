from flask import *
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mslim"
mongo = PyMongo(app)

board = mongo.db.board
test = [
    {"title" : "안녕하세요", "id" : "tmdcjf111", "content" : "안녕하세요 질문이 있습니다. 블라블라블라"}
    ]

board.insert_many(test)