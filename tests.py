import unittest
from unittest.mock import Mock

import planes
from config import settings
from main import start

# Tests fetching planes photo from jetphotos.com
assert (
    type(pl := planes.get_plane_photo("EI-FPH")[2]) == str
), f"Wrong type: {pl}"
print("Photos test successful")


class TestTelebot(unittest.TestCase):
    """Basic tests for the bot"""
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.message = Mock()
        self.message.chat.id = int(settings.INSPECT_ID)
        self.message.from_user.id = int(settings.INSPECT_ID)

    def tearDown(self):
        pass

    def test_start_command(self):
        """Tests start message of the bot"""
        self.assertTrue(
            start(self.message).text.startswith(
                "Welcome to the Plane_over_me_bot."
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
