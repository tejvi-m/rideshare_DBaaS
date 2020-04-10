import pika
import json
import pymongo
from flask import jsonify

mClient = pymongo.MongoClient("0.0.0.0:27017")
db = mClient["RideDB"]

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='0.0.0.0'))

channel = connection.channel()


channel.queue_declare(queue='ReadQ')

def get_data(jsonData):
        req = json.loads(jsonData)
        collection = db[req["collection"]]

        if req["operation"] == "getNewRideID":
                try:
                    newRide = collection.find_one()["maxRideID"]
                    return str(newRide + 1)
                except:
                    return "-1"

        else:
            match = req["data"]
            selectFields = req["selectFields"]

            try:
                # not returning _id, plus having _id has problems with jsonify
                records = collection.find(match, selectFields)

                matches = {}
                c = 0

                for x in records:
                    matches.update({c: x})
                    c += 1

                if c == 0:
                     return ""

                return json.dumps(jsonify(matches))
            except:
                return ""

def on_request(ch, method, props, body):
    # jsonData = json.jsonify(body)
    # print("do i get here")
    response = get_data(body)


    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='ReadQ', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
