FROM buildpack-deps:jessie
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV PYTHON_VERSION 3.4.3

RUN apt-get purge -y python.* \
    && apt-get update \
    && apt-get autoremove -y \
    && apt-get install -y \
        binutils \
        libproj-dev \
        gdal-bin \
        swig \
        python3.4-dev \
        libgeos++-dev \
        libgeos-3.4 \
        libgeos-dev \
    && ln -s /usr/bin/python3.4 /usr/bin/python3 \
    &&  ln -s /usr/bin/python3.4 /usr/bin/python \
    && curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements-frozen.txt
