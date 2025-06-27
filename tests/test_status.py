import pytest

from datetime import datetime, timedelta, timezone
from db import Database, StatusModel
from status import add_device_status, get_device_status, get_device_status_history, get_summary


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    # Create tables before test
    Database()._create_tables()

    yield

    # Drop tables after test
    Database()._drop_tables()


def make_status(device_id, minutes_ago=0, battery=50, rssi=-70, online=True):
    return StatusModel(
        device_id=device_id,
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
        battery_level=battery,
        rssi=rssi,
        online=online,
    )


def test_add_and_get_device_status(setup_database):
    status = make_status("sensor-123", battery=80)
    add_device_status(status)

    result = get_device_status("sensor-123")
    assert result is not None
    assert result.device_id == "sensor-123"
    assert result.battery_level == 80


def test_get_device_status_returns_latest(setup_database):
    old_status = make_status("sensor-abc", minutes_ago=10, battery=50)
    new_status = make_status("sensor-abc", minutes_ago=1, battery=90)
    add_device_status(old_status)
    add_device_status(new_status)

    result = get_device_status("sensor-abc")
    assert result.battery_level == 90


def test_status_history_pagination(setup_database):
    device_id = "sensor-paginated"

    # Insert 10 records spaced by 1 minute
    for i in range(10):
        add_device_status(make_status(device_id, minutes_ago=i, battery=50 + i))

    # Test: get first 5
    results = get_device_status_history(device_id, skip=0, limit=5)
    assert len(results) == 5
    assert results[0].battery_level == 50 + 0  # Newest
    assert results[-1].battery_level == 50 + 4

    # Test: get next 5
    results = get_device_status_history(device_id, skip=5, limit=5)
    assert len(results) == 5
    assert results[0].battery_level == 50 + 5
    assert results[-1].battery_level == 50 + 9  # Oldest

    # Test: skip beyond end
    results = get_device_status_history(device_id, skip=20, limit=5)
    assert results == []

    # Test: limit less than available
    results = get_device_status_history(device_id, skip=0, limit=3)
    assert len(results) == 3


def test_get_summary_returns_latest_per_device(setup_database):
    add_device_status(make_status("sensor-a", minutes_ago=5, battery=60))
    add_device_status(make_status("sensor-a", minutes_ago=1, battery=65))
    add_device_status(make_status("sensor-b", minutes_ago=2, battery=70))
    add_device_status(make_status("sensor-b", minutes_ago=0, battery=80))
    add_device_status(make_status("sensor-c", minutes_ago=2, battery=55))

    results = get_summary()

    assert len(results) == 3
    summary = {r.device_id: r for r in results}
    assert summary["sensor-a"].battery_level == 65
    assert summary["sensor-b"].battery_level == 80
    assert summary["sensor-c"].battery_level == 55
