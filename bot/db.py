from datetime import datetime
from typing import Optional

from pymongo import MongoClient

from config import logger, settings

try:
    base = MongoClient(settings.ATLAS_MONGO)
    logger.debug("Successfully connected to Atlas Mongo")
except Exception as e:
    logger.warning(f"Failed to connect to Atlas Mongo: {e}")


def save_user(user: dict) -> Optional[int]:
    user["timestamp"] = datetime.utcnow()
    new_user = base.bots.planes.insert_one(user)
    logger.debug(f"User data saved to Mongo: {new_user}")
    if new_user:
        return new_user.inserted_id


def read_user(user_id: int) -> Optional[dict]:
    user = base.bots.planes.find_one({"id": user_id})
    logger.debug(f"User data was retrieved from Mongo: {user}")
    if user:
        return user


def save_coordinates(user_id: int, lat: int, lon: int) -> Optional[dict]:
    new_coord = base.bots.planes.update_one(
        {"id": user_id}, {"$set": {"lat": lat, "lon": lon}}
    )
    logger.debug(f"Coordinates updated: {new_coord}")
    if new_coord:
        return new_coord
