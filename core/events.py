from typing import Callable
from threading import Thread

from loguru import logger


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
            if params:
                Thread(target=handler, args=(params,)).start()
            else:
                Thread(target=handler).start()

            logger.debug(f"started {handler} on {event} with {params=}")
