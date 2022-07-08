from filelockbase import FileLockBase
import time
import datetime
import os
import errno


class LinkLock1(FileLockBase):
    def __init__(
        self, dir: str, lockfile: str, timeout: int = 300, polltime=10
    ) -> None:
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self._lockfile = dir + lockfile
        self._linkfile = dir + "_link" + str(os.getpid())
        open(self._lockfile, "a").close()  # Create file if it does not exist
        self._timeout = timeout
        self._polltime = polltime

    def lock(self) -> None:
        timeout = self._timeout
        while timeout > 0:
            try:
                os.link(self._lockfile, self._linkfile)
                break
            except OSError as err:
                if err.errno == errno.EEXIST:
                    print("failed")
                    time.sleep(self._polltime)
                    timeout -= self._polltime
                else:
                    raise err
        else:
            raise RuntimeError("Error: timeout")

    def try_lock(self) -> bool:
        try:
            os.link(self._lockfile, self._linkfile)
            return True
        except OSError as err:
            if err.errno == errno.EEXIST:
                return False
            else:
                raise err

    def unlock(self) -> None:
        try:
            os.unlink(self._linkfile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")
