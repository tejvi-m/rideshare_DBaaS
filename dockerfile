FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev


RUN sudo apt-get install mongodb
RUN pip install -r pymongo flask 

ENTRYPOINT [ "python" ]

CMD [ "UserManagementAPIs.py" ]
