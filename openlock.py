from filelockbase import FileLockBase

import os
import time
import errno
import math

class OpenLock(FileLockBase):
    def __init__(
        self, dir: str, lockfile: str) -> None:
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise RuntimeError("Error: mkdir")
        self._lockfile = dir + lockfile

    def acquire(self, blocking=True, timeout = -1) -> bool:
        if blocking:
            if timeout != -1:
                raise RuntimeError("timeout feature not supported")
            timeout_ = math.inf if timeout == -1 else timeout
            while timeout_ > 0:
                try:
                    open_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                    os.close(os.open(self._lockfile, open_flags))
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
                open_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                os.close(os.open(self._lockfile, open_flags))
                return True
            except OSError as err:
                if err.errno == errno.EEXIST:
                    return False
                else:
                    raise err

    def release(self) -> None:
        try:
            os.unlink(self._lockfile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")
