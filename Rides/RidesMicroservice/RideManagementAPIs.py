from flask import Flask, render_template, jsonify, request, abort, make_response, json
import flask
import requests
import pymongo
from pprint import pprint
import datetime
import json as Json
#from multiprocessing import Value
import redis
import time

from utils import *


with open('/code/config.json') as json_file:
  config = Json.load(json_file)

app = Flask(__name__)
client = pymongo.MongoClient(config["MongoClientRides"])
db = client["RideDB"]

port = config["RideManagementPort"]
server = config["RideManagementIP"] + ":" + port
DBOrch = config["Orchestrator"] + ":" + config["DBport"]
usersMicroService = config["UserManagementIP"] + ":" + config["UserManagementPort"]

#counter = Value('i', 0)
count = redis.Redis(host = config["RedisRides"], port = 6379)
count.set('hits', 0)

@app.before_request
def beforeReq():
    exemptURLs = ["/", "/api/v1/db/read", "/api/v1/db/write", "/api/v1/db/clear", "/api/v1/_count"]
    if flask.request.path not in exemptURLs:
        print(flask.request.path)
        increment()


def checkUser(username):
    # call listUsers from the User management microservice

    headers = {'Origin': 'ec2-54-174-188-107.compute-1.amazonaws.com'}
    requestToCheck = requests.get(usersMicroService + "/api/v1/users", headers=headers)

    if requestToCheck.status_code != 204 and requestToCheck.status_code != 400 and username in requestToCheck.json():
        return True
    else:
        return False

def increment():
    count.incr('hits')

"""
API - 3

API to create a ride

request: POST created_by, timestamp, source, destination
response: {}

status codes: 201 - successful creation
            400 - invalid user, invalid location, empty fields

TODO: Check timestamp

"""
@app.route("/api/v1/rides", methods = ["POST"])
def createRide():

    data = request.get_json()

    try:
        username = data["created_by"]
        source, destination = data["source"], data["destination"]
        timestamp = datetime.datetime.strptime(data["timestamp"], "%d-%m-%Y:%H-%M-%S")

    except KeyError:
        return make_response("Enter all valid details", 400)

    except ValueError:
        return make_response("Invalid timestamp", 400)

    if not find_area(source) or not find_area(destination):
        return make_response("invalid area", 400)


    exists = checkUser(username)

    if not exists:
        return make_response("Error: Invalid user", 400)

    reqNewIDData = {"DB": "RideDB", "operation" : "getNewRideID", "collection": "rideId"}
    reqNewID = requests.post(DBOrch + "/api/v1/db/read", json = reqNewIDData)

    if(reqNewID.status_code != 200):
        return make_response(reqNewID.text, reqNewID.status_code)

    newID = float(reqNewID.text)
    data["rideId"] = int(newID)

    data["users"] = []

    # updating new Ride id first, because if creating a new ride fails, the next time we get a new id, it will still be unique
    # but if we update ride first but if updation of ride ID fails, there will be duplication of ride rideIDs
    updateID = {"DB": "RideDB", "operation" : "set", "collection" : "rideId", "data" : {}, "ID": newID}
    updateReq = requests.post(DBOrch + "/api/v1/db/write", json = updateID)

    if updateReq.status_code != 200:
        return make_response(updateReq.text, updateReq.status_code)

    dataToAdd = {"DB": "RideDB", "operation" : "add", "selectFields" : {"_id" : 0}, "collection" : "rides", "data" : data}
    req = requests.post(DBOrch + "/api/v1/db/write", json = dataToAdd)

    if req.status_code != 200:
        return make_response(req.text, req.status_code)

    return make_response(jsonify({}), 201)




"""
API - 4

The request is in the format mentioned below for source 2 to destination 3
/api/v1/rides?source=2&destination=3

TODO: add timestamps

request: GET, source and destination
response: { rideid, username, timestamp}

"""

