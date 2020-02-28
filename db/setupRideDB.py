import pymongo

client = pymongo.MongoClient("mongodb://172.17.0.2:27017/")

RideDB = client["RideDB"]

rides = UserDB["rides"]
r = RideDB["rideId"]

r.insert_one({"maxRideID": 0})
