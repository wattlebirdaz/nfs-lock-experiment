class FileLockBase:
    def acquire(self, blocking: bool) -> bool:
        raise NotImplementedError

    def release(self) -> None:
        raise NotImplementedError
