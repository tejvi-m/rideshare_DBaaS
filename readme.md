# Cloud Computing Project

This repository contains the source code for the Cloud computing course projects and assignments.

Team: CC_0119_01296_1421_1575



Build1 - Checking the APIs on an assumed schema of the table. Multivalued attributes not included

## Setting up the instances
Three AWS instances have been used for the project, along with a load balancer. 
Each of the instances uses an nginx reverse proxy setup.

## Setting up the Load balancer
1. Create target groups for the User and Rides microservice instances in the AWS Console by adding the two in the registered targets.
2. Create an Application Load Balancer in the console and set rides target group as the default route of the requests on port 80. Make sure that the availability zones is same as that of the instances.
3. Add the path based routing rules in the listeners tab in the console:
    * If route is /api/v1/users* then
        * forward to User target group.
    * else
        * forward to Rides target group.

### Reverse proxy setup:

installing the necessary packages:
```
sudo apt-get update 
sudo apt install nginx python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
```
install nginx, and stop apache2 (or other similar servers) if they're running.

Add the following file as ```/etc/nginx/sites-available/reverse-proxy.conf``` :
```
server {
    listen 80;
    location / {
        proxy_pass http://0.0.0.0:8080;
    }
}
```

create a symbolic link:

```ln -s /etc/nginx/sites-available/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf```

disable default virtual host:
```unlink /etc/nginx/sites-enabled/default```

restart nginx:
```sudo systemctl restart nginx```

### Running the containers
For each of the three instances, run the following:
``` 
sudo apt-get update
sudo apt-get install docker docker-compose
```

place the source code (or clone the repo) in a directory, and cd into it.

Within the source code, modify the ```config.json``` files in the  ```Users``` and ```Rides``` directories with the dns or ip of the instances being used.

#### Rides containers:
``` 
cd Rides
sudo bash start.sh
```

#### Users containers:
```
cd Users
sudo bash start.sh
```

#### DBaas containers:
```
cd Docker
sudo bash start.sh
```


You should now be able to send requests to the load balancer and get the response back.

