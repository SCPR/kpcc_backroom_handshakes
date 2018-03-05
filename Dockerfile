FROM python:2.7.14-alpine3.7

RUN apk update && apk add --no-cache \
    make \
    gcc \
    libgcc \
    g++ \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    mariadb-dev \
    mariadb-client \
    mariadb-libs

VOLUME ["/usr/local/lib/python2.7/site-packages"]

WORKDIR /home

