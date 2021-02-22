FROM python:3.7-alpine3.10
RUN mkdir /app
WORKDIR /app
ADD . /app

# Installing dependency packages
RUN apk update
RUN apk add --virtual .build-deps \
libffi-dev build-base  py3-cryptography py3-gunicorn py3-cffi py3-idna py3-paho-mqtt py3-chardet py3-httplib2 \
py3-six py3-django py3-packaging py3-sqlparse py3-openssl

# Installing necessary libraries
RUN apk add xmlsec-dev postgresql-dev \
jpeg-dev bash

# Installing the requirements for the python project
RUN pip3 install -r requirements.txt

EXPOSE 80

# Delete build dependencies
RUN apk del .build-deps
