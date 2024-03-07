from datetime import datetime
from typing import Optional

from pymongo import MongoClient

from config import logger, settings

from .utils import timing_log

try:
    base = MongoClient(settings.ATLAS_MONGO)
    logger.debug("Successfully connected to Atlas Mongo")
except Exception as e:
    logger.warning(f"Failed to connect to Atlas Mongo: {e}")


@timing_log(extra_log=True, min_time=0)
def save_user(user: dict) -> Optional[int]:
    user["timestamp"] = datetime.utcnow()
    new_user = base.bots.planes.insert_one(user)
    extra_log = {"User data saved to Mongo": new_user}
    if new_user:
        return new_user.inserted_id, extra_log


@timing_log(extra_log=True, min_time=0)
def read_user(user_id: int) -> Optional[dict]:
    user = base.bots.planes.find_one({"id": user_id})
    extra_log = {"User data was retrieved from Mongo": user}
    if user:
        return user, extra_log


def save_coordinates(user_id: int, lat: int, lon: int) -> Optional[dict]:
    timestamp = datetime.utcnow()
    new_coord = base.bots.planes.update_one(
        {"id": user_id},
        {"$set": {"lat": lat, "lon": lon, "timestamp": timestamp}},
    )
    logger.debug(f"Coordinates updated: {new_coord}")
    if new_coord:
        return new_coord
