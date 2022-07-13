import os
import errno
import threading
from filelockbase import FileLockBase
import math
import socket


class LinkLock2(FileLockBase):
    def __init__(self, dir: str, lockfile: str):
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise RuntimeError("Error: mkdir")
        self._lockfile = dir + lockfile
        self._lockfile_fd = open(self._lockfile, "a")
        self._linkfile = (
            self._lockfile
            + socket.gethostname()
            + str(os.getpid())
            + str(threading.get_ident())
        )

    def __del__(self):
        self._lockfile_fd.close()

    def acquire(self, blocking=True, timeout=-1) -> bool:
        if blocking:
            if timeout != -1:
                raise RuntimeError("timeout feature not supported")
            timeout_ = math.inf if timeout == -1 else timeout
            while timeout_ > 0:
                try:
                    os.link(self._lockfile, self._linkfile)
                    if os.stat(self._lockfile_fd.fileno()).st_nlink == 2:
                        return True
                    os.unlink(self._linkfile)
                    continue
                except OSError:
                    raise RuntimeError("Error: link, stat, or unlink")
            else:
                raise RuntimeError("Error: timeout")
        else:
            try:
                os.link(self._lockfile, self._linkfile)
                if os.stat(self._lockfile_fd.fileno()).st_nlink == 2:
                    return True
                os.unlink(self._linkfile)
                return False
            except:
                raise RuntimeError("Error in link, stat, or unlink")

    def release(self) -> None:
        try:
            os.unlink(self._linkfile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")
