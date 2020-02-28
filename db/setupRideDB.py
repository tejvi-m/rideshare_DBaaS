import pymongo

client = pymongo.MongoClient("mongodb://172.16.238.10:27017/")

RideDB = client["RideDB"]

rides = UserDB["rides"]
r = RideDB["rideId"]

r.insert_one({"maxRideID": 0})
