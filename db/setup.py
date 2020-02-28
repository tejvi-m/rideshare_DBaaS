import pymongo

client = pymongo.MongoClient("mongodb://172.17.0.2:27017/")

UserDB = client["UserDB"]
RideDB = client["RideDB"]

users = UserDB["users"]

rides = UserDB["rides"]
r = RideDB["rideId"]

r.insert_one({"maxRideID": 0})
