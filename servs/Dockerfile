FROM ubuntu:latest

RUN apt-get update && apt-get -y upgrade && apt-get install -y wget sudo gnupg gnupg2 gnupg1
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
RUN apt-get update && apt-get -y upgrade && DEBIAN_FRONTEND=noninteractive apt-get install -y mongodb-org
RUN apt-get install -y python3-pip && pip3 install flask pymongo requests
RUN mkdir /data && mkdir /data/db



