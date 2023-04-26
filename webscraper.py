######################################################
# Scrapes images from google images based on a query
#
# Author: Adam Applegate
######################################################

from pathlib import Path
import configparser
import time
import io

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from rich.progress import track
from PIL import Image

from image_gatherer import console, error_console

# Load chromedriver for selenium
config_file = str(Path('.').parent.absolute())
config = configparser.ConfigParser()
config.read_file(open(config_file + '/env.cfg', 'r'))

def initialize_webdriver(arg_options):
    """ Initializes a selenium chrome webdriver with the provided options. """

    options = webdriver.ChromeOptions()

    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--mute-audio')
    options.add_argument('--disable-dev-shm-usage')

    # headless flag
    if (arg_options[0] == True):
        options.add_argument('--headless')

    # debug flag
    if (arg_options[1] == False):
        options.add_argument('--log-level=3')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
    else:
        options.add_argument('--log-level=1')

    driver = webdriver.Chrome(config['DEFAULT']['CHROMEDRIVER_PATH'], options=options)
    return driver

def fetch_images(query: str, num: int, driver):
    """ Fetches a number of image links from google images based on a provided query. """

    URL = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={query}"

    # load google images
    driver.get(URL)
    time.sleep(3)

    # scroll to the bottom of the page so many images load, if necessary
    if (num > 35):
        last_height = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')

            # If it isn't loading many images, increase this number
            time.sleep(1.5)

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
    for attempt in range(10):
        try:
            thumbnail_results = driver.find_elements(By.CLASS_NAME, 'rg_i')
            console.print(f"[magenta]Found {len(thumbnail_results)} potential images for \"{query}\".")
            break
        except ElementClickInterceptedException as e:
            error_console.print(f'Error loading thumbnail results: - {e}')
            time.sleep(1)
            continue
    # Retries failed. Report and close app
    else:
        driver.save_screenshot(f'debug/ERROR_{time.strftime("%Y-%m-%d_%I-%M-%S-%p")}_{query}.png')
        driver.quit()
        error_console.print(f'Unable to load thumbnail results for \"{query}\"')


    # load the large version of each image and keep track of src link
    fullsize_images = []
    count = 0
    console.print(f"[yellow][bold]Processing[/bold] {num} images of \"{query}\"...")
    for thumbnail in thumbnail_results:
        thumbnail.click()
        time.sleep(1)

        # retry up to 10 times if the image loads slowly 
        for attempt in range(10):
            try:
                full_image = driver.find_element(By.CLASS_NAME, 'r48jcc')
                # Only save the image links, not the base64 encoded images
                if full_image.get_attribute('src') and 'http' in full_image.get_attribute('src'):
                    fullsize_images.append(full_image.get_attribute('src'))
                    count += 1
                break
            except NoSuchElementException as e:
                error_console.print(f'Error selecting image: - {e}')
                time.sleep(1)
                continue
        # Retries failed. Report and close app
        else:
            driver.save_screenshot(f'debug/ERROR_{time.strftime("%Y-%m-%d_%I-%M-%S-%p")}_{query}.png')
            driver.quit()
            error_console.print(f'Unable to select large images for \"{query}\"')
            return

        if count == num:
            break

    if count < num:
        console.print(f"[red]Couldn't find {num} acceptable images for \"{query}\". Got {len(fullsize_images)} instead.")

    driver.quit()

    console.print(f'[green]Successfully [bold]processed[/bold] {len(fullsize_images)} images of \"{query}\".')
    return fullsize_images


def save_images(image_links,  query: str, path: Path):
    """ Loads image links into images and saves them to the provided path.  """

    count = 0
    successful_saves = 0
    console.print(f"[yellow][bold]Saving[/bold] {len(image_links)} images of \"{query}\"...")
    for link in image_links:
        img_path = f"{path}/{query}{count+1}.jpg"

        try:
            image_content = requests.get(link).content
        except Exception as e:
            error_console.print(f"Error downloading image: {link} - {e}")

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            with open(img_path, 'wb') as file:
                image.save(file, "JPEG", quality=85)
            successful_saves += 1
        except Exception as e:
            error_console.print(f"Image #{count+1} for \"{query}\" link: {image_links[count]}")
            error_console.print(f"Error saving img: #{count+1} for \"{query}\" - {e}")

        count += 1

    if (successful_saves == len(image_links)):
        console.print(f'[green]Successfully [bold]saved[/bold] {successful_saves}/{count} images of \"{query}\".')
    elif (successful_saves == 0):
        error_console.print(f'Unable to save any images for \"{query}\"')
    else:
        console.print(f'[orange]Only able to [bold]save[/bold] {successful_saves}/{count} images of \"query\"')
