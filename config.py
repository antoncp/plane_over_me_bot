import logging.config
import os
from threading import Event, Thread

import requests
import yaml
from dotenv import load_dotenv
from flask import Flask

import planes

load_dotenv()

MODE = "_LOCAL" if os.getenv("DEBUG") == "True" else ""


# Environment variables set up
class Settings:
    DEBUG = os.getenv("DEBUG")
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
    def __init__(self, url=None):
        super().__init__()
        self.url = f"https://api.telegram.org/{settings.TEL_LOG}/sendMessage"

    def emit(self, record):
        data = {"chat_id": settings.ADMIN_ID, "text": record.getMessage()}
        response = requests.get(self.url, data=data)
        if response.status_code != 200:
            logging.error(f"Error sending message: {response.text}")


# Logging configuration
with open("logging_config.yaml", "rt") as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)
logger = logging.getLogger("special_debug")
tel_logger = logging.getLogger("telegram")


# Flask health check endpoint
app = Flask(__name__)
shutdown_event = Event()


@app.route("/", methods=["GET"])
def webhook():
    if not shutdown_event.is_set():
        title = "Planes bot is up"
        num_planes = len(planes.AirCraft.aircrafts)
        num_users = len(planes.User.users.keys())
        reg_list = " no dedicated planes "
        if num_planes:
            reg_planes = []
            for plane in planes.AirCraft.aircrafts:
                reg_planes.append(plane.reg)
            reg_list = ", ".join(reg_planes)
        info_1 = f"There are <b>{num_planes} planes</b> in system now:"
        info_2 = f"Active users in system: <b>{num_users}</b>"
        message = [title, info_1, f"<i>[{reg_list}]</i>", info_2]
        return "<br><br>".join(message)


def run_flask_app():
    app.run(host="0.0.0.0", port=1300)


flask_thread = Thread(target=run_flask_app)
