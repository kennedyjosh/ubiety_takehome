import os
from threading import Lock

class Singleton(type):
    # Must be used as a metaclass
    _instances = {}
    _lock = Lock()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def is_test_env():
    """Returns true if env var is set to testing mode, false otherwise"""
    return "UBIETY_RUN_ENV" in os.environ and os.environ["UBIETY_RUN_ENV"] == "test"
