from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller

from core import Eventer

FULL_SCREEN_VIDEO = True

driver: webdriver.Chrome
wait: WebDriverWait


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("detach", True)

    chrome_driver = webdriver.Chrome(options=options)

    return chrome_driver


def open_first_in_search(params):
    query = params["query"]

    driver.get(f'https://www.youtube.com/results?search_query={query}')

    # open video
    wait.until(
        EC.visibility_of_element_located((By.ID, "video-title"))
    ).click()

    if FULL_SCREEN_VIDEO:
        full_screen_current_page()


def full_screen_current_page():
    ActionChains(driver).move_to_element(
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ytp-chrome-controls"))
        )
    ).perform()

    wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.ytp-fullscreen-button.ytp-button"))
    ).click()


def open_link(params):
    url = params["url"]
    driver.get(url)


def init():
    global driver
    global wait

    chromedriver_autoinstaller.install(cwd=True)

    driver = get_driver()
    wait = WebDriverWait(driver, 3)

    eventer = Eventer()
    eventer.add_handler("open_video", open_first_in_search)
    eventer.add_handler("open_link", open_link)
    eventer.add_handler("stop", stop)

    print("INFO: browser module initialized")


def stop():
    driver.quit()

    print("INFO: browser module stopped")


if __name__ == "__main__":
    from time import sleep

    init()
    sleep(60)
    stop()
