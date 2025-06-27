import pytest

from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def make_base_payload():
    return {
        "device_id": "sensor-validate",
        "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        "battery_level": 50,
        "rssi": -60,
        "online": True,
    }


@pytest.mark.parametrize("invalid_battery", [-10, 101])
def test_post_status_invalid_battery_level(invalid_battery):
    payload = make_base_payload()
    payload["battery_level"] = invalid_battery

    response = client.post("/status", json=payload)
    assert response.status_code == 422
    assert "battery_level" in response.text


@pytest.mark.parametrize(
    "missing_field",
    ["device_id", "timestamp", "battery_level", "rssi", "online"]
)
def test_post_status_missing_fields(missing_field):
    payload = make_base_payload()
    del payload[missing_field]

    response = client.post("/status", json=payload)
    assert response.status_code == 422
    assert missing_field in response.text


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("device_id", 12345),           # should be str
        ("timestamp", "not-a-date"),   # should be datetime string
        ("battery_level", "full"),     # should be int
        ("rssi", "strong"),            # should be int
        ("online", "yes"),             # should be bool
    ]
)
def test_post_status_invalid_types(field, invalid_value):
    payload = make_base_payload()
    payload[field] = invalid_value

    response = client.post("/status", json=payload)
    assert response.status_code == 422
    assert field in response.text
