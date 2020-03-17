import pymongo
import json as Json

with open('/code/config.json') as json_file:
  config = Json.load(json_file)

client = pymongo.MongoClient(config["MongoClientRides"])
RideDB = client["RideDB"]

rides = RideDB["rides"]
r = RideDB["rideId"]

r.insert_one({"maxRideID": 0})
