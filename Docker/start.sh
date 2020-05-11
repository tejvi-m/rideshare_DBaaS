sudo docker system prune --force
sudo docker system prune --volumes -y
sudo docker container prune --force
sudo docker container rm $(sudo docker container ls -aq) --force
sudo docker stop docker_slave_2
sudo docker stop docker_slave_3
sudo docker rm docker_slave_2
sudo docker rm docker_slave_3
sudo docker-compose build
sudo docker-compose up