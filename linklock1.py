from filelockbase import FileLockBase
import time
import os
import errno
import math


class LinkLock1(FileLockBase):
    def __init__(self, dir: str, lockfile: str) -> None:
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise RuntimeError("Error: mkdir")
        self._lockfile = dir + lockfile
        self._linkfile = (
            dir + lockfile + str(os.getpid())
        )  # This file is common among all the threads
        open(self._lockfile, "a").close()  # Create file if it does not exist

    def acquire(self, blocking=True, timeout=-1) -> bool:
        if blocking:
            if timeout != -1:
                raise RuntimeError("timeout feature not supported")
            timeout_ = math.inf if timeout == -1 else timeout
            while timeout_ > 0:
                try:
                    os.link(self._lockfile, self._linkfile)
                    return True
                except OSError as err:
                    if err.errno == errno.EEXIST:
                        continue
                    else:
                        raise err
            else:
                raise RuntimeError("Error: timeout")
        else:
            try:
                os.link(self._lockfile, self._linkfile)
                return True
            except OSError as err:
                if err.errno == errno.EEXIST:
                    return False
                else:
                    raise err

    def release(self) -> None:
        try:
            os.unlink(self._linkfile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")
