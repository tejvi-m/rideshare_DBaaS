import pymongo
import json


class DB:
    def __init__(self, ip):
        self.ip = ip
        self.mClient = pymongo.MongoClient("mongodb://" + ip + ":27017/")


    def setup(self):
        UserDB = self.mClient["UserDB"]
        users = UserDB["users"]

        RideDB = self.mClient["RideDB"]

        rides = RideDB["rides"]
        r = RideDB["rideId"]

        r.insert_one({"maxRideID": 0})
        print("setup the db")



    def get_data(self, jsonData):
        try:
            print("rec: ", jsonData)
            req = json.loads(jsonData)

            db = self.mClient[req["DB"]]
            collection = db[req["collection"]]

            if req["operation"] == "getNewRideID":
                    try:
                        newRide = collection.find_one()["maxRideID"]
                        print("found new ride id as ", newRide)
                        return [str(newRide + 1), 200]
                    except Exception as e:
                        print(e)
                        return ["read failed:" , 500]

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
                         return [json.dumps({}), 400]

                    return [json.dumps(matches), 200]
                except Exception as e:
                    print(e)
                    return ["read failed:", 500]
        except Exception as e:
            print(e)
            return ["read failed", 500]


    def write_data(self, jsonData):
        try:
            req = json.loads(jsonData)

            if req["operation"] == "clear":
                print("clearing")
                db = self.mClient["RideDB"]
                db.rides.remove({})
                db.rideId.remove({})
                db["rideId"].insert_one({"maxRideID": 0})

                db = self.mClient["UserDB"]
                db.users.remove({})

                return 200

            db = self.mClient[req["DB"]]
            collection = db[req["collection"]]
            data = req["data"]

            if req["operation"] == "add":
                try:
                    print("adding:", data)
                    add = collection.insert_one(data)
                except Exception as e:
                    print(e)
                    return 500

            elif req["operation"] == "delete":
                try:
                    delete = collection.delete_many(data)

                    if(delete.deleted_count == 0):
                        return 400
                    else:
                        return 200

                except Exception as e:
                    print(e)
                    return 500

            elif req["operation"] == "update":
                try:
                    user = req["extend"]["users"]

                    update = collection.update_one(data, {"$addToSet" : {"users" : user}})

                except Exception as e:
                    print(e)
                    return 500
            elif req["operation"] == "update-pull":
                try:
                    user = req["remove"]["users"]

                    update = collection.update_many(data, {"$pull" : {"users" : user}})

                except Exception as e:
                    print(e)
                    return 500


            elif req["operation"] == "set":
                try:
                    newID = req["ID"]
                    print("setting new ride id to ", newID)
                    update = collection.update(collection.find_one(), {"$set" : {"maxRideID" : newID}})
                except Exception as e:
                    print(e)
                    return 500

            else:
                
                return 500

            return 200
        except Exception as e:
            print(e)
            return 500