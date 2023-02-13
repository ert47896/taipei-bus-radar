# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /workspace/flask

RUN apt-get update && \
  apt-get install -y build-essential && \
  apt-get clean
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /workspace/flask/requirements.txt

COPY . .

RUN chmod a+x /workspace/flask/startproject.sh
ENTRYPOINT ["/workspace/flask/startproject.sh"]
