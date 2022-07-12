import threading
import os
import time
import argparse

from filelockbase import FileLockBase
from linklock1 import LinkLock1
from linklock2 import LinkLock2
from openlock import OpenLock

config: str
dir: str
num_threads: int
thread_lock = threading.Lock()
global_lock = threading.Lock()


def get_lock() -> FileLockBase:
    if config == "linklock1":
        return LinkLock1(dir + "/./linklock1/", "lockfile")
    elif config == "linklock2":
        return LinkLock2(dir + "/./linklock2/", "lockfile")
    elif config == "openlock":
        return OpenLock(dir + "/./openlock/", "lockfile")
    elif config == "threadlock":
        return thread_lock
    else:
        raise RuntimeError("Unknown Lock Type")


def read_and_write_val(filename):
    with open(filename, "r+") as f:
        data = f.readlines()
        last_line = int(data[-1])
        f.write(str(last_line + 1) + "\n")
        f.flush()
        os.fsync(f.fileno())


def increment_append(filename):
    while not global_lock.locked():
        l = get_lock()
        l.acquire(blocking=True)
        read_and_write_val(filename)
        l.release()


def warn_sudo():
    if os.getuid() != 0:
        print("Run this as root if you are using a mount directory")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lock_type")
    parser.add_argument("dir")
    parser.add_argument("num_threads")
    args = parser.parse_args()

    warn_sudo()
    config = args.lock_type
    dir = args.dir
    num_threads = int(args.num_threads)
    seconds = 10
    datafile = config + "_datafile"

    with open(datafile, "w+") as f:
        f.write("0\n")
        f.flush()
        os.fsync(f.fileno())

    threads = []
    for i in range(num_threads):
        threads.append(threading.Thread(target=increment_append, args=[datafile]))

    for i in range(num_threads):
        threads[i].start()

    time.sleep(seconds)
    global_lock.acquire()

    for i in range(num_threads):
        threads[i].join()

    with open(datafile, "r") as f:
        print(
            "Locktype: {}, Threads: {}, Seconds: {}, Locks acquired: {}".format(
                config, num_threads, seconds, int(f.readlines()[-1])
            )
        )
