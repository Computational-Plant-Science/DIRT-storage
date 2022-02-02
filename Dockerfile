LABEL maintainer="Alexander Bucksch"

# RUN apt-get update && \
#     echo 'deb http://downloads.skewed.de/apt/xenial xenial universe' | tee -a  /etc/apt/sources.list && \
#     echo 'deb-src http://downloads.skewed.de/apt/xenial xenial universe' | tee -a  /etc/apt/sources.list && \
COPY . /opt/DIRT-storage

RUN cd /opt/DIRT-storage && \
    pip install -r /opt/DIRT-storage/requirements.txt

ENV LC_ALL=C
ENV DISPLAY=:1
