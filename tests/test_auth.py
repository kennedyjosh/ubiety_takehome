import pytest

from fastapi.testclient import TestClient

import auth
from src.main import app
from src.auth import ApiKey
from src.db import Database


API_KEY = "test-key"
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_env_and_db(monkeypatch):
    # Auth is not checked when env var is set to test - remove it just for these tests
    # As a side effect, this affects the DB, so manually create and then cleanup (drop) the tables
    db = Database()
    db._create_tables()
    monkeypatch.delenv("UBIETY_RUN_ENV")
    yield
    monkeypatch.setenv("UBIETY_RUN_ENV", "test")
    db._drop_tables()


@pytest.fixture(scope="function")
def setup_api_key(monkeypatch, setup_env_and_db):
    monkeypatch.setattr(ApiKey, "get", lambda _: API_KEY)


@pytest.fixture(scope="function")
def setup_no_api_key(monkeypatch):
    monkeypatch.setattr(ApiKey, "get", lambda _: None)


def make_payload():
    from datetime import datetime, timezone
    return {
        "device_id": "sensor-auth",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_level": 70,
        "rssi": -60,
        "online": True,
    }


def test_verify_no_api_key(setup_no_api_key):
    auth.verify_api_key(None)
    auth.verify_api_key("")
    auth.verify_api_key("doesnt-matter")


def test_post_status_with_valid_api_key(setup_api_key):
    response = client.post(
        "/status",
        json=make_payload(),
        headers={"x-api-key": API_KEY},
    )
    assert response.status_code == 201


def test_post_status_with_invalid_api_key(setup_api_key):
    response = client.post(
        "/status",
        json=make_payload(),
        headers={"x-api-key": "invalid-key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_post_status_missing_api_key(setup_api_key):
    response = client.post("/status", json=make_payload())
    assert response.status_code == 422 or response.status_code == 401

    # FastAPI returns 422 for missing required header by default,
    # unless the dependency uses `Header(None)` and manually checks for presence
