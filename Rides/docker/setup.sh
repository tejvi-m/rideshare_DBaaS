#!/bin/bash
mongod --fork --logpath /var/log/mongodb.log --bind_ip 0.0.0.0
python3 /code/db/setupRideDB.py
python3 /code/RidesMicroservice/RideManagementAPIs.py
