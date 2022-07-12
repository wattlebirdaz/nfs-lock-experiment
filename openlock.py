from filelockbase import FileLockBase

import os
import time
import errno


class OpenLock(FileLockBase):
    def __init__(
        self, dir: str, lockfile: str, timeout: int = 300, polltime=10
    ) -> None:
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise RuntimeError("Error: mkdir")
        self._lockfile = dir + lockfile
        self._timeout = timeout
        self._polltime = polltime

    def acquire(self, blocking=True) -> bool:
        if blocking:
            timeout = self._timeout
            while timeout > 0:
                try:
                    open_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                    os.close(os.open(self._lockfile, open_flags))
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
