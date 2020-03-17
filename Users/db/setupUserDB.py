import pymongo
import json as Json

with open('/code/config.json') as json_file:
  config = Json.load(config["MongoClientUser"])

client = pymongo.MongoClient(config["MongoClientRides"])

UserDB = client["UserDB"]
users = UserDB["users"]
