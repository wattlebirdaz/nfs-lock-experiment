import threading
import os
import time
import argparse

from filelockbase import FileLockBase
from linklock1 import LinkLock1
from linklock2 import LinkLock2
from openlock import OpenLock

# thread を num_threads 個立ち上げ、それぞれ共通のファイルに書かれた値を読み込む。
# 各 thread は末尾に書かれた値を m 回インクリメントして、共通ファイルにアペンドする。
# 最終的に末尾に書かれた値が num_threads * m を満たしているか確認

config: str
dir: str
num_threads: int
m: int = 10
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


def read_and_write_val(filename):
    with open(filename, "r+") as f:
        data = f.readlines()
        last_line = int(data[-1])
        f.write(str(last_line + 1) + "\n")
        f.flush()
        os.fsync(f.fileno())


def increment_append(filename):
    for i in range(m):
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

    time.sleep(2)

    for i in range(num_threads):
        threads[i].join()

    with open(datafile, "r") as f:
        assert num_threads * m == int(f.readlines()[-1])
        print("ok")
