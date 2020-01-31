import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

DB = client["CC"]
users = DB["users"]
rides = DB["rides"]
r = DB["rideID"]

r.insert_one({"maxRideID": 0})
