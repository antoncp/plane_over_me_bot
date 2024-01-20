import logging

import requests

from config import settings


class CustomHTTPHandler(logging.Handler):
    def __init__(self, url=None):
        super().__init__()
        self.url = f"https://api.telegram.org/{settings.TEL_LOG}/sendMessage"

    def emit(self, record):
        data = {"chat_id": settings.ADMIN_ID, "text": record.getMessage()}

        response = requests.get(self.url, data=data)
        if response.status_code != 200:
            logging.error("Error sending message: {}".format(response.text))
