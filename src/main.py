import src.status as status

from src.auth import verify_api_key
from datetime import datetime
from src.db import StatusModel
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, StrictBool
from typing import Annotated


app = FastAPI()


class StatusPayload(BaseModel):
    device_id: str
    timestamp: datetime
    battery_level: int = Field(ge=0, le=100)
    rssi: int
    online: StrictBool

    def to_model(self):
        return StatusModel(
            device_id=self.device_id,
            timestamp=self.timestamp,
            battery_level=self.battery_level,
            rssi=self.rssi,
            online=self.online
        )


@app.post("/status", status_code=201)
async def post_status(payload: StatusPayload, _auth: Annotated[str | None, Depends(verify_api_key)]):
    status.add_device_status(payload.to_model())


@app.get("/status/summary")
async def get_summary(_auth: Annotated[str | None, Depends(verify_api_key)]):
    results = status.get_summary()
    return [
        {
            "device_id": r.device_id,
            "timestamp": r.timestamp,
            "battery_level": r.battery_level,
            "online": r.online,
        }
        for r in results
    ]


@app.get("/status/{device_id}")
async def get_device_status(device_id: str, _auth: Annotated[str | None, Depends(verify_api_key)]):
    result = status.get_device_status(device_id)
    if not result:
        raise HTTPException(status_code=404, detail="Device not found")
    return {
        "device_id": result.device_id,
        "timestamp": result.timestamp,
        "battery_level": result.battery_level,
        "rssi": result.rssi,
        "online": result.online,
    }

@app.get("/status/{device_id}/history")
async def get_device_status_history(device_id: str,
                                    _auth: Annotated[str | None, Depends(verify_api_key)],
                                    skip: int = Query(0, ge=0),
                                    limit: int = Query(100, ge=1, le=500)):
    results = status.get_device_status_history(device_id, skip, limit)
    data = [
        {
            "device_id": r.device_id,
            "timestamp": r.timestamp,
            "battery_level": r.battery_level,
            "rssi": r.rssi,
            "online": r.online,
        }
        for r in results
    ]
    return {
        "skip": skip,
        "limit": limit,
        "data": data
    }
