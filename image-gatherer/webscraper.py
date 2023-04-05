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

    # scroll to the bottom of the page so many images load
    last_height = driver.execute_script('return document.body.scrollHeight')

    while True:
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
 
        # waiting for the results to load
        # Increase the sleep time if your internet is slow
        time.sleep(3)

        new_height = driver.execute_script('return document.body.scrollHeight')

        # click on "Show more results" (if exists)
        try:
            driver.find_element(By.CSS_SELECTOR, ".YstHxe input").click()

            # waiting for the results to load
            # Increase the sleep time if your internet is slow
            time.sleep(3)

        except:
            print("Scrolling to bottom of page...")
            pass

        # checking if we have reached the bottom of the page
        if new_height == last_height:
            break

        last_height = new_height
    

    # capture each large image
    print('Saving images...')
    for i in range(1, num):
        try: 
            img = driver.find_element(By.XPATH, ('//*[@id="islrg"]/div[1]/div[' + str(i) + ']/a[1]/div[1]/img'))
 
            img.screenshot(f'{path}/{subject}{str(i)}.png')
            print(f'Saved image #{i} of {num}')
            time.sleep(0.2)
            
        except:
            num += 1
            continue

    # all done
    driver.close()
