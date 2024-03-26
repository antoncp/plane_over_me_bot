import logging.config
import os

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


# settings: Settings = Settings()
settings: Settings = Settings()


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
