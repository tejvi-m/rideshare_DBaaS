import pika
from utils import *
from DBops.DBops import DB
import sys
import os
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.recipe.watchers import ChildrenWatch
import subprocess
import docker
import socket
import random

class Worker:
    """
    setup all the necessary connections to servers based on the ips sent
    database is setup only when the flag is set
    flag is set only when the database needs to be populated with initial state
    """
    def __init__(self, name, host = 'rmq', db = '0.0.0.0', setup = 0):
        self.host_ip = host
        self.db_ip = db
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host_ip))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rmq', heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count = 1)
        self.dockerClient = docker.APIClient()
        self.name = name

        if(setup):
            DB(db).setup()


    """
    Using name of the container (sent by the orchestrator) with docker inspect to get the PID of the container
    """
    def getPID(self):
        print("host: ", socket.gethostname())
        print("hostname: ", self.name)
        pid = self.dockerClient.inspect_container(socket.gethostname())['State']['Pid']

        print("WORKER PID", pid)
        return pid

    """
        starts the worker as a master.
        WriteQ and SyncQ are declared, with callbacks being generated using currying so that an extra parameter(db ip) can be sent

    """
    def start_as_master(self):

        # check if the master container's znode is already present in the znode tree
        if zk.exists("/zoo/master"):
            print("Node already exists")
        else:
            # if not present, add the znode with the container's PID,
            #, this need not be ephemeral as the master is assumed never to crash
            PID = self.getPID()
            zk.create_async("/zoo/master", str.encode(str(PID)))

        self.channel.queue_declare(queue = "WriteQ")
        self.channel.exchange_declare(exchange = "SyncQ", exchange_type='fanout')

        callback_write = generateWriteCallback(self.channel, self.db_ip)
        self.channel.basic_consume(queue = "WriteQ", on_message_callback = callback_write)
        print("[master] Awaiting requests for writes")

        self.channel.start_consuming()

    """
        starts the worker as a slave.
        ReadQ, SyncQ and temporary queue for the RPC are setup on the same channel, on which the start_consuming is called.

        callbacks are generated using currying to send extra paremeters (the db IP)
    """
    def start_as_slave(self):
        #check if the node existsm to keep the count of the slave contianers
        if zk.exists("/zoo/count"):
            # if present increment the value of the slave containers
            value = zk.get("/zoo/count")[0]
            zk.set("/zoo/count", str.encode(str(int(value.decode("utf-8")) + 1)))
            # print("Node already exists")
        else:
            #intialise the number of slaves to 1
            zk.create("/zoo/count", str.encode(str(1)))

        #ensure that the path zoo/slave exists
        # create a new path for the new slave container's znode to be added
        zk.ensure_path("/zoo/slave")
        nodePath = "/zoo/slave/s" + str(random.randint(0, 1000))

        #check if the node already exists
        if zk.exists(nodePath):
            print("Node already exists")
        else:
            # add an ephemeral znode with the container's pid as its metadata
            PID = self.getPID()
            zk.create_async(nodePath, str.encode(str(PID)), ephemeral = True)

        self.channel.queue_declare(queue = "ReadQ")
        self.channel.exchange_declare(exchange = "SyncQ", exchange_type='fanout')

        temp_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        self.channel.queue_bind(exchange='SyncQ', queue = temp_queue)

        callback_read = generateReadCallback(self.db_ip)

        self.channel.basic_consume(queue = "ReadQ", on_message_callback = callback_read)
        print("[slave] Awaiting RPC requests for reads")

        callback_sync = generateSyncCallback(self.db_ip)
        self.channel.basic_consume(queue = temp_queue, on_message_callback = callback_sync)
        print("[slave] Awaiting Sync requests")

        self.channel.start_consuming()


"""
Command line arguments for rmq and db ips along with a flag to setup the database.
Another command line argument to start as master or as slave.
"""
if __name__ == "__main__":

    print("starting new worker")
    if len(sys.argv) > 3:

        zk = KazooClient(hosts='zoo:2181')
        zk.start()
        zk.ensure_path("/zoo")

        worker = Worker(sys.argv[4], sys.argv[2], sys.argv[3], int(sys.argv[5]))

        if sys.argv[1] == "master":
            worker.start_as_master()

        else:
            worker.start_as_slave()

    else:
        print("incorrect number of arguments")
