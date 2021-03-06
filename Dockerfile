FROM ubuntu:bionic
LABEL maintainer="Alexander Bucksch"

# RUN apt-get update && \
#     echo 'deb http://downloads.skewed.de/apt/xenial xenial universe' | tee -a  /etc/apt/sources.list && \
#     echo 'deb-src http://downloads.skewed.de/apt/xenial xenial universe' | tee -a  /etc/apt/sources.list && \

#RUN apt-get update && \
#    DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common && \
#    apt-key adv --keyserver keys.openpgp.org --recv-key 7A80C8ED4FCCBE09 && \
#    add-apt-repository "deb [ arch=amd64 ] https://downloads.skewed.de/apt bionic main" && \
#    apt-key adv --keyserver keys.openpgp.org --recv-key 612DEFB798507F25 && \
#    apt-get update && \
#    DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python3-graph-tool python-skimage

COPY . /opt/DIRT-storage

# RUN pacman -S --noconfirm gcc git python-pip && \
RUN cd /opt/DIRT-storage
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y libjpeg-dev && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y zlib1g-dev

RUN pip3 install -r /opt/DIRT-storage/requirements.txt

ENV LC_ALL=C
ENV DISPLAY=:1

CMD python /opt/DIRT-storage/storage.py "$@"
