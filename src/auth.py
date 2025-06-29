from configparser import ConfigParser
from fastapi import Header, HTTPException
from src.util import is_test_env, Singleton
from typing import Annotated

class ApiKey(metaclass=Singleton):
    """Singleton to hold info about API key fetched from config"""
    def __init__(self):
        # Fetch API key, if there is one
        self.API_KEY = None
        _config = ConfigParser()
        _config.read("config.ini")
        if "general" in _config:
            self.API_KEY = _config["general"].get("key", None)

    def get(self):
        return self.API_KEY


def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    """Enforces API key if one is specified in the config"""
    key = ApiKey().get()
    # Raise error if 1. not test env, 2. key is not None, and 3. given key does not match true key
    if not is_test_env() and key is not None and x_api_key != key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )
