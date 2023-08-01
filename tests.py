from telebot.types import Chat, Message, User

import main
import planes

# Tests fetching planes photo from jetphotos.com
assert (
    type(pl := planes.get_plane_photo("EI-FPH")[2]) == str
), f"Wrong type: {pl}"
print("Photos test successful")

# Tests start message to the bot
intro_message = Message(
    message_id=3475,
    from_user=User(id=82175453, is_bot=False, first_name="Anton"),
    date=1690915163,
    chat=Chat(id=82175453, type="private"),
    content_type="text",
    options=[],
    json_string={
        "message_id": 3475,
        "from": {
            "id": 82175453,
            "is_bot": False,
            "first_name": "Anton",
            "username": "antoncp",
            "language_code": "ru",
        },
    },
)

assert main.start_main(intro_message)[1].startswith("Welcome to the")
print("Start message test successful")
