from pathlib import Path
import configparser
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Load chromedriver for selenium
config_file = str(Path('.').parent.absolute())
config = configparser.ConfigParser()
config.read_file(open(config_file + '/env.cfg', 'r'))

def fetch_images(subject: str, num: int, path: Path):
    URL = 'https://images.google.com/'

    # Configure selenium chrome webdriver
    # option = webdriver.Chrome()
    # option.add_argument('--headless')
    # option.add_argument('--no-sandbox')
    # option.add_argument('--disable-dev-sh-usage')
    driver = webdriver.Chrome(config['DEFAULT']['CHROMEDRIVER_PATH'])
    driver.maximize_window()

    # load google
    driver.get(URL)
    # time.sleep(1000)

    # search for the subject in search bar
    driver.find_element(By.NAME, 'q').send_keys(subject)
    time.sleep(3)
    driver.find_element(By.CLASS_NAME, 'Tg7LZd').send_keys(Keys.ENTER)
    time.sleep(3)

    driver.close()