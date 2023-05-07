import queue
from threading import Thread
from time import sleep

import vosk
import sounddevice

from core import Eventer, config
from .handler import handle_user_request, get_used_name
from .downloader import download_model

running: bool
successfully_started = None
data_queue: queue.Queue
eventer: Eventer


def callback(indata, frames, time, status):
    data_queue.put(bytes(indata))


def listening_loop():
    global successfully_started
    try:
        model_path = download_model(config.get("listener", "language", fallback="ru"))
        model = vosk.Model(model_path=str(model_path))
    except Exception as exc:
        print(exc)
        successfully_started = False
        return

    microphone = sounddevice.default.device[0]
    samplerate = int(sounddevice.query_devices(microphone, 'input')['default_samplerate'])

    with sounddevice.RawInputStream(
            samplerate=samplerate,
            blocksize=16000,
            device=microphone,
            dtype='int16',
            channels=1,
            callback=callback):
        recognizer = vosk.KaldiRecognizer(model, samplerate)
        successfully_started = True

        while running:
            data = data_queue.get()
            handle_raw_data(data, recognizer)


def handle_raw_data(data, recognizer):
    if recognizer.AcceptWaveform(data):
        full_text = recognizer.Result()
        full_text = full_text[14:-3]
        print(full_text)
        name = get_used_name(full_text)
        if name:
            print(f"DEBUG: request received {full_text}")
            handle_user_request(full_text, name)

    else:
        part_text = recognizer.PartialResult()
        part_text = part_text[17:-3]
        print(part_text)


def init_config():
    if not config.has_section("listener"):
        config.add_section("listener")
    config.set_if_none("listener", "language", "ru")


def init():
    if not sounddevice.default.device:
        print("WARNING: could not find an available microphone")
        return

    if successfully_started:
        print("WARNING: listener module already initialized")
        return

    global running
    global data_queue
    global eventer

    init_config()

    running = True
    data_queue = queue.Queue()

    eventer = Eventer()
    eventer.add_handler("stop", stop)

    thread = Thread(target=listening_loop)
    thread.name = "listener"
    thread.start()

    while successfully_started is None:
        sleep(0.5)

    if successfully_started:
        print("INFO: listener module initialized")
    else:
        print("WARNING: failed to start listener module")


def stop():
    global running
    global successfully_started
    running = False
    successfully_started = None

    print("INFO: listener module stopped")


if __name__ == "__main__":
    init()
    sleep(60)
    stop()
