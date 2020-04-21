import pymongo
import json


class DB:
    def __init__(self, ip):
        self.ip = ip
        self.mClient = pymongo.MongoClient(self.ip)

    def get_data(self, jsonData):
            req = json.loads(jsonData)

            db = self.mClient[req["DB"]]
            collection = db[req["collection"]]

            if req["operation"] == "getNewRideID":
                    try:
                        newRide = collection.find_one()["maxRideID"]
                        return str(newRide + 1)
                    except:
                        return "read failed"

            else:
                match = req["data"]
                selectFields = req["selectFields"]

                try:
                    records = collection.find(match, selectFields)

                    matches = {}
                    c = 0

                    for x in records:
                        matches.update({c: x})
                        c += 1

                    if c == 0:
                         return ""

                    return json.dumps(jsonify(matches))
                except:
                    return "read failed"



    def write_data(self, jsonData):

        req = json.loads(jsonData)

        db = self.mClient[req["DB"]]
        collection = db[req["collection"]]
        data = req["data"]

        if req["operation"] == "add":
            try:
                add = collection.insert_one(data)
            except:
                return "write failed"

        elif req["operation"] == "delete":
            try:
                delete = collection.delete_many(data)

                if(delete.deleted_count == 0):
                    return "write failed"

            except:
                return "write failed"

        elif req["operation"] == "update":
            try:
                user = req["extend"]["users"]

                update = collection.update_one(data, {"$addToSet" : {"users" : user}})

            except:
                return "write failed"
        elif req["operation"] == "update-pull":
            try:
                user = req["remove"]["users"]

                update = collection.update_many(data, {"$pull" : {"users" : user}})

            except:
                return "write failed"


        elif req["operation"] == "set":
            try:
                newID = req["ID"]
                update = collection.update(collection.find_one(), {"$set" : {"maxRideID" : newID}})
            except:
                return "write failed"

        else:
            return "write failed"

        return "OK"
