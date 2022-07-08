from filelockbase import FileLockBase


class LinkLock2(FileLockBase):
    def lock() -> None:
        raise NotImplementedError

    def try_lock() -> bool:
        raise

    def unlock() -> None:
        raise NotImplementedError
