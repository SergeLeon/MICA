from typing import Callable
from threading import Thread

from loguru import logger


def log_exceptions(func: Callable) -> Callable:
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.exception(f"an error occurred while executing {func.__module__}.{func.__name__}")

    return _wrapper


class Eventer:
    _handlers = {}

    @classmethod
    def add_handler(cls, event, handler: Callable):
        if event not in cls._handlers:
            cls._handlers[event] = list()

        cls._handlers[event].append(handler)
        logger.debug(f"for {event} added handler {handler.__module__}.{handler.__name__}")

    @classmethod
    def call_event(cls, event, params=None):
        if event not in cls._handlers:
            logger.warning(f"{event} handlers not defined")
            return

        for handler in cls._handlers[event]:
            logged_handler = log_exceptions(handler)
            if params:
                thread = Thread(target=logged_handler, args=(params,))
            else:
                thread = Thread(target=logged_handler)

            thread.name = f"{handler.__module__}.{handler.__name__}"
            thread.start()

            logger.debug(f"started {thread.name} on {event} with {params=}")
