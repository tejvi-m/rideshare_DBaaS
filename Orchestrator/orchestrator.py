import flask
from flask import Flask, render_template, jsonify, request, abort, make_response, json
import RPCClients.responseQClient as responseClient

import os
from kazoo.client import KazooClient
from kazoo.client import KazooState

import pika

import docker

import json
import threading
import redis
import time
import logging
import subprocess
import socket
app = Flask(__name__)
zk = KazooClient(hosts='zoo:2181')

dockerClient = docker.APIClient()

count = redis.Redis(host = 'redis', port = 6379)
count.set('hits', 0)

connection = pika.BlockingConnection(pika.ConnectionParameters('rmq', 5672))

readChannel = connection.channel()
writeChannel = connection.channel()
readChannel.queue_declare(queue = "ReadQ")
responseRPC = responseClient.ResponseQRpcClient("ResponseQ")

writeChannel.queue_declare(queue = "WriteQ")

zk.start()
zk.delete("/zoo", recursive=True)
zk.ensure_path("/zoo")

containers = []
availableContainers = {"docker_slave_3", "docker_slave_2"}

#this func keeps a continuous watch on the path and its children, so any event on any of them triggers a call to this function.
@zk.ChildrenWatch('/zoo')
def my_func(children):
    print (" $$ZOOKEEPER$$ Children are %s" % children)


def increment():
    count.incr('hits')

@app.route('/api/v1/db/read', methods=["POST"])
def read():
    increment()
    print("[orchestrator] Read Request")
    print(request.get_json())
    dataReturned = responseRPC.call(json.dumps(request.get_json()))
    print(dataReturned)
    return make_response(dataReturned, 200)

@app.route('/api/v1/db/write', methods=["POST"])
def write():

    print("[orchestrator] Write Request")
    writeChannel.basic_publish(exchange = "",
                         routing_key = "WriteQ",
                         body = json.dumps(request.get_json()))
    return("hello", 200)

#this will be used in scalability feature
def spawn_new(container_type):
        global availableContainers
        print("[docker] starting a new container")
        #replace the following hash value with the running slave container id, and the key in host config the actual host path.
        act_containers = dockerClient.containers()
        for i in range(len(act_containers)):
            if(act_containers[i]['Image'] == 'docker_slave'):
                contID = act_containers[i]['Id']
                print("GOT THE SLAVE'S ID")
                break

        image = dockerClient.inspect_container(contID)['Config']['Image']
        networkID = dockerClient.inspect_container(contID)['NetworkSettings']['Networks']['docker_default']['NetworkID']
        newCont = dockerClient.create_container(image, name=availableContainers.pop(), volumes=['/code/'],
                                            host_config=dockerClient.create_host_config(binds={
                                                '/home/tejvi/CC': {
                                                    'bind': '/code/',
                                                    'mode': 'rw',
                                                }
                                            }, privileged=True, restart_policy = {'Name' : 'on-failure'}), command='sh -c "python /code/Workers/worker.py slave 0.0.0.0 0.0.0.0"')
        dockerClient.connect_container_to_network(newCont, networkID)
        print(newCont.get('Id'))
        containers.append(newCont.get('Id'))
        dockerClient.start(newCont)
        dockerClient.attach(newCont)
        print("[docker] started a new container")
        

def setNumSlaves(num):
    current = len(containers) + 1
    if(num > current):
        spawn_new("slave")

def hello():
    while(1):
        time.sleep(10)
        print("currently running containers", containers)
        hits = int(count.get('hits'))
        print("timer ", hits)

        if(hits > 10):
            setNumSlaves(3)
        elif(hits > 5):
            setNumSlaves(2)
        count.set('hits', 0)
        

if __name__ == '__main__':
    t = threading.Thread(target=hello)
    t.start()
    app.debug=True
    app.run('0.0.0.0', port = 8000, use_reloader=False)
