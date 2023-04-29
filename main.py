import os

import telebot
from dotenv import load_dotenv
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

import planes

load_dotenv()
RAPID_API = os.getenv("RAPID_API_TOKEN")
MAP_KEY = os.getenv("MAP_KEY")
bot = telebot.TeleBot(os.getenv("TEL_TOKEN"))


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(
        KeyboardButton(text="Share my location", request_location=True)
    )
    bot.send_message(message.chat.id, "Hi!", reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        lat = message.location.latitude
        lon = message.location.longitude
        plane_list = planes.get_plane_list(lat, lon)
        sort_list = planes.sort_plane_list(plane_list)
        num_total_planes = sort_list.shape[0]
        num_planes_on_map = min(5, sort_list.shape[0])
        plane_map = planes.plane_map(lat, lon, sort_list)
        plane_selector = InlineKeyboardMarkup(row_width=1)
        plane_selector.add(
            *[
                InlineKeyboardButton(text=i, callback_data=f"del {i}")
                for i in planes.get_plane_selector(sort_list)
            ]
        )
        bot.send_photo(
            message.chat.id,
            plane_map,
            caption=(
                f"{num_planes_on_map} planes on map"
                f", total found: {num_total_planes}"
            ),
            reply_markup=plane_selector,
        )


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
