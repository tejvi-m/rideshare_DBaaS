import pika
from utils import *
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
    def __init__(self, name, host = 'rmq', db = '0.0.0.0'):
        self.host_ip = host
        self.db_ip = db
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host_ip))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rmq'))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count = 1)
        self.dockerClient = docker.APIClient()
        self.name = name
    
    def something(self, children, event):
        print("WATCHING!!    " + str(children))
        try:
            print("EVENT TRIGGERED     ", event)
            num = zk.get("/zoo/count")[0]
            num = int(num.decode("utf-8"))
            print("####count is  ", num)
            if(len(children) < num):
                zk.set("/zoo/count", str.encode(str(len(children))))
                self.spawn_new("slave")
            
        except:
            pass

    def getPID(self):
        print("host: ", socket.gethostname())
        print("hostname: ", self.name)
        pid = self.dockerClient.inspect_container(self.name)['State']['Pid']

        print("WORKER PID", pid)
        return pid

    def start_as_master(self):

        if zk.exists("/zoo/master"):
            print("Node already exists")
        else:
            PID = self.getPID()
            zk.create_async("/zoo/master", str.encode(str(PID)))
            zk.ensure_path("/zoo/slave")
            watcher = ChildrenWatch(zk, '/zoo/slave', func = self.something, send_event = True)
            
        self.channel.queue_declare(queue = "WriteQ")
        self.channel.exchange_declare(exchange = "SyncQ", exchange_type='fanout')

        callback_write = generateWriteCallback(self.channel, self.db_ip)
        self.channel.basic_consume(queue = "WriteQ", on_message_callback = callback_write)
        print("[master] Awaiting requests for writes")

        self.channel.start_consuming()

    def start_as_slave(self):
        
        if zk.exists("/zoo/count"):
            value = zk.get("/zoo/count")[0]
            zk.set("/zoo/count", str.encode(str(int(value.decode("utf-8")) + 1)))
            # print("Node already exists")
        else:
            zk.create("/zoo/count", str.encode(str(1)))

        zk.ensure_path("/zoo/slave")
        nodePath = "/zoo/slave/s" + str(random.randint(0, 1000))
        
        if zk.exists(nodePath):
            print("Node already exists")
        else:
            PID = self.getPID()
            zk.create_async(nodePath, str.encode(str(PID)), ephemeral = True)

        self.channel.queue_declare(queue = "ReadQ")
        self.channel.exchange_declare(exchange = "SyncQ", exchange_type='fanout')

        temp_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        self.channel.queue_bind(exchange='SyncQ', queue = temp_queue)

        callback_read = generateReadCallback(self.db_ip)
        # callback_read = self.spawn_new("slave")
        self.channel.basic_consume(queue = "ReadQ", on_message_callback = callback_read)
        print("[slave] Awaiting RPC requests for reads")

        callback_sync = generateSyncCallback(self.db_ip)
        self.channel.basic_consume(queue = temp_queue, on_message_callback = callback_sync)
        print("[slave] Awaiting Sync requests")

        self.channel.start_consuming()
    
    #this will be useful for spawning when a container fails
    def spawn_new(self, container_type):
        print("[docker] starting a new container")
        #replace the following hash value with the running slave container id, and the key in host config the actual host path.
        act_containers = self.dockerClient.containers()
        for i in range(len(act_containers)):
            if(act_containers[i]['Image'] == 'docker_slave'):
                contID = act_containers[i]['Id']
                print("GOT THE SLAVE'S ID")
                break

        image = self.dockerClient.inspect_container(contID)['Config']['Image']
        networkID = self.dockerClient.inspect_container(contID)['NetworkSettings']['Networks']['docker_default']['NetworkID']
        newCont = self.dockerClient.create_container(image, name="newCont", volumes=['/code/'],
                                            host_config=self.dockerClient.create_host_config(binds={
                                                '/home/thejas/Sem 6/CC/project/CC': {
                                                    'bind': '/code/',
                                                    'mode': 'rw',
                                                },
                                                '/var/run/docker.sock' : {
                                                    'bind': '/var/run/docker.sock',
                                                    'mdde': 'rw'
                                                }
                                            }, privileged=True, restart_policy = {'Name' : 'on-failure'}), command='sh -c "python /code/Workers/worker.py master 0.0.0.0 0.0.0.0 newCont"')
        self.dockerClient.connect_container_to_network(newCont, networkID)
        print(newCont.get('Id'))
        self.dockerClient.start(newCont)
        self.dockerClient.attach(newCont)
        print("[docker] started a new container")
        return "success"

if __name__ == "__main__":

    if len(sys.argv) > 3:

        zk = KazooClient(hosts='zoo:2181')
        zk.start()
        zk.ensure_path("/zoo")

        worker = Worker(sys.argv[4], sys.argv[2], sys.argv[3])

        if sys.argv[1] == "master":
            worker.start_as_master()

        else:
            worker.start_as_slave()

    else:
        print("incorrect number of arguments")
