import time
from typing import Callable, Optional

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import logger, logger_timing, settings

BUTTON = settings.REMARKS["EN"]["BUTTONS"]


def replace_underscore(func: Callable) -> Callable:
    """Decorator that replaces underscores in return data structures with
    whitespaces.
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, str):
            result = result.replace("_", " ")
        elif isinstance(result, list):
            result = [
                item.replace("_", " ") if isinstance(item, str) else item
                for item in result
            ]
        elif isinstance(result, dict):
            result = {
                key: (
                    value.replace("_", " ")
                    if isinstance(value, str)
                    else value
                )
                for key, value in result.items()
            }
        elif isinstance(result, tuple):
            result = tuple(
                item.replace("_", " ") if isinstance(item, str) else item
                for item in result
            )

        return result

    return wrapper


def clean_markdown(text: str) -> str:
    """Replaces underscores in strings with whitespaces."""
    return text.replace("_", " ")


def check_map_button(
    reply_markup: InlineKeyboardMarkup, call_message: Message
) -> Optional[InlineKeyboardMarkup]:
    """Adds the Show Map button to the reply keypad."""
    try:
        if BUTTON["show_map"] not in str(call_message):
            reply_markup.add(
                InlineKeyboardButton(
                    text=BUTTON["show_map"],
                    callback_data=("last"),
                )
            )
        return reply_markup
    except Exception as e:
        logger.warning(f"Add show_map button failed: {e}")
        return None


def timing_log(
    show_return: bool = False, extra_log: bool = False, min_time: float = 0.1
) -> Callable:
    """Decorator for measuring function execution time."""

    def decorator(func: Callable) -> Callable:
        def timer(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time > min_time:
                log = True
                log_message = (
                    f"({func.__module__}.{func.__name__}): "
                    f"{elapsed_time:.2f} seconds."
                )
            else:
                log = False
            if extra_log and isinstance(result, tuple) and len(result) == 2:
                if log:
                    extra_message = " || ".join(
                        f"{key}: {value}" for key, value in result[1].items()
                    )
                    logger_timing.debug(f"{log_message} {extra_message}")
                return result[0]
            if log:
                if result is None:
                    logger_timing.debug(f"{log_message} Returned: None")
                elif show_return or isinstance(result, bool):
                    logger_timing.debug(f"{log_message} Returned: {result}")
                else:
                    logger_timing.debug(log_message)
            return result

        return timer

    return decorator
