#!/bin/bash
mongod --fork --logpath /var/log/mongodb.log --bind_ip 0.0.0.0
python3 /code/db/setupUserDB.py
python3 /code/UserMicroservice/UserManagementAPIs.py
