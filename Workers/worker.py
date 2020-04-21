import pika
from utils import *
import sys



class Worker:
    def __init__(self, host = '0.0.0.0', db = '0.0.0.0'):
        self.host_ip = host
        self.db_ip = db
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host_ip))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count = 1)

    def start_as_master(self):
        self.channel.queue_declare(queue = "WriteQ")
        self.channel.exchange_declare(exchange = "SyncQ", exchange_type='fanout')

        callback_write = generateWriteCallback(self.channel, self.db_ip)
        self.channel.basic_consume(queue = "WriteQ", on_message_callback = callback_write)
        print("[master] Awaiting requests for writes")

        self.channel.start_consuming()

    def start_as_slave(self):
        self.channel.queue_declare(queue = "ReadQ")
        self.channel.exchange_declare(exchange = "SyncQ", exchange_type='fanout')

        temp_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        self.channel.queue_bind(exchange='SyncQ', queue = temp_queue)

        self.channel.basic_consume(queue = "ReadQ", on_message_callback = on_read_request)
        print("[slave] Awaiting RPC requests for reads")

        self.channel.basic_consume(queue = temp_queue, on_message_callback = on_sync_request)
        print("[slave] Awaiting Sync requests")

        self.channel.start_consuming()

if __name__ == "__main__":

    if len(sys.argv) > 3:
        worker = Worker(sys.argv[2], sys.argv[3])

        if sys.argv[1] == "master":
            worker.start_as_master()

        else:
            worker.start_as_slave()

    else:
        print("incorrect number of arguments")
