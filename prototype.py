from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.algo_comp
serverStatusResult=db.command("serverStatus")
db.test.insert_one({"test": "hello"})