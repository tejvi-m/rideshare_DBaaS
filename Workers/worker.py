import pika
import DBops.DBops as DB

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='0.0.0.0'))

readChannel = connection.channel()
writeChannel = readChannel

readChannel.queue_declare(queue='ReadQ')
writeChannel.queue_declare(queue='WriteQ')


def on_read_request(ch, method, props, body):

    print("Read Request")
    response = DB.get_data(body)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))

    ch.basic_ack(delivery_tag=method.delivery_tag)


def on_write_request(ch, method, props, body):
    print("Write Request")

    # response = DB.write_data(body)

    # should we not send ack for failed writes?
    # how do we handle failed writes
    ch.basic_ack(delivery_tag=method.delivery_tag)


readChannel.basic_qos(prefetch_count = 1)
readChannel.basic_consume(queue='ReadQ', on_message_callback = on_read_request)
writeChannel.basic_qos(prefetch_count = 1)
writeChannel.basic_consume(queue = 'WriteQ', on_message_callback = on_write_request)


print(" [x] Awaiting RPC requests for reads")
print(" [x] Awaiting requests for writes")
readChannel.start_consuming()
writeChannel.start_consuming()