# check route
# TODO: add timestamp checking
@app.route('/api/v1/rides', methods = ["GET"])
def getUpcomingRides():

    timeNow = datetime.datetime.now()

    try:
        source = request.args.get('source')
        destination = request.args.get('destination')

    except:
        return make_response("select source and destination", 400)

    if source == "" or destination == "" or not find_area(source) or not find_area(destination):
        return make_response("select valid source and desintation", 400)


    current_time = datetime.datetime.now()
    dtFormat = "%d-%m-%Y:%H-%M-%S"

    dataToMatch = {"DB": "RideDB", "operation" : "read", "collection": "rides", "selectFields": {"timestamp" : 1, "created_by": 1, "rideId": 1, "_id" : 0}, "data" : {"source" : source, "destination" : destination}}
    req = requests.post(DBOrch + "/api/v1/db/read", json = dataToMatch)
    # data = req.json()
    # data = req.json()

    matches = []
    for i in req.json():
        newJson = req.json()[i]
        if(timeNow < datetime.datetime.strptime(newJson["timestamp"], dtFormat)):
            newJson["username"] = newJson.pop("created_by")
            # req.json()[i].pop("created_by")
            matches.append(newJson)

    if (len(matches) == 0):
        return make_response(jsonify(matches), 204)
    else:
        return make_response(jsonify(matches), req.status_code)


@app.route("/api/v1/rides/count", methods = ["GET"])
def count_rides():

    rides = {"DB": "RideDB", "operation": "read", "selectFields" : {"_id" : 0}, "collection" : "rides" , "data" : {}}
    req = requests.post(DBOrch + "/api/v1/db/read", json = rides)

    if req.status_code == 204 or req.status_code == 400:
        return (jsonify([0]), 200)
    elif req.status_code == 200:
        return (jsonify([len(req.json().keys())]), 200)
    else:
        return (jsonify({}), req.status_code)

"""
API - 5
List all details of a ride



"""
# TODO: add the right status codes
@app.route("/api/v1/rides/<rideID>", methods = ["GET"])
def getRideDetails(rideID):

    rideID = int(rideID)
    dataToMatch = {"DB": "RideDB", "operation": "read", "selectFields" : {"_id" : 0}, "collection" : "rides" , "data" : {"rideId" : rideID}}
    req = requests.post(DBOrch + "/api/v1/db/read", json = dataToMatch)

    # Ride does not exist
    if(req.status_code == 400):
         return(make_response("rideID does not exist", 400))

    else:
        data = req.json()["0"]
        # rideIDs being unique will only have one entry in the response

        return make_response(data, 200)



"""
API - 6

"""
@app.route("/api/v1/rides/<rideID>", methods = ["POST"])
def joinRide(rideID):

    rideID = int(rideID)

    user = request.get_json()["username"]

    exists = checkUser(user)

    if not exists:
        return make_response("Error: Invalid user", 400)

    dataToCheckUser = {"DB": "RideDB", "operation": "read", "selectFields" : {"_id" : 0, "created_by" : 1}, "collection" : "rides", "data": {"rideId" : rideID}}
    requestToCheckUser = requests.post(DBOrch + "/api/v1/db/read", json = dataToCheckUser)
    createdBy = requestToCheckUser.json()["0"]["created_by"]
    #
    if(user == createdBy):
        return make_response("Error: user cannot join their own ride", 400)

    # print(requestToCheckUser.json())
    dataToUpdate = {"DB": "RideDB", "operation": "update", "collection": "rides", "data" : {"rideId": rideID}, "extend": {"users" : user}}
    req = requests.post(server + "/api/v1/db/write", json = dataToUpdate)

    if(req.status_code == 200):
        return make_response("", 200)
    else:
        return make_response("", req.status_code)




"""
API - 7


"""
@app.route("/api/v1/rides/<rideID>", methods = ["DELETE"])
def deleteRide(rideID):

    rideID = int(rideID)
    dataToDelete = {"operation" : "delete", "collection" : "rides", "data" : {"rideId" : rideID}}
    req = requests.post(DBOrch + "/api/v1/db/write", json = dataToDelete)

    if req.status_code == 200:
         return make_response("", 200)
    else:
        abort(req.status_code)




