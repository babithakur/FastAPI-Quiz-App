from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
quiz_db = client.quiz
quiz_collection = quiz_db.questions
users_collection = quiz_db.users
