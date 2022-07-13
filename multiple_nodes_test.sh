#!/bin/bash
set -euxvo pipefail

docker build -t "nfs-client" .
docker-compose up -d

echo "Run the following to enter nfs client"
echo "docker exec -it nfs-client1 /bin/bash"
echo "docker exec -it nfs-client2 /bin/bash"

echo "Run the following to mount nfs"
echo "mount -t nfs 172.30.0.11:/ /mnt"
echo "for checking: df -h"