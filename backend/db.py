from pymongo import MongoClient


# MongoDB local setup
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_budget"]