"""

API - 8

use this API to write to the database
Currently using mongodb as the database to store information about rides

sending data through POST:
the post request is to be structured as follows (JSON):
["operation": "add/delete/update/set", "collection" : "<collection_name>", "data" : {data_to_insert}, "extend"(if using update) : {"users" : "user"} ]

add : to add to db
delete : to delete from db
update: mostly used to append a new user to the users in a ride. can be used to add any value to any array on the db with minor tweaks.
set: used almost exclusively setting a new rideid


The API must support the following operations:
1. write username and hashed password
2. delete a user
3. create a new ride
4. join an existing ride
5. delete a ride

returns status code 200 OK if successful.

"""

# @app.route('/api/v1/db/write', methods=["POST"])
# def write():

#     req = request.get_json()
#     collection = db[req["collection"]]
#     data = req["data"]

#     if req["operation"] == "add":
#         try:
#             add = collection.insert_one(data)
#         except:
#             abort(500)

#     elif req["operation"] == "delete":
#         try:
#             delete = collection.delete_many(data)

#             if(delete.deleted_count == 0):
#                 return make_response("", 400)
#             else:
#                 return make_response("", 200)
#         except:
#             return(make_response("", 500))

#     elif req["operation"] == "update":
#         try:
#             user = req["extend"]["users"]

#             update = collection.update_one(data, {"$addToSet" : {"users" : user}})

#         except:
#             return make_response("", 500)
#     elif req["operation"] == "update-pull":
#         # try:
#             user = req["remove"]["users"]

#             update = collection.update_many(data, {"$pull" : {"users" : user}})

#         # except:
#         #     return make_response("", 500)


#     elif req["operation"] == "set":
#         try:
#             newID = req["ID"]
#             update = collection.update(collection.find_one(), {"$set" : {"maxRideID" : newID}})
#         except:
#             return(make_response("", 500))

#     else:
#         return(make_response("", 500))
#     return make_response("", 200)



"""
API 9
use this API to read from the database
Currently using mongodb as the database to store information about rides

sending data through POST:
the post request is to be structured as follows (JSON):
["operation": "getNewRideID/read", "collection" : "<collection_name>", "data_to_match" : {data_to_match}]

The API must support the following operations:
1. list upcoming rides given a source and destination
2. given a ride id, list all its details

returns the data in json format.
"""

# # TODO: return less generic status codes
# @app.route('/api/v1/db/read', methods=["POST"])
# def read():

#     req = request.get_json()
#     collection = db[req["collection"]]

#     if req["operation"] == "getNewRideID":
#             # newRide = list(collection.find().sort([("rideIDn",-1)]).limit(1))[0]["rideIDn"]
#             # return make_response(str(newRide + 1), 200)
#             try:
#                 newRide = collection.find_one()["maxRideID"]
#                 return make_response(str(newRide + 1), 200)
#             except:
#                 return make_response("", 500)

#     else:
#         match = req["data"]
#         selectFields = req["selectFields"]

#         try:
#             # not returning _id, plus having _id has problems with jsonify
#             records = collection.find(match, selectFields)

#             matches = {}
#             c = 0

#             for x in records:
#                 matches.update({c: x})
#                 c += 1

#             if c == 0:
#                  return make_response(jsonify({}), 400)

#             return make_response(jsonify(matches), 200)
#         except:
#             make_response("", 500)



"""
API 11
clear database
"""
# @app.route('/api/v1/db/clear', methods=["POST"])
# def clearDB():

#     db.rides.remove({})
#     db.rideId.remove({})
#     db["rideId"].insert_one({"maxRideID": 0})


#     return make_response("", 200)

"""
API 12
Count HTTP Requests
"""
@app.route('/api/v1/_count', methods=['GET'])
def get_count():
    try:
        return make_response(jsonify([int(count.get('hits'))]), 200)
    except:
        return make_response("", 400)
"""
API 13
Reset count
"""
@app.route('/api/v1/_count', methods=['DELETE'])
def reset_count():
    try:
        count.set('hits', 0)
        return make_response(jsonify({}), 200)
    except:
        return make_response("", 400)


if __name__ == '__main__':
	app.debug=True
	app.run('0.0.0.0', port = port, threaded=True)
	# app.run('127.0.0.1', port = config["RideManagementPort"])
