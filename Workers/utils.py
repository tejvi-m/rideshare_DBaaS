import pika
import DBops.DBops as DB
import json

def on_read_request(ch, method, props, body):

    print("Read Request")
    # response = DB.get_data(body)
    # response = jsonify({1:"death will come for us all"})
    response = json.loads(json.dumps({1:"death"}))
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    print("did i die")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("did i die")


def on_write_request(ch, method, props, body):
    print("Write Request")

    # response = DB.write_data(body)

    # should we not send ack for failed writes?
    # how do we handle failed writes
    ch.basic_ack(delivery_tag=method.delivery_tag)

def on_sync_request(ch, method, props, body):
    print("Sync Request")
    ch.basic_ack(delivery_tag=method.delivery_tag)
