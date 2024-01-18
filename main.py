import logging.config
import os

import telebot
from dotenv import load_dotenv
from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from yaml import safe_load

import planes

load_dotenv()

MODE = "_LOCAL" if os.getenv("DEBUG") == "True" else ""
bot = telebot.TeleBot(os.getenv(f"TEL_TOKEN{MODE}"))

with open("logging_config.yaml", "rt") as f:
    config = safe_load(f.read())
logging.config.dictConfig(config)
logger = logging.getLogger("all")

bot.set_my_commands([])


def send_text(*args):
    bot.send_message(
        args[0],
        args[1],
        reply_markup=args[2] if args[2] else None,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["start"])
def start(message):
    answer = start_main(message)
    send_text(*answer)


def start_main(message):
    keyboard = ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(
        KeyboardButton(text="Planes", request_location=True),
        KeyboardButton(text="Last location"),
    )
    text = (
        "Welcome to the *Plane_over_me_bot*. Provide your location via "
        "Telegram and get instant picture about nearest planes in the air. "
        "After getting the map with planes' marks you can examine the "
        "concrete plane by pushing the button with its parameters _(distance "
        "from you / plane model / plane altitude / plane speed)_.\n\n"
        "Use bot buttons, integrated to the keyboard:\n\n"
        "*Planes* - up to 5 planes around you, higher than "
        "100 meters\n\n*Last location* - planes in you last provided "
        "location without sending new one (e.g. for requests from "
        "non-mobile Telegram)"
    )

    return message.chat.id, text, keyboard


@bot.message_handler(content_types=["location"])
def location(message, **kwargs):
    if message.location is not None or kwargs.get("latitude"):
        if kwargs.get("latitude"):
            lat = kwargs.get("latitude")
            lon = kwargs.get("longitude")
        else:
            lat = message.location.latitude
            lon = message.location.longitude
        user = planes.user_details(message.chat.id)
        if user:
            user.lat = lat
            user.lon = lon
        else:
            user = planes.User(message.chat.id, lat, lon)
        plane_list = planes.get_plane_list(lat, lon)
        sort_list = planes.sort_plane_list(plane_list)
        num_total_planes = sort_list.shape[0]
        num_planes_on_map = min(5, sort_list.shape[0])
        plane_map = planes.plane_map(lat, lon, sort_list)
        plane_selector = InlineKeyboardMarkup(row_width=1)
        plane_selector.add(
            *[
                InlineKeyboardButton(
                    text=info,
                    callback_data=(f"pl {reg}"),
                )
                for info, reg in planes.get_plane_selector(sort_list)
            ]
        )
        sending = bot.send_photo(
            message.chat.id,
            plane_map,
            caption=(
                f"{num_planes_on_map} planes on the map"
                f", total in a 80 km circle: {num_total_planes}"
            ),
            reply_markup=plane_selector,
        )
        user.last_map = sending.photo[0].file_id
        user.caption = sending.caption


@bot.callback_query_handler(func=lambda call: call.data.startswith("pl"))
def show_plane(call):
    plane = planes.plane_details(call.data.split()[1])
    if not plane:
        bot.send_message(call.message.chat.id, "Data is outdated")
        bot.answer_callback_query(callback_query_id=call.id)
        return
    (
        image,
        plane_model,
        date_img,
        place_img,
        author_img,
        url,
    ) = planes.get_plane_photo(plane.reg)
    plane_selector = call.message.reply_markup
    bot.edit_message_media(
        media=telebot.types.InputMediaPhoto(image),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    if "Show the map" not in str(call.message):
        plane_selector.add(
            InlineKeyboardButton(
                text="Show the map",
                callback_data=("last"),
            )
        )
    bot.edit_message_caption(
        caption=(
            f"({plane.order}) {plane_model} `({plane.reg})`\n\n"
            f"*{plane.alt}* m / *{plane.spd}* km/h\n"
            f"_Distance from you: {plane.dist} km_\n\n"
            f"{plane.start}\n*>>>*\n{plane.end}\n\n"
            f"_Photo credits: {date_img}, {place_img}, {author_img} {url}_"
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=plane_selector,
        parse_mode="Markdown",
    )
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("last"))
def show_map_again(call):
    user = planes.user_details(call.message.chat.id)
    if not user or not user.last_map:
        bot.send_message(call.message.chat.id, "Data is outdated")
        bot.answer_callback_query(callback_query_id=call.id)
        return
    bot.edit_message_media(
        media=telebot.types.InputMediaPhoto(user.last_map),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    bot.edit_message_caption(
        caption=user.caption,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=call.message.reply_markup,
        parse_mode="Markdown",
    )
    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Last location":
        user = planes.user_details(message.chat.id)
        if not user:
            bot.send_message(
                message.chat.id,
                "There is no last position in system. "
                "Please resend your location.",
            )
            logger.warning("No position in system")
            return
        latitude = user.lat
        longitude = user.lon
        location(message, latitude=latitude, longitude=longitude)


if __name__ == "__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
