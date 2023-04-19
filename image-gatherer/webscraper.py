######################################################
# Scrapes images from google images based on a query
#
# Author: Adam Applegate
######################################################

from pathlib import Path
import configparser
import time

from PIL import Image
import io
import requests
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By

# Load chromedriver for selenium
config_file = str(Path('.').parent.absolute())
config = configparser.ConfigParser()
config.read_file(open(config_file + '/env.cfg', 'r'))


def fetch_images(query: str, num: int, headless: bool):
    """ Fetches <num> image links from google images based on a provided query. """

    URL = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={query}"

    # Configure selenium chrome webdriver
    options = webdriver.ChromeOptions()

    if (headless == True):
        options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--mute-audio')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(config['DEFAULT']['CHROMEDRIVER_PATH'], options=options)

    # load google
    driver.get(URL)
    time.sleep(3)

    # scroll to the bottom of the page so many images load
    print("Loading images...")
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')

        # If it isn't loading many images, increase this number
        # time.sleep(1)

        new_height = driver.execute_script('return document.body.scrollHeight')

        # click on "Show more results" if it's there
        try:
            driver.find_element(By.CSS_SELECTOR, ".YstHxe input").click()
            time.sleep(3)
        except:
            pass

        # checking if we have reached the bottom of the page
        if new_height == last_height:
            break

        last_height = new_height

    # Grab all of the image thumbnails
    thumbnail_results = driver.find_elements(By.CLASS_NAME, 'rg_i')
    print(f"Found {len(thumbnail_results)} potential images.")
    fullsize_images = []

    # load the large version of each image and save it
    count = 0
    for thumbnail in thumbnail_results:
        thumbnail.click()
        time.sleep(1)

        full_image = driver.find_element(By.CLASS_NAME, 'r48jcc')
        if full_image.get_attribute('src') and 'http' in full_image.get_attribute('src'):
            fullsize_images.append(full_image.get_attribute('src'))
            print(f"Loaded image #{count+1} of {num}: {full_image.get_attribute('src')}")
            count += 1

        if count == num:
            break

    if count < num:
        print(f"Couldn't get {num} images. Got {len(fullsize_images)} instead.")

    driver.quit()

    return fullsize_images


def save_images(image_links,  query: str, path: Path):
    """ Loads image links into images and saves them to the provided path.  """

    count = 0
    for link in image_links:
        img_path = f"{path}/{query}{count+1}.jpg"

        try:
            image_content = requests.get(link).content

        except Exception as e:
            print(f"Error downloading image: {link} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            with open(img_path, 'wb') as file:
                image.save(file, "JPEG", quality=85)
            print(f"Successfully saved img #{count+1} - as {img_path}")

        except Exception as e:
            print(f"Error saving img: #{count+1} - {e}")

        count += 1