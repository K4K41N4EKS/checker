FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    wget \
    unzip \
    libjsoncpp-dev \
    pkg-config \
    libpqxx-dev \
    openssl \
    libssl-dev \
    uuid-dev \
    zlib1g-dev \
    libmariadb3 \
    libyaml-cpp0.8 && rm -rf /var/lib/apt/lists/*

ENV DROGON_PATH=/opt/drogon
RUN git clone https://github.com/drogonframework/drogon $DROGON_PATH
WORKDIR $DROGON_PATH
RUN git submodule update --init
RUN mkdir build
WORKDIR $DROGON_PATH/build
RUN cmake .. && make && make install

WORKDIR /tmp
RUN git clone https://github.com/dipsomask/auth-servis.git \
    && mv /tmp/auth-servis/deb/auth-servis-0.1.1-Linux.deb /usr/src \
    && mv /tmp/auth-servis/servisCfg.example.json /usr/src \
    && mv /tmp/auth-servis/config.example.nossl.json /usr/src \
    && rm -rf /tmp/auth-servis

CMD cd /usr/src && dpkg -i auth-servis-0.1.1-Linux.deb && chmod +x /usr/bin/auth-servis && cd /usr/bin && /usr/bin/auth-servis /usr/src/config.example.nossl.json /usr/src/servisCfg.example.json
