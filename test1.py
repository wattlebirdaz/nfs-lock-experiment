import threading
import os
import time
import argparse

from filelockbase import FileLockBase
from linklock1 import LinkLock1
from linklock2 import LinkLock2
from openlock import OpenLock

# thread 2つ立ち上げて、片方が lock を作成して 10s sleep する
# その間に片方が link の作成に失敗するかどうかを確認

config: str
dir: str
thread_lock = threading.Lock()


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


def lock_and_sleep() -> None:
    l = get_lock()
    l.acquire()
    time.sleep(1)
    l.release()


def try_acquire() -> None:
    l = get_lock()
    for i in range(10):
        if l.acquire(blocking=False):
            raise RuntimeError("Unexpected lock acquired")


def warn_sudo():
    if os.getuid() != 0:
        print("Run this as root if you are using a mount directory")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lock_type")
    parser.add_argument("dir")
    args = parser.parse_args()
    warn_sudo()
    config = args.lock_type
    dir = args.dir
    l = get_lock()
    l.acquire()
    t1 = threading.Thread(target=try_acquire)
    t1.start()
    time.sleep(1)
    t1.join()
    l.release()
    print("ok")
