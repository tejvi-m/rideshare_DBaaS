FROM python:3.7-slim-stretch

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir -p /code

RUN pip install ipython
RUN pip install pika
RUN pip install kazoo
RUN pip install flask
RUN pip install redis
RUN pip install docker

COPY . /code
WORKDIR /code
