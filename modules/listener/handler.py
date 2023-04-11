from core import Eventer

BASIC_NAMES = [
    "мика",
    "миха",
]


def get_used_name(text: str) -> str:
    for name in BASIC_NAMES:
        if name in text:
            return name
    return ""


# TODO: use Scikit-Learn for commands
def handle_user_request(text: str, used_name: str):
    request = text.split(used_name, 1)[1].strip()
    if not request:
        return

    if request.startswith("включи"):
        search_query = request.replace("включи", "", 1).strip()
        Eventer.call_event("open_video", {"query": search_query})
