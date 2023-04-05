from pathlib import Path
import configparser
import time
import base64

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


def fetch_images(subject: str, num: int):
    """ Fetches <num> image links from google images based on a provided subject. """

    URL = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={subject}"

    # Configure selenium chrome webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-sh-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(config['DEFAULT']['CHROMEDRIVER_PATH'], options=options)

    # load google
    driver.get(URL)
    time.sleep(3)

    # scroll to the bottom of the page so many images load
    print("Loading images...")
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(.5)

        new_height = driver.execute_script('return document.body.scrollHeight')

        # click on "Show more results" (if exists)
        try:
            driver.find_element(By.CSS_SELECTOR, ".YstHxe input").click()
            time.sleep(3)
        except:
            pass

        # checking if we have reached the bottom of the page
        if new_height == last_height:
            break

        last_height = new_height

    # Grab all of the images
    thumbnail_results = driver.find_elements(By.CLASS_NAME, 'rg_i')
    fullsize_images = []
    print(f"Found {len(thumbnail_results)} potential images.")

    # load the large version of each image and save it
    count = 0
    for thumbnail in thumbnail_results:
        thumbnail.click()
        time.sleep(1)

        full_image = driver.find_element(By.CLASS_NAME, 'n3VNCb')
        if full_image.get_attribute('src') and 'http' in full_image.get_attribute('src'):
            fullsize_images.append(full_image.get_attribute('src'))
            print(f"Loaded image #{count+1} of {num}: {full_image.get_attribute('src')}")
            count += 1

        if count == len(thumbnail_results):
            print(f"Couldn't get {num} images. Got {len(fullsize_images)} instead.")
            break
        if count == num:
            break

    driver.close()
    
    return fullsize_images


def save_images(image_links,  subject: str, path: Path):
    """ Loads image links into images and saves them to the provided path.  """

    count = 0
    for link in image_links:
        img_path = f"{path}/{subject}{count+1}.jpg"

        try:
            image_content = requests.get(link).content

        except Exception as e:
            print(f"Error downloading image: {link} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            with open(img_path, 'wb') as file:
                image.save(file, "JPEG", quality=85)
            print(f"Successfully saved img: {link} - as {img_path}")

        except Exception as e:
            print(f"Error saving img: {link} - {e}")

        count += 1