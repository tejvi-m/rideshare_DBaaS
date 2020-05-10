FROM ubuntu:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir -p /code
RUN apt update && apt -y install docker wget python3-pip gnupg apt-transport-https ca-certificates
COPY ./requirements.txt /code/requirements.txt
RUN pip3 install -r /code/requirements.txt
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list
RUN apt-get update && apt-get -y upgrade && DEBIAN_FRONTEND=noninteractive apt-get install -y mongodb-org
COPY . /code
WORKDIR /code
RUN mkdir /data/db -p

EXPOSE 8000
# 