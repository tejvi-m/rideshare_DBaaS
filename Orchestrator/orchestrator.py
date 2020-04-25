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

app = Flask(__name__)
zk = KazooClient(hosts='zoo:2181')

client = docker.from_env()

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

def spawn_new(container_type):
    print("[docker] starting a new container")
    client.containers.run('alpine', 'echo hello world && sleep 10',
                            volumes = {'/var/run/docker.sock' : {'bind' : '/var/run/docker.sock', 'mode' : 'rw'}},
                            privileged = True)
                            # detach = True)
    print("[docker] started a new container")

def hello():
    while(1):
        time.sleep(2)
        hits = int(count.get('hits'))
        print("timer ", hits)
        if(hits == 1):
            spawn_new("slave")
        count.set('hits', 0)

if __name__ == '__main__':
    t = threading.Thread(target=hello, daemon=True)
    t.start()
    app.debug=True
    app.run('0.0.0.0', port = 8000, use_reloader=False)
