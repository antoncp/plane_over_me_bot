import json
from threading import Timer

import redis

from config import logger, settings

from .planes import AirCraft, User

REDIS_CONNECTED = False

try:
    r = redis.Redis(
        host="localhost",
        port=6379,
        password=settings.REDIS_PAS,
        decode_responses=True,
    )
    r.get("test")
    REDIS_CONNECTED = True
except Exception as e:
    logger.warning(f"Failure to connect to Redis: {e}")


def redis_updates():
    if not REDIS_CONNECTED:
        return
    num_planes = len(AirCraft.aircrafts)
    num_users = len(User.users.keys())
    reg_planes = []
    if num_planes:
        for plane in AirCraft.aircrafts:
            reg_planes.append(plane.reg)
            reg_planes = list(set(reg_planes))
    data = {
        "num_planes": num_planes,
        "num_users": num_users,
        "planes": reg_planes,
    }
    try:
        r.set("plane_over_me", json.dumps(data), ex=5)
        redis_update = Timer(1.0, redis_updates)
        redis_update.start()
    except Exception as e:
        logger.warning(f"Lost connection to Redis: {e}")
