FROM docker.io/debian:11-slim
RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-requests python3-pandas python3-click git \
    && apt-get clean
COPY . /opt/ths-tools
RUN pip install /opt/ths-tools
