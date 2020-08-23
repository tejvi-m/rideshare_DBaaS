#!/bin/bash
mongod --fork --logpath /var/log/mongodb.log --bind_ip 172.16.238.10
python3 /code/db/setupUserDB.py
python3 /code/UserMicroservice/UserManagementAPIs.py
