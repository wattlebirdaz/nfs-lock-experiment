from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import argparse
from locks import BaseLock, LinkLock
from locks import get_lock_file
from locks import OpenLock
from locks import SymlinkLock
import time
import os
import numpy as np
from tqdm import tqdm

datafile = "./datafile"
config = "symlock"


def Lock(filename) -> BaseLock:
    if config == "symlock":
        return SymlinkLock(filename)
    elif config == "linklock":
        return LinkLock(filename)
    elif config == "openlock":
        return OpenLock(filename)
    else:
        raise RuntimeError("Unknown Lock Type")


def increment_append(id: int):
    lock_obj = Lock(datafile)
    with get_lock_file(lock_obj):
        with open(datafile, "r+") as f:
            data = f.readlines()
            last_line = int(data[-1])
            f.write(str(last_line + 1) + "\n")
            f.flush()
            os.fsync(f.fileno())
    return id


def check(filename, num_executions):
    with open(filename, "r+") as f:
        data = f.readlines()
        last_line = int(data[-1])
        if last_line != num_executions:
            raise RuntimeError()


def execute():
    with open(datafile, "w+") as f:
        f.write("0\n")
        f.flush()
        os.fsync(f.fileno())

    num_executions = 1000

    results = []
    with ProcessPoolExecutor(10) as pool:
        results = pool.map(increment_append, range(num_executions))

    return len(list(results))


def bench():
    elapsed = []
    for i in tqdm(range(5)):
        start = time.time()
        num_executions = execute()
        end = time.time()
        check(datafile, num_executions)
        elapsed.append(end - start)

    score = f"{np.mean(elapsed):7.3f} (+/- {np.std(elapsed):.3f})s"
    print(f"Elapsed: {score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lock_type")
    args = parser.parse_args()
    config = args.lock_type
    print(config)
    bench()
