import flask
from flask import Flask, render_template, jsonify, request, abort, make_response, json
import RPCClients.responseQClient as responseClient
from kazoo.recipe.watchers import ChildrenWatch

import os
from kazoo.client import KazooClient
from kazoo.client import KazooState

import pika

import docker

import sys
import json
import threading
import redis
import time
import logging
import subprocess
import socket
from datetime import datetime

from mappings import *

containers = []
app = Flask(__name__)
zk = KazooClient(hosts='zoo:2181')

dockerClient = docker.APIClient()

count = redis.Redis(host = 'redis', port = 6379, connection_pool=None, retry_on_timeout=True)
count.set('hits', 0)
count.set('prevHits', 0)
count.set('timer', 0)

connection = pika.BlockingConnection(pika.ConnectionParameters('rmq', 5672, heartbeat=0))

readChannel = connection.channel()
writeChannel = connection.channel()
readChannel.queue_declare(queue = "ReadQ")
responseRPC = responseClient.ResponseQRpcClient("ResponseQ")

writeChannel.queue_declare(queue = "WriteQ")

#start the zk client and delete any znode tree which was present from the previous executions
# and ensure the path for future zk operations
zk.start()
zk.delete("/zoo", recursive=True)
zk.ensure_path("/zoo")



#this func keeps a continuous watch on the path and its children, so any event on any of them triggers a call to this function.
@zk.ChildrenWatch('/zoo', send_event = True)
def my_func(children, event):
    print (" $$ZOOKEEPER$$ Children are %s" % children)
    try:
        print ("EVENT TRIGGERED is %s" % event.type)
    except:
        print("ERROR: ", sys.exc_info())
        pass


"""
increment hits counter
"""
def increment():
    count.incr('hits')




