# first arg: ip address to bind mongo to, as well as to be used in the workers. 
# second arg: type of container.
# third arg: name of ctr
mongod --fork --logpath /var/log/mongodb.log --bind_ip $1
cd /code 
echo "dumping the database"
mongodump --host 172.16.238.05
echo "dumped the database"
mongorestore --host $1
echo "restored the database"
cd /code
python3 /code/Workers/worker.py $2 rmq $1 $3
