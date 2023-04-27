import urllib.request
import zipfile
from pathlib import Path

MODELS = {
    "ru": "vosk-model-small-ru-0.22",
    "en": "vosk-model-en-us-0.22-lgraph",
}


def download_model(lang: str, folder: Path | None = None) -> Path:
    model = MODELS.get(lang, "en")

    if folder is None:
        folder = Path(__file__).parent / model

    if folder.exists():
        print(f"INFO: used existing model {model}")
        return folder

    print(f"INFO: downloading model {model}")
    url = f"https://alphacephei.com/vosk/models/{model}.zip"
    zip_path, _ = urllib.request.urlretrieve(url)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(folder.parent)

    return folder