"""
a daemon thread that checks for the number of hits every 2 minutes.
has a call to setNumSLaves which takes current number of required containers as an argument

prev hits counter is also set to check for hits during a crashSlave

"""
def start_timer():
    while(1):
        time.sleep(120)
        print("currently running containers", containers)
        hits = int(count.get('hits'))
        print("timer ", hits)
        print(containerPIDs)

        setNumSlaves(max((hits - 1), 0) // 20 + 1)
        # if(hits > 40):
        #     setNumSlaves(3)
        # elif(hits > 20):
        #     setNumSlaves(2)
        # else:
        #     setNumSlaves(1)

        count.set('prevHits', hits)
        count.set('hits', 0)


"""
Read API
Uses RPC calls to get the relevant data
"""

@app.route('/api/v1/db/read', methods=["POST"])
def read():
    timer = int(count.get('timer'))
    if not timer:
        timerThread = threading.Thread(target=start_timer)
        timerThread.start()
    count.set('timer', 1)
    increment()
    print("[orchestrator] Read Request")
    print(request.get_json())
    dataReturned = responseRPC.call(json.dumps(request.get_json()))
    dataReturned = dataReturned.decode()
    d = json.loads(dataReturned.split(';;')[0])
    i = int(dataReturned.split(';;')[1])
    if type(d) is int or type(d) is float:
        d = str(d)
    return make_response(d, i)


"""
Write API
publishes to writeQ to write the given data to db
delay added to ensure syncs with slaves complete
"""
@app.route('/api/v1/db/write', methods=["POST"])
def write():

    print("[orchestrator] Write Request")
    print(request)
    writeChannel.basic_publish(exchange = "",
                         routing_key = "WriteQ",
                         body = json.dumps(request.get_json()))

    time.sleep(1)
    return("", 200)


"""
Sends a request to master to clear db on WriteQ
"""
@app.route('/api/v1/db/clear', methods=["POST"])
def clear():
    print("[Orchestrator] Request to clear database")
    request = jsonify(json.loads('{"operation":"clear"}'))
    writeChannel.basic_publish(exchange = "",
                         routing_key = "WriteQ",
                         body = json.dumps(request.get_json()))
    return("", 200)

"""
Master is assumed to not fail
"""
@app.route('/api/v1/crash/master')
def crashMaster():
    pass


"""
function to stop a container.
other bookkeeping is done based on whether its a crash or scale in event
"""
def stop_container(toRemove, isCrash):

    if isCrash:
        containers.remove(toRemove)

    name = ""

    for key in containerPIDs.keys():

            if toRemove == containerPIDs[key][1]:
                    availableContainers.add(key)
                    del containerPIDs[key]

                    break

    dockerClient.stop(toRemove)
    dockerClient.remove_container(toRemove)
    print("[orchestrator] stopped a container. currently running:", containers)


"""
Crashes the container with the highest PID
"""
@app.route('/api/v1/crash/slave', methods=["POST", "GET"])
def crashSlave():
    maxPid = 0
    toRemove = 0

    for key in containerPIDs.keys():
        if maxPid < containerPIDs[key][0]:
            maxPid = containerPIDs[key][0]
            toRemove = containerPIDs[key][1]

    stop_container(toRemove, 1)

    return "OK"


"""
Returns  a list of workers as a sorted list of Container PIDs
"""
@app.route('/api/v1/worker/list')
def listWorkers():
    workers = []

    for key in containerPIDs.keys():
        workers.append(containerPIDs[key][0])

    workers.sort()

    return jsonify(workers)


def childrenHandler(children, event):
        print("WATCHING!!    " + str(children))
        global containers
        if(len(containers) == 0):
            # add the og slave container
            print("[zookeeper] need to update the newly spawned slave data")
            # this is only happens when the orch first starts, because every other time the length of containers array is 0,
            # there will not be a running image of "docker_slave"
            act_containers = dockerClient.containers()
            # print("act continares: ", act_containers)
            for i in range(len(act_containers)):
                if(act_containers[i]['Image'] == 'docker_slave'):

                    id = act_containers[i]['Id']
                    containers.append(id)
                    print("added the first container to the containers list")

                    pid = dockerClient.inspect_container('docker_slave_1')['State']['Pid']
                    containerPIDs.update({"docker_slave_1" : (pid, id)})

        try:
            print("EVENT TRIGGERED     ", event)
            hits = int(count.get('prevHits'))
            # num represents how many containers should be running in the present frame of request counts.
            num = max((hits - 1), 0) // 20 + 1
            setNumSlaves(max((hits - 1), 0) // 20 + 1)
            #if the number of running containers is less than the num value then a delete event has occured, so spawn new slaves.
            if(len(containers) < num):
                print("[Zookeeper] Not enough children: unexpected crash")
                for i in range(num - len(containers)):
                    spawn_new("slave")

        except Exception as e:
            print("[Zookeeper] something died: ", e)

def watchChildren():
    try:
        print("ANOTHER WATCHER")
        # this zk watcher is used to watch the slave nodes,
        # if one of the slaves crash the event would be captured by this watcher and a new slave will be spawned if necessary.
        zk.ensure_path("/zoo/slave")
        watcher = ChildrenWatch(zk, '/zoo/slave', func = childrenHandler, send_event = True)


    except:
        print("ERROR 1:", sys.exc_info())


"""
Spawns a new container using the orchestrator image.
Docker low level API is used
Database dump is performed on the master node and restored on to the worker
"""
def spawn_new(container_type):
        global availableContainers
        ctime = time.time()
        # cTime = str(datetime.time())
        # print("dumping database")
        # command = os.popen("cd /code/ && mongodump --host 172.16.238.05")
        # print(command)
        # print("dumped the database")
        print("[docker] starting a new container")
        #replace the following hash value with the running slave container id, and the key in host config the actual host path.
        act_containers = dockerClient.containers()
        for i in range(len(act_containers)):
            # using the image of docker orchestrator since thats the only component that should not fail
            if(act_containers[i]['Image'] == 'docker_orchestrator'):
                contID = act_containers[i]['Id']
                print("GOT THE SLAVE'S ID")
                break
        # getting the image of the orchestrator container
        image = dockerClient.inspect_container(contID)['Config']['Image']
        # getting the network id where the rmq and zk are running
        networkID = dockerClient.inspect_container(contID)['NetworkSettings']['Networks']['docker_microservice_nets']['NetworkID']
        newContainerName = availableContainers.pop()
        # create a container using the image, network information along with properly mounting hte docker daemon and the source code folder
        newCont = dockerClient.create_container(image, name=newContainerName, volumes=['/code/'],
                                            host_config=dockerClient.create_host_config(binds={
                                                '/home/ubuntu/CC': {
                                                    'bind': '/code/',
                                                    'mode': 'rw',
                                                },
                                                '/var/run/docker.sock' : {
                                                    'bind': '/var/run/docker.sock',
                                                    'mdde': 'rw'
                                                }
                                            }, privileged=True, restart_policy = {'Name' : 'on-failure'}),
                                             command='sh -c "bash /code/Docker/setupNewWorker.sh ' +  containerIPs[newContainerName] + ' slave ' + newContainerName + ' 0"')
        #adding the newly spawned container to the existing network, making sure that newly spawned container communicates with same servers as the others.
        dockerClient.connect_container_to_network(newCont, networkID, ipv4_address = containerIPs[newContainerName])
        id = newCont.get('Id')
        print(newCont.get('Id'))
        containers.append(newCont.get('Id'))
        dockerClient.start(newCont)
        dockerClient.attach(newCont)
        pid = dockerClient.inspect_container(newContainerName)['State']['Pid']
        print("new containers pid is: ", pid)
        #update the running containers mapping with the pid and container id info
        containerPIDs.update({newContainerName: (pid, id)})
        nTime = time.time()
        print("[docker] started a new container. took ", nTime - ctime, " seconds to spawn")


"""
Sets the number of slaves that need to be running currently
"""
def setNumSlaves(num):
    current = len(containers)
    if(num > current):
        for i in range(num - current):
            spawn_new("slave")
    elif(num < current):
        for i in range(current - num):
            toRemove = containers.pop()
            stop_container(toRemove, 0)



"""
Node watching is spawned on a different thread
"""
if __name__ == '__main__':
    watchChildNodes = threading.Thread(target=watchChildren)
    watchChildNodes.start()
    app.debug=True
    app.run('0.0.0.0', port = 80, use_reloader=False, threaded=True)
