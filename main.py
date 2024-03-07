import telebot
from telebot.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup)

import bot.planes as planes
from bot.health_endpoint import flask_thread, shutdown_event
from bot.utils import clean_markdown
from config import logger, settings

bot = telebot.TeleBot(settings.TEL_TOKEN)
REMARKS = settings.REMARKS["EN"]

bot.set_my_commands([])


@bot.message_handler(commands=["start"])
def start(message: Message) -> Message:
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
    return bot.send_message(
        message.chat.id, text, reply_markup=keyboard, parse_mode="Markdown"
    )


@bot.message_handler(content_types=["location"])
def location(message: Message, **kwargs) -> None:
    if message.location is not None or kwargs.get("latitude"):
        if kwargs.get("latitude"):
            lat = kwargs.get("latitude")
            lon = kwargs.get("longitude")
        else:
            lat = message.location.latitude
            lon = message.location.longitude
        user = planes.user_details(message.chat.id)
        if user:
            user.update_coordinates(lat, lon)
        else:
            user = planes.User(message.chat.id, lat, lon)
        plane_list = planes.get_plane_list(lat, lon)
        sort_list = planes.sort_plane_list(plane_list)
        num_total_planes = sort_list.shape[0]
        num_planes_on_map = min(5, sort_list.shape[0])
        plane_map = planes.plane_map(lat, lon, sort_list)
        caption = REMARKS["map_caption"].format(
            num_planes_on_map, num_total_planes
        )
        sending = bot.send_photo(message.chat.id, plane_map)
        plane_selector = InlineKeyboardMarkup(row_width=1)
        plane_selector.add(
            *[
                InlineKeyboardButton(
                    text=info,
                    callback_data=(f"pl {reg}"),
                )
                for info, reg in planes.get_plane_selector(
                    sort_list, f"{message.chat.id}{sending.message_id}"
                )
            ]
        )
        bot.edit_message_caption(
            caption=caption,
            chat_id=message.chat.id,
            message_id=sending.message_id,
            reply_markup=plane_selector,
            parse_mode="Markdown",
        )
        user.last_map[sending.message_id] = sending.photo[0].file_id
        user.caption[sending.message_id] = caption
        if not user.saved:
            user.save_to_db()


@bot.callback_query_handler(func=lambda call: call.data.startswith("pl"))
def show_plane(call: CallbackQuery) -> None:
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
    response = bot.edit_message_media(
        media=telebot.types.InputMediaPhoto(image),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    plane_pic = response.photo[0].file_id
    update_plane_pic = planes.plane_photo_details(plane.reg)
    update_plane_pic.image = plane_pic
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
            f"_Photo credits: {date_img}, {clean_markdown(place_img)},"
            f" {clean_markdown(author_img)} {url}_"
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=plane_selector,
        parse_mode="Markdown",
    )
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("last"))
def show_map_again(call: CallbackQuery) -> None:
    user = planes.user_details(call.message.chat.id)
    if not user or not user.last_map.get(call.message.message_id):
        bot.send_message(call.message.chat.id, "Data is outdated")
        bot.answer_callback_query(callback_query_id=call.id)
        return
    bot.edit_message_media(
        media=telebot.types.InputMediaPhoto(
            user.last_map[call.message.message_id]
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    plane_selector = call.message.reply_markup
    plane_selector.keyboard = plane_selector.keyboard[:-1]
    bot.edit_message_caption(
        caption=user.caption[call.message.message_id],
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=plane_selector,
        parse_mode="Markdown",
    )
    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message) -> None:
    if message.text == "Last location":
        user = planes.user_details(message.chat.id)
        if not user:
            return bot.send_message(
                message.chat.id,
                "There is no last position in system. "
                "Please resend your location.",
            )
        latitude = user.lat
        longitude = user.lon
        location(message, latitude=latitude, longitude=longitude)


if __name__ == "__main__":
    flask_thread.start()
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error in the Telegram bot: {e}")
        shutdown_event.set()
