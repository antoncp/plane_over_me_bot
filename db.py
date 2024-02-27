from pymongo import MongoClient

from config import logger, settings

try:
    base = MongoClient(settings.ATLAS_MONGO)
    logger.info("Connected to Mongo")
except Exception as e:
    logger.warning(f"Failed to connect to Mongo: {e}")
