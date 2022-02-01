LABEL maintainer="Alexander Bucksch"

# RUN apt-get update && \
#     echo 'deb http://downloads.skewed.de/apt/xenial xenial universe' | tee -a  /etc/apt/sources.list && \
#     echo 'deb-src http://downloads.skewed.de/apt/xenial xenial universe' | tee -a  /etc/apt/sources.list && \
COPY . /opt/DIRT_storage

RUN cd /opt/DIRT_storage
    pip install -r /opt/DIRT_storage/requirements.txt

ENV LC_ALL=C
ENV DISPLAY=:1

CMD python /opt/DIRT_storage/storage.py "$@"
