import logging.config
import os
from threading import Event, Thread

import requests
import yaml
from dotenv import load_dotenv
from flask import Flask

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


# Flask health check endpoint
app = Flask(__name__)
shutdown_event = Event()


@app.route("/", methods=["GET"])
def webhook():
    if not shutdown_event.is_set():
        return "Telegram bot is up!"


def run_flask_app():
    app.run(host="0.0.0.0", port=1300)


flask_thread = Thread(target=run_flask_app)
