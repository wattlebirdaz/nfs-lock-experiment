from linklock1 import LinkLock1
from linklock2 import LinkLock2
from openlock import OpenLock


def get_lock(config, dir):
    if config == "linklock1":
        return LinkLock1(dir + "/./linklock1/", "lockfile")
    elif config == "linklock2":
        return LinkLock2(dir + "/./linklock2/", "lockfile")
    elif config == "openlock":
        return OpenLock(dir + "/./openlock/", "lockfile")
    else:
        raise RuntimeError("Unknown Lock Type")
