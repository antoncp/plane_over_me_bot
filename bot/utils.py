import time
from typing import Callable

from config import logger


def replace_underscore(func: Callable) -> Callable:
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
                key: value.replace("_", " ")
                if isinstance(value, str)
                else value
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
    return text.replace("_", " ")


def timing(func: Callable) -> Callable:
    def timer(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > 0.1:
            logger.debug(f"({func.__name__}): {elapsed_time:.4f} seconds")
        return result

    return timer
