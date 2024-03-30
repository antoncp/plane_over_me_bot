from datetime import datetime, timezone
from typing import Optional

from pymongo import MongoClient

from config import logger, settings

from .utils import timing_log

try:
    base = MongoClient(settings.ATLAS_MONGO)
except Exception as e:
    logger.warning(f"Failed to connect to Atlas Mongo: {e}")


@timing_log(extra_log=True, min_time=0)
def save_user(user: dict) -> Optional[int]:
    """Saves user info (coordinates and telegram id) in a MongoDB Atlas
    Database. Adds a current timestamp to the record.

    Args:
        user (dict): User information as a dictionary.

    Returns:
        int, None: id of the new record if successful, None otherwise.
    """
    user["timestamp"] = datetime.now(timezone.utc)
    new_user = base.bots.planes.insert_one(user)
    extra_log = {"User data saved to Mongo": new_user}
    if new_user:
        return new_user.inserted_id, extra_log


@timing_log(extra_log=True, min_time=0)
def read_user(user_id: int) -> Optional[dict]:
    """Reads user info (coordinates) from MongoDB Atlas by telegram_id.

    Args:
        user_id (int): User id from Telegram.

    Returns:
        dict, None: dict with user coordinates if successful, None otherwise.
    """
    user = base.bots.planes.find_one({"id": user_id})
    extra_log = {"User data was retrieved from Mongo": user}
    if user:
        return user, extra_log


def save_coordinates(user_id: int, lat: int, lon: int) -> Optional[dict]:
    """Updates user info (coordinates) in a MongoDB Atlas Database with a
    new latitude and longitude by telegram_id.

    Args:
        user_id (int): User id from Telegram.
        lat (int): User's latitude.
        lon (int): User's longitude.

    Returns:
        dict, None: dict with new user info if successful, None otherwise.
    """
    timestamp = datetime.now(timezone.utc)
    new_coord = base.bots.planes.update_one(
        {"id": user_id},
        {"$set": {"lat": lat, "lon": lon, "timestamp": timestamp}},
    )
    logger.debug(f"Coordinates updated: {new_coord}")
    if new_coord:
        return new_coord
