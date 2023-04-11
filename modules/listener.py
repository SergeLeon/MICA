import queue
from threading import Thread

import vosk
import sounddevice

from core import Eventer

VOSK_MODEL_PATH = "vosk-model-small-ru-0.22"

running: bool
successfully_started = None
data_queue: queue.Queue
eventer: Eventer


def callback(indata, frames, time, status):
    data_queue.put(bytes(indata))


def listening_loop():
    global successfully_started
    try:
        model = vosk.Model(VOSK_MODEL_PATH)
    except:
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
        rec = vosk.KaldiRecognizer(model, samplerate)
        successfully_started = True

        while running:
            data = data_queue.get()
            if rec.AcceptWaveform(data):
                full_text = rec.Result()
                full_text = full_text[14:-3]
                print(full_text)
                if "мика" in full_text:
                    eventer.call_event("open_video", {"query": "зимнелетнее похождение"})

            else:
                part_text = rec.PartialResult()
                part_text = part_text[17:-3]
                print(part_text)


def init():
    if not sounddevice.default.device:
        print("WARNING: could not find an available microphone")
        return

    if successfully_started is not None:
        print("WARNING: listener module already initialized")
        return

    global running
    global data_queue
    global eventer

    running = True
    data_queue = queue.Queue()
    eventer = Eventer()

    Thread(target=listening_loop).start()

    while successfully_started is None:
        pass

    if successfully_started:
        print("INFO: listener module initialized")
    else:
        print("WARNING: failed to start listener module")


def stop():
    global running
    global started
    running = False
    started = False

    print("INFO: listener module stopped")


if __name__ == "__main__":
    from time import sleep

    init()
    sleep(60)
    stop()
