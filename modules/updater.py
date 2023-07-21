import os
import sys
import threading
import subprocess
from time import sleep
from pathlib import Path

from loguru import logger

from core import Eventer, config

PROJECT_PATH = Path(__file__).parent.parent

running: bool = False


def stop_all():
    Eventer.call_event("stop")
    # ignore first MainThread
    while threading.enumerate()[1:]:
        sleep(1)
        threads = threading.enumerate()[1:]
        if len(threads) > 1:
            continue

        thread = threads[0]
        if thread.name == "updater" or (hasattr(thread, "_target") and getattr(thread, "_target") == restart):
            break


def restart():
    """stop all modules and restart app."""
    stop_all()
    os.execv(sys.executable, ["python"] + sys.argv)


def updating_loop():
    sleep(20)
    while running:
        if not config.getboolean("updater", "autoupdate"):
            sleep(30)
            continue

        if check_updates():
            update()
            restart()
        for _ in range(config.getint("updater", "check_period")):
            if not running:
                return
            sleep(1)


def check_git():
    try:
        process = subprocess.Popen(["git"], cwd=PROJECT_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        return True
    except FileNotFoundError:
        return False


def check_updates() -> bool:
    process = subprocess.Popen(["git", "fetch", "--dry-run"], cwd=PROJECT_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return any(process.communicate())


def update():
    process = subprocess.Popen(["git", "pull"], cwd=PROJECT_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f"MICA was updated {process.communicate()}")


def init_config():
    if not config.has_section("updater"):
        config.add_section("updater")
    config.set_if_none("updater", "autoupdate", True)
    config.set_if_none("updater", "check_period", 900)


def init():
    global running

    if running:
        logger.warning("updater module already initialized")
        return

    if not check_git():
        logger.warning("updater module cannot be run without git installed")
        return

    init_config()

    eventer = Eventer()
    eventer.add_handler("stop", stop)

    eventer.add_handler("restart", restart)

    if config.getboolean("updater", "autoupdate"):
        thread = threading.Thread(target=updating_loop)
        thread.name = "updater"
        thread.start()

        running = True

    logger.info("updater module initialized")


def stop():
    global running
    running = False
    logger.info("updater module stopped")


if __name__ == "__main__":
    print(check_updates())
