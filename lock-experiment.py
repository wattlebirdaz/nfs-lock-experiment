import threading
import os
import time

from filelockbase import FileLockBase
from linklock1 import LinkLock1
from linklock2 import LinkLock2
from openlock import OpenLock


config: str


def get_lock() -> FileLockBase:
    if config == "link1":
        return LinkLock1("/mnt/linklock1/", "lockfile")
    elif config == "link2":
        return LinkLock2("/mnt/linklock2/", "lockfile")
    elif config == "open":
        return OpenLock
    else:
        raise RuntimeError


def lock_and_sleep() -> None:
    l = get_lock()
    l.lock()
    time.sleep(1)
    l.unlock()


def try_lock() -> None:
    l = get_lock()
    for i in range(10):
        if l.try_lock():
            raise RuntimeError("Unexpected lock acquired")
        else:
            print("success")


def check_sudo():
    if os.getuid() != 0:
        print("Run this as root if you are using a mount directory")


if __name__ == "__main__":
    check_sudo()
    config = "link1"
    l = get_lock()
    l.lock()
    t1 = threading.Thread(target=try_lock)
    t1.start()
    time.sleep(1)
    t1.join()
    l.unlock()
