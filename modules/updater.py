import os
import sys
import threading
import subprocess
from time import sleep

from core import Eventer, config

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
        if hasattr(thread, "_target") and getattr(thread, "_target") == restart:
            break


def restart():
    """stop all modules and restart app."""
    stop_all()
    os.execv(sys.executable, ["python"] + sys.argv)


def init_config():
    if not config.has_section("updater"):
        config.add_section("updater")
    config.set_if_none("updater", "autoupdate", True)
    config.set_if_none("updater", "check_period", 900)


def updating_loop():
    sleep(20)
    while running:
        if check_updates():
            update()
            restart()
        for _ in range(config.getint("updater", "check_period")):
            if not running:
                break
            sleep(1)


def check_updates() -> bool:
    env = {
        **os.environ,
        "LC_ALL": "C",
    }
    process = subprocess.Popen(["git", "status", "-uno"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdoutput, stderroutput = process.communicate()
    return b"Your branch is up to date with" not in stdoutput


def update():
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutput, stderroutput = process.communicate()
    print(f"INFO: MICA was updated {stdoutput}")


def check_git():
    try:
        process = subprocess.Popen(["git"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        return True
    except FileNotFoundError:
        return False


def stop():
    global running
    running = False
    print("INFO: updater module stopped")


def init():
    global running

    if running:
        print("WARNING: updater module already initialized")
        return

    if not check_git():
        print("WARNING: updater module cannot be run without git installed")
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

    print("INFO: updater module initialized")


if __name__ == "__main__":
    init()
