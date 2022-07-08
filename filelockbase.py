class FileLockBase:
    def lock() -> None:
        raise NotImplementedError

    def try_lock() -> bool:
        raise

    def unlock() -> None:
        raise NotImplementedError
