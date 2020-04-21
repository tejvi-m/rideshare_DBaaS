import pika
import DBops.DBops as DB
import json

def on_read_request(ch, method, props, body):

    print("[slave] Read Request: ", body)
    response = DB.get_data(body)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))

    ch.basic_ack(delivery_tag=method.delivery_tag)


def generateWriteCallback(channel):
    def callback(ch, method, properties, body):

        print("[master] Write Request", body)

        # response = DB.write_data(body)
        channel.basic_publish(exchange = "SyncQ",
                             routing_key = "",
                             body = body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    return callback



def on_sync_request(ch, method, props, body):
    print("[slave] Sync Request", body)
    # response = DB.write_data(body)


    ch.basic_ack(delivery_tag=method.delivery_tag)
