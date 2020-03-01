import pymongo

client = pymongo.MongoClient("mongodb://172.16.238.11:27017/")

RideDB = client["RideDB"]

rides = RideDB["rides"]
r = RideDB["rideId"]

r.insert_one({"maxRideID": 0})
