import os

import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

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
    bot.send_message(message.chat.id, reply_markup=keyboard)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        lat = message.location.latitude
        lon = message.location.longitude
        plane_list = planes.get_plane_list(lat, lon)
        sort_list = planes.sort_plane_list(plane_list)
        plane_map = planes.plane_map(lat, lon, sort_list)
        bot.send_message(message.chat.id, f"Found {sort_list.shape[0]} planes")
        bot.send_photo(message.chat.id, plane_map, caption="Planes on map")


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
