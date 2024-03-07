from bot.db import read_user
from config import settings


def test_read_user():
    """Tests reading user from MongoDB Atlas"""
    assert (
        read_user(settings.ADMIN_ID)["id"] == settings.ADMIN_ID
    ), "No user from database"
