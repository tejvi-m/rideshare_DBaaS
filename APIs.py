from flask import Flask, render_template, jsonify, request, abort
import pymongo
from pprint import pprint

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]



"""

API - 8
use this API to write to the database
Currently using mongodb as the database to store information about rides

sending data through POST:
the post request is to be structured as follows (JSON):
["operation": "add/delete", "table" : "<table_name>", "column" : "<column_name>", "data" : {data_to_insert}]

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
    column = db[req["column"]]
    data = req["data"]

    if req["operation"] == "add":
        try:
            add = column.insert_one(data)
        except:
            panic(500)

    elif req["operation"] == "delete":
        try:
            delete = column.delete_one(data)
        except:
            panic(500)
            
    else:
        panic(500)
    return "OK"


if __name__ == '__main__':
	app.debug=True
	app.run(port ='5000')
