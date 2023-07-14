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

    if "видео" in request:
        search_query = text.split("видео", 1)[1].strip()
        Eventer.call_event("open_video", {"query": search_query})

    elif "гиф" in request:
        search_query = text.split("гиф")[1]
        if not search_query:
            return
        search_query = search_query.split(" ", 1)
        if len(search_query) == 1:
            return
        search_query = search_query[1]
        Eventer.call_event("show_gifs", {"query": search_query})

    elif "стоп" in request or "останови" in request or "выклю" in request:
        Eventer.call_event("stop")
