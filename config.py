import logging.config
import os
from datetime import datetime, timezone

import requests
import yaml
from dotenv import load_dotenv

load_dotenv(override=True)


# Environment variables set up
class Settings:
    DEBUG: bool = os.getenv("DEBUG") == "True"
    TEL_TOKEN: str = os.getenv("TEL_TOKEN")
    RAPID_API: str = os.getenv("RAPID_API")
    MAP_KEY: str = os.getenv("MAP_KEY")
    TEL_LOG: str = os.getenv("TEL_LOG")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID"))
    BASE_LATITUDE: int = os.getenv("BASE_LATITUDE")
    BASE_LONGITUDE: int = os.getenv("BASE_LONGITUDE")
    ATLAS_MONGO: str = os.getenv("ATLAS_MONGO")
    REDIS_PAS: str = os.getenv("REDIS_PAS")
    REMARKS: dict = {}

    @property
    def redis_host(self):
        if self.DEBUG:
            return "localhost"
        return "redis"


# settings: Settings = Settings()
settings: Settings = Settings()


class RedisDataSharing:
    last_map = ""
    last_plane_image = ""
    last_plane_url = ""
    last_plane_photo_author = ""
    plane_model = ""
    log_messages = []


# Custom logging handler (sends errors alerts via Telegram)
class CustomHTTPHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.url = f"https://api.telegram.org/{settings.TEL_LOG}/sendMessage"

    def emit(self, record):
        data = {
            "chat_id": settings.ADMIN_ID,
            "text": f"PLANES bot: {record.getMessage()}",
        }
        response = requests.get(self.url, data=data)
        if response.status_code != 200:
            logging.error(f"Error sending message: {response.text}")


class CustomRedisHandler(logging.Handler):
    def emit(self, record):
        timestamp = datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S")
        RedisDataSharing.log_messages.append(
            f"{timestamp} && {record.getMessage()}"
        )
        if len(RedisDataSharing.log_messages) > 5:
            RedisDataSharing.log_messages.pop(0)


# Logging configuration
with open("configs/logging_config.yaml", "rt") as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)
logger = logging.getLogger("special_debug")
logger_timing = logging.getLogger("timing_debug")

# Loading remarks
with open("configs/remarks.yaml", "r", encoding="utf-8") as f:
    remarks_data = yaml.safe_load(f)
    settings.REMARKS = remarks_data
