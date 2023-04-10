##################################################################
# An assistant for training image classification ML models.
# Gathers images from the web and prepares them for consumption.
#
# Author: Adam Applegate
##################################################################

import sys
import argparse
from pathlib import Path

import webscraper
import image_processor

def confirm_prompt(question: str) -> bool:
    """ Easy way to get confirmation from user. """

    reply = None
    while reply not in ("y", "n", "1", "2"):
        reply = input(f"{question} (y/n): ").casefold()
    return (reply == "y" or reply == "1")

def sanitize_query(subject: str):
    """ Strips illegal chars from subject. """

    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        subject = subject.replace(char, '')
    subject = subject.strip()

    return subject

def create_dir(path: Path, subject: str):
    """ Creates a directory with the name of the query for storage of the images. """

    subject = subject.replace(" ", "_")

    path = path.joinpath(subject)

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    return path
        
def check_path(path: Path):
    """ Ensures the provided path is valid, or creates the default path if no path was provided. """

    if not path.exists() and path == Path('downloads'):
        path.mkdir(parents=True, exist_ok=True)
        print("Created default path.")

    elif not path.exists():
        sys.exit('Provided path doesn\'t exist.')

    elif not path.is_dir():
        sys.exit('Provided path is not a directory.')


def main ():
    """ Entry point for the program. """

    parser = argparse.ArgumentParser(description='Scrapes images from the web and prepares them for training ML algorithms')
    subparsers = parser.add_subparsers()

    # webscraper commands
    webscraper_parser = subparsers.add_parser('scrape', help="Scrape images from the web")
    webscraper_parser.add_argument('-s',
                        '--subject',
                        type=str,
                        help='The subject of the images to be scraped.',
                        metavar='[subject]')

    webscraper_parser.add_argument('-n',
                        '--num',
                        type=int, 
                        help='The number of images to fetch, from 1-1000. Defaults to 10.', 
                        choices=range(1,101),
                        metavar='[1-1000]', 
                        default=10)
    
    webscraper_parser.add_argument('-p',
                        '--path',
                        type=Path,
                        help='The path where the images will be saved.',
                        metavar='[path]',
                        default='downloads')
    
    # image processor commands
    img_processor_parser = subparsers.add_parser('process', help='Process scraped images for better ML consumption')
    img_processor_parser.add_argument('-t',
                        '--test',
                        type=str,
                        help='Test command..')
    
    args = parser.parse_args()
    subject = args.subject
    num = args.num
    path = args.path
    
    check_path(path)
    subject = sanitize_query(subject)

    print(f'About to scrape {num} images of \"{subject}\". Files will be stored at: {path.resolve()}')
    if not confirm_prompt("Proceed?"):
        sys.exit('Closing image_gather...')
    
    # Create subdirectory for stored images
    path = create_dir(path, subject)

    # Let the webscraper do its thing
    image_links = webscraper.fetch_images(subject, num)
    webscraper.save_images(image_links, subject, path)


if __name__ == '__main__':
    main()
