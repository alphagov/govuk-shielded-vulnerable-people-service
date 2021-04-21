import os
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def before_all(context):
    chrome_options = Options()
    chrome_options.binary = "bin/headless-chromium"
    chrome_options.headless = True

    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1200,800")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm")
    chrome_options.add_argument("--disable-info-bars")
    chrome_options.add_argument("--disable-browser-side-navigation")

    context.browser = webdriver.Chrome(options=chrome_options)
    context.browser.set_page_load_timeout(time_to_wait=60)
    context.browser.set_script_timeout(time_to_wait=60)
    context.browser.delete_all_cookies()

    context.config.setup_logging(os.environ.get("LOG_LEVEL", "ERROR"))
    context.logger = logging.getLogger("behave")


def after_all(context):
    context.browser.quit()
