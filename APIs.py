from flask import Flask, render_template, jsonify, request, abort, make_response
import requests
import pymongo
from pprint import pprint

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]

port = '5005'

"""
API - 4
"""

# check route
# TODO: add timestamp checking
@app.route('/api/v1/rides', methods = ["GET"])
def getUpcomingRides():

    source = request.args.get('source')
    destination = request.args.get('destination')

    print(source, destination)

    if source == "" or destination == "":
        abort(400)

    dataToMatch = {"collection": "customers", "data" : {"source":source, "destination":destination}}
    req = requests.post("http://127.0.0.1:" + port + "/api/v1/db/read", json = dataToMatch)
    data = req.json()

    return data


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

    elif req["operation"] == "delete":
        try:
            delete = collection.delete_one(data)
        except:
            abort(500)

    else:
        abort(500)
    return "OK"

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

        return make_response(jsonify(matches), 200)

    except:
        abort(500)


if __name__ == '__main__':
	app.debug=True
	app.run(port = port)
