import pytest

from config import settings
from main import start, handle_text


@pytest.fixture
def message(mocker):
    message = mocker.Mock()
    message.chat.id = int(settings.ADMIN_ID)
    message.from_user.id = int(settings.ADMIN_ID)
    return message


def test_start_command(message):
    """Tests start message of the bot"""
    assert start(message).text.startswith(
        "Welcome to the Plane_over_me_bot."
    ), "Wrong start message of the bot"


def test_last_location_with_no_location(message):
    """Tests Last location function with no last location position"""
    message.text = "Last location"
    settings.DEBUG = False
    assert handle_text(message).text.startswith(
        "There is no last position in system"
    ), "Last location error message"