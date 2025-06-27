from src.db import Database, StatusModel
from sqlalchemy import func
from sqlalchemy.orm import aliased


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


def get_device_status_history(device_id: str, skip: int = 0, limit: int = 100):
    with Database().get() as db:
        return (
            db.query(StatusModel)
            .filter(StatusModel.device_id == device_id)
            .order_by(StatusModel.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


def get_summary():
    with Database().get() as db:
        # Create a subquery that ranks each row by timestamp per device
        ranked = db.query(
            StatusModel,
            func.row_number().over(
                partition_by=StatusModel.device_id,
                order_by=StatusModel.timestamp.desc(),
            ).label("rnk")
        ).subquery()

        # Alias the StatusModel for cleaner access
        top = aliased(StatusModel, ranked)

        # Return only the top-ranked (latest) row per device
        results = db.query(top).filter(ranked.c.rnk == 1).all()
    return results
