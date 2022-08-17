import abc
from contextlib import contextmanager
import errno
import json
import os
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional


LOCK_FILE_SUFFIX = ".lock"
RENAME_FILE_SUFFIX = ".rename"


class BaseLock(abc.ABC):
    @abc.abstractmethod
    def acquire(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def release(self) -> None:
        raise NotImplementedError


class LinkLock(BaseLock):
    def __init__(self, filepath: str) -> None:
        self._lock_target_file = filepath
        self._lockfile = filepath + LOCK_FILE_SUFFIX
        self._lockrenamefile = self._lockfile + RENAME_FILE_SUFFIX

    def acquire(self) -> bool:
        while True:
            try:
                os.link(self._lock_target_file, self._lockfile)
                return True
            except OSError as err:
                if err.errno == errno.EEXIST or err.errno == errno.ENOENT:
                    continue
                else:
                    raise err
            except BaseException:
                self.release()
                raise

    def release(self) -> None:
        try:
            os.rename(self._lockfile, self._lockrenamefile)
            os.unlink(self._lockrenamefile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")


class SymlinkLock(BaseLock):
    def __init__(self, filepath: str) -> None:
        self._lock_target_file = filepath
        self._lockfile = filepath + LOCK_FILE_SUFFIX
        self._lockrenamefile = self._lockfile + RENAME_FILE_SUFFIX

    def acquire(self) -> bool:
        while True:
            try:
                os.symlink(self._lock_target_file, self._lockfile)
                return True
            except OSError as err:
                if err.errno == errno.EEXIST or err.errno == errno.ENOENT:
                    continue
                else:
                    raise err
            except BaseException:
                self.release()
                raise

    def release(self) -> None:
        try:
            os.rename(self._lockfile, self._lockrenamefile)
            os.unlink(self._lockrenamefile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")


class OpenLock(BaseLock):
    def __init__(self, filepath: str) -> None:
        self._lockfile = filepath + LOCK_FILE_SUFFIX
        self._lockrenamefile = self._lockfile + RENAME_FILE_SUFFIX

    def acquire(self) -> bool:
        while True:
            try:
                open_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                os.close(os.open(self._lockfile, open_flags))
                return True
            except OSError as err:
                if err.errno == errno.EEXIST:
                    continue
                else:
                    raise err
            except BaseException:
                self.release()
                raise

    def release(self) -> None:
        try:
            os.rename(self._lockfile, self._lockrenamefile)
            os.unlink(self._lockrenamefile)
        except OSError:
            raise RuntimeError("Error: did not possess lock")

@contextmanager
def get_lock_file(lock_obj: BaseLock) -> Iterator[None]:
    lock_obj.acquire()
    try:
        yield
    finally:
        lock_obj.release()