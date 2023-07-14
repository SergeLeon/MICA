from wsgiref.simple_server import make_server, WSGIRequestHandler
from threading import Thread
from pathlib import Path
import socket

from bottle import ServerAdapter, route, post, run, template, redirect, request, response, auth_basic, HTTPError, \
    static_file, TEMPLATE_PATH
from loguru import logger

from core import Eventer, config

STATIC_PATH = Path(__file__).parent / "static"
TEMPLATE_PATH.insert(0, STATIC_PATH)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


class StoppableWSGIRefServer(ServerAdapter):
    server = None

    def run(self, handler):
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): ...

            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        if server is not None:
            self.server.shutdown()


server: StoppableWSGIRefServer | None = None


def is_authenticated(user, password):
    return password == config.get("web_interface", "password")


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=STATIC_PATH)


@route("/")
def index():
    if config.get("web_interface", "password"):
        redirect("/settings")

    if request.auth:
        config.set("web_interface", "password", request.auth[1])
        redirect("/settings")

    err = HTTPError(401, "")
    err.add_header('WWW-Authenticate', 'Basic realm="%s"')
    return err


@route("/settings")
@auth_basic(is_authenticated)
def settings():
    return template("settings", config=config.as_dict())


@post("/settings")
@auth_basic(is_authenticated)
def change_setting():
    json = request.json
    config.set(json["module"], json["setting"], json["value"])
    return 'OK'


def init_config():
    if not config.has_section("web_interface"):
        config.add_section("web_interface")
    config.set_if_none("web_interface", "password", "")


def init():
    global server
    if server is not None:
        logger.warning("web_interface module already initialized")
        return

    init_config()

    eventer = Eventer()
    eventer.add_handler("stop", stop)

    server = StoppableWSGIRefServer(host="0.0.0.0", port=80)

    thread = Thread(target=run, kwargs={'server': server})
    thread.name = "web_interface"
    thread.start()

    Eventer.call_event(
        "open_link",
        {"url": f"https://api.qrserver.com/v1/create-qr-code/?size=1000x1000&data=http://{get_ip()}"}
    )

    logger.info("web_interface module initialized")


def stop():
    global server
    if server is None:
        logger.warning("web_interface module already stopped")
        return

    server.stop()
    server = None

    logger.info("web_interface module stopped")


if __name__ == "__main__":
    init()