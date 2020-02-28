#!/bin/bash

if [ "$NAME" == "USER" ];
then
	mongod --fork --logpath /var/log/mongodb.log --bind_ip 172.16.238.10 
	python3 /code/db/setupUserDB.py
	python3 /code/UserManagementAPIs.py
else
	mongod --fork --logpath /var/log/mongodb.log --bind_ip 172.16.238.11
	python3 /code/db/setupRideDB.py
	python3 /code/RideManagementAPIs.py
fi
