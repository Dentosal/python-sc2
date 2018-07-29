# FROM burnysc2/python-sc2-docker
FROM ubuntu:16.04
USER root
WORKDIR /root/
RUN apt-get update --assume-yes --quiet=2
# RUN apt-get build-dep --assume-yes --no-install-recommends --no-show-upgraded --quiet=2 python-pygame
RUN apt-get install --assume-yes --no-install-recommends --no-show-upgraded --quiet=2 \
    net-tools \
    build-essential \
    clang \
    cmake \
    curl  \
    git  \
    htop  \
    libidn11  \
    libz-dev \
    libssl-dev \
    make \
    software-properties-common \
    unzip \
    vim \
    wget
# Install python 3.6 with pip
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update --assume-yes --quiet=2
RUN apt-get install --assume-yes --no-install-recommends --no-show-upgraded --quiet=2 \
    python3.6 \
    python3-setuptools \
    python3-pip
RUN apt-get update
RUN apt-get install wget unzip git tar gzip -y
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv




# Copy python-sc2 directory to docker image
ADD $TRAVIS_BUILD_DIR /root/python-sc2
# ADD python-sc2 /root/python-sc2

# Copy run_tests bash script - since we 'CD'ed into the test folder, we can just copy the file from here
ADD run_tests.sh /root/run_tests.sh

# RUN /root/run_tests.sh

# docker rm mytest
# docker run --name mytest ubuntu echo one
# docker start -i mytest
# docker cp run_tests.sh mytest:/root/
# docker cp python-sc2/. mytest:/root/python-sc2
# docker exec mytest bash /root/run_tests.sh