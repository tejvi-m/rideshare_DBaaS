# first arg: ip address to bind mongo to, as well as to be used in the workers. 
# second arg: type of container.
# third arg: name of ctr
mongod --fork --logpath /var/log/mongodb.log --bind_ip $1
sleep 25
python3 /code/Workers/worker.py $2 rmq $1 $3 $4
