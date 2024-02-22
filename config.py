import logging.config
import os

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

MODE = "_LOCAL" if os.getenv("DEBUG") == "True" else ""


# Environment variables set up
class Settings:
    DEBUG = os.getenv("DEBUG") == "True"
    TEL_TOKEN = os.getenv(f"TEL_TOKEN{MODE}")
    RAPID_API = os.getenv(f"RAPID_API_TOKEN{MODE}")
    MAP_KEY = os.getenv(f"MAP_KEY{MODE}")
    TEL_LOG = os.getenv("TEL_LOG")
    ADMIN_ID = os.getenv("ADMIN_ID")
    BASE_LATITUDE = os.getenv("BASE_LATITUDE")
    BASE_LONGITUDE = os.getenv("BASE_LONGITUDE")


settings = Settings()


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
with open("logging_config.yaml", "rt") as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)
logger = logging.getLogger("special_debug")
tel_logger = logging.getLogger("telegram")
