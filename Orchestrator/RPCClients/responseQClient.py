import pika
import uuid

class ResponseQRpcClient(object):

    def __init__(self, queueName):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='0.0.0.0'))
        self.queueName = queueName
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue=queueName)
        # self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=queueName,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='ReadQ',
            properties=pika.BasicProperties(
                reply_to=self.queueName,
                correlation_id=self.corr_id,
            ),
            body=str(data))
        while self.response is None:
            self.connection.process_data_events()
        return self.response
