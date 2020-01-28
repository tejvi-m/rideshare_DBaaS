from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import random
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_DB'] = 'TestDB'

mysql = MySQL(app)
#The schema is yet to be decided!! 
#Assumed schema 
##  CREATE TABLE Rides( rideId INT AUTO_INCREMENT PRIMARY KEY NOT NULL, 
#                       creator VARCHAR(30) NOT NULL,
#                       users VARCHAR(10000),
#                       timestamp VARCHAR(20), 
#                       source INT, destination INT);
@app.route('/api/v1/rides', methods=['GET', 'POST'])
def add_rides():
    if(request.method == "POST"):
        details = request.get_json()
        
        creator = details['creator']
        timestamp = details['timestamp']
        source = details['source']
        destination = details['dst']
        rideId = random.randint(0, 100000)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Rides VALUES (%s, %s, %s, %s, %s, %s);", (rideId, creator, str(creator), timestamp, source, destination))
        mysql.connection.commit()
        cur.close()
        return "aayto"
    return "use POST"

@app.route('/api/v1/rides/<rideID>', methods=['GET'])
def getRideDetails(rideID):
    
    cur = mysql.connection.cursor()
    
    query = "SELECT * FROM Rides WHERE rideId = " + rideID + ";"
    print(query)
    cur.execute(query)        
    data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return jsonify(data)

@app.route('/api/v1/rides/<rideID>', methods=['GET'])
def deleteRide(rideID):
    if(request.method == "DELETE"):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Rides WHERE rideId=%s;", (rideID, ))
        mysql.connection.commit()
        cur.close()
        return "done."
    return "aagalla"

@app.route('/api/v1/rides/details', methods=['GET'])
def getUpcomingRides():
    
    details = request.get_json()
    source = details["source"]
    destination = details["destination"]
    cur = mysql.connection.cursor()
    query = "SELECT rideId, creator, timestamp FROM Rides WHERE source = " + source + " and destination = " + destination + ";"
    print(query)
    cur.execute(query)        
    data = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return jsonify(data)

@app.route('/api/v1/rides/join/<rideID>', methods=['POST'])
def joinRide(rideID):
    details = request.get_json()
    newUser = details['username']
    cur = mysql.connection.cursor()
    query = "UPDATE Rides SET users = CONCAT(users, \", " + newUser +"\") WHERE rideId = "+ rideID +";"
    print(query)
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return "done."



if __name__ == '__main__':
    app.run()
