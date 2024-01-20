import logging.config
import os

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

MODE = "_LOCAL" if os.getenv("DEBUG") == "True" else ""


# Environment variables set up
class Settings:
    TEL_TOKEN = os.getenv(f"TEL_TOKEN{MODE}")
    RAPID_API = os.getenv(f"RAPID_API_TOKEN{MODE}")
    MAP_KEY = os.getenv(f"MAP_KEY{MODE}")
    TEL_LOG = os.getenv("TEL_LOG")
    ADMIN_ID = os.getenv("ADMIN_ID")


settings = Settings()


# Custom logging handler
class CustomHTTPHandler(logging.Handler):
    def __init__(self, url=None):
        super().__init__()
        self.url = f"https://api.telegram.org/{settings.TEL_LOG}/sendMessage"

    def emit(self, record):
        data = {"chat_id": settings.ADMIN_ID, "text": record.getMessage()}

        response = requests.get(self.url, data=data)
        if response.status_code != 200:
            logging.error("Error sending message: {}".format(response.text))


# Logging set up
with open("logging_config.yaml", "rt") as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)
logger = logging.getLogger("all")
tel_logger = logging.getLogger("teleg")
