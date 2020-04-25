import flask
from flask import Flask, render_template, jsonify, request, abort, make_response, json
import RPCClients.responseQClient as responseClient

import os
from kazoo.client import KazooClient
from kazoo.client import KazooState

import pika
import json
import logging


app = Flask(__name__)
zk = KazooClient(hosts='zoo:2181')

connection = pika.BlockingConnection(pika.ConnectionParameters('rmq'))

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

@app.route('/api/v1/db/read', methods=["POST"])
def read():
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


if __name__ == '__main__':


    app.debug=True
    app.run('0.0.0.0', port = 8000)