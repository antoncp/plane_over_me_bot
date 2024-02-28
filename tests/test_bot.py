import pytest

from config import settings
from main import handle_text, start


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


def test_no_answer_for_random_text(message):
    """Tests text function with random text"""
    message.text = "Hi bot!"
    assert handle_text(message) is None, "Answer for text error"
