from flask import Flask, render_template, jsonify, request, abort, make_response
import requests
import pymongo
from pprint import pprint
from utils import *

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]

port = '5009'


"""
API - 4

The request is in the format mentioned below for source 2 to destination 3
/api/v1/rides?source=2&destination=3

TODO: add timestamps

The API returns the details of the rides in JSON
"""

# check route
# TODO: add timestamp checking
@app.route('/api/v1/rides', methods = ["GET"])
def getUpcomingRides():

    source = request.args.get('source')
    destination = request.args.get('destination')


    if source == "" or destination == "" or not find_area(source) or not find_area(destination):
        abort(400)

    dataToMatch = {"collection": "customers", "data" : {"source" : source, "destination" : destination}}
    req = requests.post("http://127.0.0.1:" + port + "/api/v1/db/read", json = dataToMatch)
    data = req.json()

    return make_response(data, 200)


"""
API - 5
List all details of a ride



"""
# TODO: add the right status codes
@app.route("/api/v1/rides/<rideID>", methods = ["GET"])
def getRideDetails(rideID):

    dataToMatch = {"collection" : "customers" , "data" : {"rideID" : rideID}}
    req = requests.post("http://127.0.0.1:" + port + "/api/v1/db/read", json = dataToMatch)

    # Ride does not exist
    if(req.status_code == 405):
         abort(405)

    else:
        data = req.json()
        return make_response(data, 200)



"""
API - 6

"""
@app.route("/api/v1/rides/<rideID>", methods = ["POST"])
def joinRide(rideID):
    # check if rideID exists
    # check if username exists

    user = request.get_json()["username"]
    print(user)

    dataToUpdate = {"operation": "update", "collection": "customers", "data" : {"rideID": rideID}, "extend": {"users" : user}}
    req = requests.post("http://127.0.0.1:" + port + "/api/v1/db/write", json = dataToUpdate)

    if(req.status_code == 200):
        return make_response("", 200)
    else:
        return make_response("", req.status_code)




"""
API - 7


"""
@app.route("/api/v1/rides/<rideID>", methods = ["DELETE"])
def deleteRide(rideID):

    dataToDelete = {"operation" : "delete", "collection" : "customers", "data" : {"rideID" : rideID}}
    req = requests.post("http://127.0.0.1:" + port + "/api/v1/db/write", json = dataToDelete)

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
["operation": "add/delete", "collection" : "<collection_name>", "data" : {data_to_insert}]

The API must support the following operations:
1. write username and hashed password
2. delete a user
3. create a new ride
4. join an existing ride
5. delete a ride

returns status code 200 OK if successful.

"""

# TODO: return less generic status codes
@app.route('/api/v1/db/write', methods=["POST"])
def write():

    req = request.get_json()
    collection = db[req["collection"]]
    data = req["data"]

    if req["operation"] == "add":
        try:
            add = collection.insert_one(data)
        except:
            abort(500)

    # does not exit with 405 for some reason
    elif req["operation"] == "delete":
        # try:
            delete = collection.find_one_and_delete(data)

            c = 0
            for x in delete:
                c += 1

            if(c == 0):
                return make_response("", 405)

            else:
                return make_response("", 200)
            # if len(delete) == 0:
            #     return make_response("", 405)

            # delete returns None when empty
            # abort(405)
        # except:
            # abort(500)

    elif req["operation"] == "update":
        # try:
            user = req["extend"]["users"]

            print(user, data)
            update = collection.update(data, {"$push" : {"users" : user}})
        #
        # except:
        #     abort(450)

    else:
        abort(500)
    return make_response("", 200)



"""
API 9
use this API to read from the database
Currently using mongodb as the database to store information about rides

sending data through POST:
the post request is to be structured as follows (JSON):
["collection" : "<collection_name>", "data_to_match" : {data_to_match}]

The API must support the following operations:
1. list upcoming rides given a source and destination
2. given a ride id, list all its details

returns the data in json format.
"""

# TODO: return less generic status codes
@app.route('/api/v1/db/read', methods=["POST"])
def read():

    req = request.get_json()
    collection = db[req["collection"]]
    match = req["data"]

    try:
        # not returning _id, plus having _id has problems with jsonify
        records = collection.find(match, {"_id":0})

        matches = {}
        c = 0

        for x in records:
            matches.update({c: x})
            c += 1

        if c == 0:
             return make_response(jsonify(matches), 405)
        return make_response(jsonify(matches), 200)

    except:
        abort(500)


if __name__ == '__main__':
	app.debug=True
	app.run(port = port)
