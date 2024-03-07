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


def timing_log(
    show_return: bool = False, extra_log: bool = False, min_time: float = 0.1
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def timer(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time > min_time:
                log = True
                log_message = f"({func.__name__}): {elapsed_time:.2f} seconds."
            else:
                log = False
            if extra_log and isinstance(result, tuple) and len(result) == 2:
                if log:
                    extra_message = " || ".join(
                        f"{key}: {value}" for key, value in result[1].items()
                    )
                    logger.debug(f"{log_message} {extra_message}")
                return result[0]
            if log:
                if result is None:
                    logger.debug(f"{log_message} Returned: None")
                elif show_return or isinstance(result, bool):
                    logger.debug(f"{log_message} Returned: {result}")
                else:
                    logger.debug(log_message)
            return result

        return timer

    return decorator
