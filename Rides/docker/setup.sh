#!/bin/bash
mongod --fork --logpath /var/log/mongodb.log --bind_ip 172.16.238.11
python3 /code/db/setupRideDB.py
python3 /code/RidesMicroservice/RideManagementAPIs.py
