import pymongo

client = pymongo.MongoClient("mongodb://172.16.238.10:27017/")

UserDB = client["UserDB"]
users = UserDB["users"]
