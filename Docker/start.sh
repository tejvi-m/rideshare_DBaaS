sudo docker container rm $(sudo docker container ls -aq)
sudo docker stop docker_slave_2
sudo docker stop docker_slave_3
sudo docker rm docker_slave_2
sudo docker rm docker_slave_3
sudo docker-compose build
sudo docker-compose up