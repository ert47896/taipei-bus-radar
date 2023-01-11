# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /workspace

RUN apt-get update && \
  apt-get install -y build-essential && \
  apt-get clean
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r /workspace/requirements.txt

COPY . .

RUN chmod +x /workspace/startproject.sh
ENTRYPOINT ["/workspace/startproject.sh"]