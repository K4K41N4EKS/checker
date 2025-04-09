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
ENV CPR_PATH=/opt/cpr
RUN git clone https://github.com/libcpr/cpr.git ${CPR_PATH}
WORKDIR $CPR_PATH
RUN mkdir build
WORKDIR $CPR_PATH/build
RUN cmake .. && make && make install


ENV DROGON_PATH=/opt/drogon
RUN git clone https://github.com/drogonframework/drogon $DROGON_PATH
WORKDIR $DROGON_PATH
RUN git submodule update --init
RUN mkdir build
WORKDIR $DROGON_PATH/build
RUN cmake .. && make && make install


WORKDIR /usr/src/auth-servis
COPY . .

#CMD cd /usr/src/auth-servis && mkdir build && cd build && cmake .. && \
#cmake --build . && \
#/usr/src/auth-servis/build/auth-servis \ 
#/usr/src/auth-servis/config.example.nossl.json \ 
#/usr/src/auth-servis/servisCfg.example.json

CMD /usr/src/auth-servis/build/auth-servis \ 
/usr/src/auth-servis/config.example.nossl.json \ 
/usr/src/auth-servis/servisCfg.example.json
