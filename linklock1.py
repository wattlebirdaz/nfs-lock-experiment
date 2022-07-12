from filelockbase import FileLockBase
import time
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
                raise RuntimeError("Error: mkdir")
        self._lockfile = dir + lockfile
        self._linkfile = (
            dir + lockfile + str(os.getpid())
        )  # This file is common among all the threads
        open(self._lockfile, "a").close()  # Create file if it does not exist
        self._timeout = timeout
        self._polltime = polltime

    def acquire(self, blocking=True) -> bool:
        if blocking:
            timeout = self._timeout
            while timeout > 0:
                try:
                    os.link(self._lockfile, self._linkfile)
                    return True
                except OSError as err:
                    if err.errno == errno.EEXIST:
                        time.sleep(self._polltime)
                        timeout -= self._polltime
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
