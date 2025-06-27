from src.db import Database, StatusModel
from sqlalchemy import func


def add_device_status(status_model: StatusModel):
    with Database().get() as db:
        db.add(status_model)
        db.commit()

def get_device_status(device_id: str):
    # Query for the most recent status by timestamp
    with Database().get() as db:
        return (
            db.query(StatusModel)
            .filter(StatusModel.device_id == device_id)
            .order_by(StatusModel.timestamp.desc())
            .first()
        )

def get_summary():
    with Database().get() as db:
        # Subquery to get each device's latest status timestamp
        subquery = (
            db.query(StatusModel.device_id, func.max(StatusModel.timestamp).label("latest"))
            .group_by(StatusModel.device_id)
            .subquery()
        )

        # Join subquery back to main table to get full rows
        results = (
            db.query(StatusModel)
            .join(
                subquery,
                (StatusModel.device_id == subquery.c.device_id)
                & (StatusModel.timestamp == subquery.c.latest),
            )
            .all()
        )

    return results
