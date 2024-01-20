import logging.config
import os

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

# Logging set up + custom logging handler
with open("logging_config.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)
logger = logging.getLogger("all")
tel_logger = logging.getLogger("teleg")
