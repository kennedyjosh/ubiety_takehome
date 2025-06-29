from configparser import ConfigParser
from contextlib import contextmanager
from sqlalchemy import Boolean, create_engine, Column, DateTime, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from src.util import is_test_env, Singleton

# Base class that models will inherit from to create DB tables
Base = declarative_base()

class StatusModel(Base):
    """Class representing the status model in the database"""

    __tablename__ = "status"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime)
    battery_level = Column(Integer)
    rssi = Column(Integer)
    online = Column(Boolean)

class Database(metaclass=Singleton):
    """A singleton class that manages the database connection"""

    def __init__(self):
        # Get database url
        if is_test_env():
            # Use a separate db for testing
            # If you change this name, update the Makefile
            self.DATABASE_URL = "sqlite:///./iot_test.db"
        else:
            # Load settings from config file
            _config = ConfigParser(allow_no_value=True)
            _config.read("config.ini")
            fallback = "sqlite:///./iot.db"
            if "database" in _config:
                _db_config = _config["database"]
                self.DATABASE_URL = _db_config.get("url", fallback)
            else:
                self.DATABASE_URL = fallback

        # Create engine and session
        # check_same_thread is False for SQLite to handle multiple thread connections
        self.engine = create_engine(self.DATABASE_URL, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        self._create_tables(test=False)

    @contextmanager
    def get(self):
        """Returns a db Session object.

        Example usage:
        ```
        with Database().get() as db:
            db.query(...)
        ```
        """

        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def _assert_test_env(self):
        assert is_test_env()

    def _create_tables(self, test=True):
        if test: self._assert_test_env()
        Base.metadata.create_all(bind=self.engine)

    def _drop_tables(self):
        self._assert_test_env()
        Base.metadata.drop_all(bind=self.engine)
