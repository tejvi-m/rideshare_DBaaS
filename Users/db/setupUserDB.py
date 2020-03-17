import pymongo
import json as Json

with open('/code/config.json') as json_file:
  config = Json.load(json_file)

client = pymongo.MongoClient(config["MongoClientUser"])

UserDB = client["UserDB"]
users = UserDB["users"]
http_users = UserDB["users"]