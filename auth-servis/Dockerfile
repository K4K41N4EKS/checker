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


# Установка библиотеки cpr
WORKDIR /tmp
RUN git clone https://github.com/libcpr/cpr.git
WORKDIR /tmp/cpr
RUN mkdir build
WORKDIR /tmp/cpr/build
RUN cmake .. && make && make install


ENV DROGON_PATH=/opt/drogon
RUN git clone https://github.com/drogonframework/drogon $DROGON_PATH
WORKDIR $DROGON_PATH
RUN git submodule update --init
RUN mkdir build
WORKDIR $DROGON_PATH/build
RUN cmake .. && make && make install

COPY . .
WORKDIR /usr/src/auth-servis

CMD cd /usr/src/auth-servis && mkdir build && cd build && \
 ./run && /usr/src/auth-servis \
 /usr/src/auth-servis/config.example.nossl.json \
 /usr/src/auth-servis/servisCfg.example.json
