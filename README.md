
# Setup NFS

```sh
sudo mkdir -p /data/nfs-storage
docker-compose up -d

# find IP address of docker
ip addr
# docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
#    link/ether 02:42:49:40:46:ee brd ff:ff:ff:ff:ff:ff
#    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
#       valid_lft forever preferred_lft forever

# mount
sudo mount -t nfs 172.17.0.1:/ /mnt

# check
df -h
# 172.17.0.1:/    468G   98G  347G  22% /mnt
```

if it fails to create a docker container because port 2049 is in use, stop nfs kernel service using the following commands and retry again.

```sh
sudo service portmap stop
sudo service nfs-kernel-server stop
```

# Experiment

```sh
python3 lock-experiment.py lock_type dir
```

### lock_type
1. link1 -- [ref](https://stackoverflow.com/a/38239456)
2. link2 -- [ref](https://github.com/sile/optjournal/blob/357cfdf9525010cffb83a2c55b76c3556c26d212/optjournal/_file_system.py#L213-L221)
3. open

## Test

```sh
./test.sh
```
