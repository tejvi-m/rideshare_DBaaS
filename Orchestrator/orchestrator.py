import flask
from flask import Flask, render_template, jsonify, request, abort, make_response, json
import RPCClients.responseQClient as responseClient
import pika
import json

app = Flask(__name__)

connection = pika.BlockingConnection(pika.ConnectionParameters('0.0.0.0', 5672))

readChannel = connection.channel()
writeChannel = connection.channel()

readChannel.queue_declare(queue = "ReadQ")
responseRPC = responseClient.ResponseQRpcClient("ResponseQ")

writeChannel.queue_declare(queue = "WriteQ")

@app.route('/api/v1/db/read', methods=["POST"])
def read():
    print("got a read")
    dataReturned = responseRPC.call(json.dumps(request.get_json()))
    return make_response(dataReturned, 200)

@app.route('/api/v1/db/write', methods=["POST"])
def write():
    writeChannel.basic_publish(exchange = "",
                         routing_key = "WriteQ",
                         body = json.dumps(request.get_json()))
    print("sent message")
    return("hello", 200)



if __name__ == '__main__':
	app.debug=True
	app.run('0.0.0.0', port = 8000)
