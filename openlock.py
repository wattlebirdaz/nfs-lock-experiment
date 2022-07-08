from filelockbase import FileLockBase


class OpenLock(FileLockBase):
    def lock() -> None:
        raise NotImplementedError

    def try_lock() -> bool:
        raise

    def unlock() -> None:
        raise NotImplementedError
