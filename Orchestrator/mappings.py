
containerPIDs = dict()
containerIPs = {'docker_slave_1':'172.16.238.02',
 'docker_slave_2':'172.16.238.03',
'docker_slave_3':'172.16.238.04'
}

def genContainerIPs():
    slave_template = "docker_container_slave_"
    IP_template = "172.16.238."
    for i in range (4, 201):
        slave = slave_template + str(i)
        ip = IP_template + str(i + 6)

        containerIPs.update({slave:ip})


genContainerIPs()

# print(containerIPs)

availableContainers = set(containerIPs.keys()) - {'docker_slave_1'}
# print(availableContainers)