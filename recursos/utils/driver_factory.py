import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from recursos.utils.config import Config


def create_driver(config: type[Config] = Config) -> webdriver.Remote:
    browser = config.BROWSER

    if browser == "firefox":
        options = FirefoxOptions()
        if config.HEADLESS:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
    else:
        options = ChromeOptions()
        options.page_load_strategy = "eager"
        if config.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_bin = os.getenv("CHROME_BIN") or os.getenv("CHROME_PATH")
        if chrome_bin:
            options.binary_location = chrome_bin
        driver = webdriver.Chrome(options=options)

    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(0)
    return driver
