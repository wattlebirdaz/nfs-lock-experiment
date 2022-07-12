import os
import errno
import time
import threading
from filelockbase import FileLockBase


class LinkLock2(FileLockBase):
    def __init__(self, dir: str, lockfile: str, timeout: int = 300, polltime: int = 10):
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise RuntimeError("Error: mkdir")
        self._lockfile = dir + lockfile
        self._lockfile_fd = open(self._lockfile, "a")
        self._linkfile = self._lockfile + str(threading.get_ident())
        self._timeout = timeout
        self._polltime = polltime

    def __del__(self):
        self._lockfile_fd.close()

    def acquire(self, blocking=True) -> bool:
        if blocking:
            timeout = self._timeout
            while timeout > 0:
                try:
                    os.link(self._lockfile, self._linkfile)
                    if os.stat(self._lockfile_fd.fileno()).st_nlink == 2:
                        return True
                    os.unlink(self._linkfile)
                    time.sleep(self._polltime)
                    timeout = -self._polltime
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
