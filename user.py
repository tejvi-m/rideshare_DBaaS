from flask import Flask, render_template,\
jsonify,request,abort
from flask_pymongo import PyMongo
import re
import datetime

app=Flask(__name__)
app.config['MONGO_DBNAME'] = 'mydb'
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydb"

mongo = PyMongo(app)

user_collection = mongo.db.users
location_collection = mongo.db.location

def user_exists(username):
    return user_collection.find_one({"username": username})

def location_exists(loc):
    return location_collection.find_one({"place_id": loc})

@app.route("/api/v1/users", methods=["PUT"])
def add_user():
    user = request.get_json()    
    if(user_exists(user["username"])):
        abort(405)
    else:
        pattern = re.compile(r'\b[0-9a-fA-F]{40}\b')
        s = str(user["password"])
        #if(re.search(pattern, s)):
        if(1):
            user_collection.insert(user)
            return "success"
        else:
            abort(400)


@app.route("/api/v1/users/<username>", methods=["DELETE"])
def del_user(username):
    if(user_exists(username)):
        user_collection.remove( { "username" : username })
        return "success"
    else:
        abort(405)

@app.route("/api/v1/rides", methods=["POST"])
def create_ride():
    ride_info=request.get_json()
    if(user_exists(ride_info["created_by"])):
        try:
            d = datetime.strptime(ride_info["timestamp"], "%d-%b-%Y:%H-%M-%S")
            if(location_exists(ride_info["source"]) and location_exists(ride_info["destination"])):
                return "success"
            else:
                abort(400)
        except:
            abort(400)
    else:
        abort(405)   