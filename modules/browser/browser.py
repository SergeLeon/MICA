from time import sleep
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException, ElementNotInteractableException, WebDriverException

import chromedriver_autoinstaller
from loguru import logger

from core import Eventer, config

driver: webdriver.Chrome
wait: WebDriverWait

lock = False
need_to_stop = False


def stop_actions():
    global lock
    global need_to_stop
    need_to_stop = True
    while lock:
        sleep(0.5)
    need_to_stop = False


def stop_other(func):
    def _wrapper(*args, **kwargs):
        stop_actions()
        result = func(*args, **kwargs)
        return result

    return _wrapper


def lock_function(func):
    def _wrapper(*args, **kwargs):
        global lock
        lock = True
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            lock = False
            raise e
        lock = False
        return result

    return _wrapper


def get_driver():
    options = webdriver.ChromeOptions()
    if config.getboolean("browser", "full_screen_browser", fallback=True):
        options.add_argument("--kiosk")
        options.add_experimental_option("detach", True)

    options.add_argument("--start-maximized")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    options.add_argument('log-level=3')

    options.page_load_strategy = 'eager'

    # options.add_argument("--allow-profiles-outside-user-dir")
    # options.add_argument("--enable-profile-shortcut-manager")
    # options.add_argument(f"user-data-dir={Path.cwd() / 'selenium_data'}")
    # options.add_argument("--profile-directory=Profile 1")

    # options.add_argument('--log-level=3')
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])

    chrome_driver = webdriver.Chrome(options=options)

    return chrome_driver


@stop_other
@lock_function
def open_first_video_in_search(params):
    query = params["query"]

    driver.get(f"https://www.youtube.com/results?search_query={query}")

    # open video
    wait.until(
        EC.visibility_of_element_located((By.ID, "video-title"))
    ).click()

    if config.getboolean("browser", "full_screen_video", fallback=True):
        full_screen_current_video()


def full_screen_current_video():
    ActionChains(driver).move_to_element(
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ytp-chrome-controls"))
        )
    ).perform()

    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.ytp-fullscreen-button.ytp-button"))
    ).click()


@stop_other
@lock_function
def open_link(params):
    url = params["url"].strip()
    if not url.startswith("http") and not url.startswith("file:///"):
        url = f"http://{url}"
    try:
        driver.get(url)
        if (("://youtu.be" in url or "://youtube" in url or "://m.youtube" in url)
                and config.getboolean("browser", "full_screen_video", fallback=True)):
            full_screen_current_video()
    except WebDriverException:
        logger.warning(f"unable to load page '{url}'")


@stop_other
@lock_function
def show_gifs(params):
    query = params["query"]
    gif_links = get_gif_links(query)

    for gif_link in gif_links:
        if need_to_stop:
            return

        driver.get(f"{gif_link}/tile")
        driver.execute_script("document.body.style.overflow = 'hidden';")
        sleep(config.getint("browser", "gif_timeout", fallback=5))
        try:
            driver.find_element(By.ID, "didomi-notice-agree-button").click()
            driver.find_element(By.CLASS_NAME, "CloseButton-sc-ecivd4").click()
        except (NoSuchElementException, ElementNotInteractableException):
            pass


def get_gif_links(query):
    # TODO: find method to extract api key
    api_key = "Gc7131jiJuvI7IdN0HZ1D7nh0ow5BU6g"
    total_count = 25
    offset = 0
    while total_count - 25 >= offset:
        link = f"https://api.giphy.com/v1/gifs/search?offset={offset}&type=gifs&sort=&q={query}&api_key={api_key}"
        raw_json = requests.get(link).json()
        total_count = raw_json["pagination"]["total_count"]
        for obj in raw_json["data"]:
            yield obj["url"]
        offset += 25


def init_config():
    if not config.has_section("browser"):
        config.add_section("browser")
    config.set_if_none("browser", "full_screen_browser", True)
    config.set_if_none("browser", "full_screen_video", True)
    config.set_if_none("browser", "gif_timeout", 5)


def init():
    global driver
    global wait

    init_config()

    chromedriver_autoinstaller.install(path=str(Path(__file__).parent))

    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    eventer = Eventer()
    eventer.add_handler("open_video", open_first_video_in_search)
    eventer.add_handler("open_link", open_link)

    eventer.add_handler("show_gifs", show_gifs)

    eventer.add_handler("stop", stop)

    logger.info("browser module initialized")


def stop():
    stop_actions()
    driver.quit()

    logger.info("browser module stopped")


if __name__ == "__main__":
    init()
    Eventer.call_event("show_gifs", {"query": "anime"})
    sleep(20)
    Eventer.call_event("show_gifs", {"query": "cat"})
    sleep(20)
    Eventer.call_event("open_video", {"query": "зимнелетние похожденмя"})
    sleep(20)

    stop()
