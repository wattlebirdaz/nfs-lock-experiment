FROM debian:jessie
LABEL maintainer="wattlebirdaz"

RUN set -eux && \
    apt-get upgrade && \
    apt-get update && \
    apt-get install -y git nfs-common python3 && \
    git clone https://github.com/wattlebirdaz/nfs-lock-experiment.git
    
CMD set -eux && \
    tail -F anything
