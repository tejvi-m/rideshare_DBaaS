import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='0.0.0.0'))

channel = connection.channel()

channel.queue_declare(queue='ReadQ')

def get_data(jsonData):
    return "found"

def on_request(ch, method, props, body):
    # jsonData = json.jsonify(body)
    print("do i get here")
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
