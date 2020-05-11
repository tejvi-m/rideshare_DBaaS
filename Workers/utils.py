import pika
from DBops.DBops import DB
import json

def generateReadCallback(db_ip):
    def callback(ch, method, props, body):

        print("[slave] Read Request: ", body)
        response = DB(db_ip).get_data(body)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                         body= response[0] + ";;" + str(response[1]))

        ch.basic_ack(delivery_tag=method.delivery_tag)
    return callback


def generateWriteCallback(channel, db_ip):
    def callback(ch, method, properties, body):

        print("[master] Write Request", body)

        response = DB(db_ip).write_data(body)

        channel.basic_publish(exchange = "SyncQ",
                             routing_key = "",
                             body = body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    return callback



def generateSyncCallback(db_ip):
    def callback(ch, method, props, body):
        print("[slave] Sync Request", body)
        response = DB(db_ip).write_data(body)
        # response = "synchelp"

        ch.basic_ack(delivery_tag=method.delivery_tag)
    return callback
