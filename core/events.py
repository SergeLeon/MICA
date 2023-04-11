from typing import Callable
from threading import Thread


class Eventer:
    _handlers = {}

    @classmethod
    def add_handler(cls, event, handler: Callable):
        if event not in cls._handlers:
            cls._handlers[event] = list()

        cls._handlers[event].append(handler)
        print(f"DEBUG: for {event} added handler {handler}")

    @classmethod
    def call_event(cls, event, params=None):
        if event not in cls._handlers:
            print(f"WARNING: {event} handlers not defined")
            return

        for handler in cls._handlers[event]:
            if params:
                Thread(target=handler, args=(params,)).start()
            else:
                Thread(target=handler).start()

            print(f"DEBUG: started {handler} on {event} with {params=}")
