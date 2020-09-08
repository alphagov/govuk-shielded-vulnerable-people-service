import os
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def before_all(context):
    chrome_options = Options()
    chrome_options.binary = "bin/headless-chromium"
    chrome_options.add_argument("-headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")

    context.browser = webdriver.Chrome(options=chrome_options)
    context.browser.set_page_load_timeout(time_to_wait=200)

    context.config.setup_logging(os.environ.get("LOG_LEVEL", "ERROR"))
    context.logger = logging.getLogger("behave")


def after_all(context):
    context.browser.quit()
