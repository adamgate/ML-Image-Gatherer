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

def sanitize_query(query: str):
    """ Strips illegal chars from query. """

    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        query = query.replace(char, '')
    query = query.strip()

    return query

def create_dir(path: Path, query: str):
    """ Creates a directory with the name of the query for storage of the images. """

    query = query.replace(" ", "_")

    path = path.joinpath(query)

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    return path
        
def check_path(path: Path):
    """ Ensures the provided path is valid, or creates the default path if no path was provided. """

    if not path.exists() and path == Path('downloads'):
        path.mkdir(parents=True, exist_ok=True)
        print("Created default path.")

    elif not path.exists():
        sys.exit(f'Provided path \"{path}\" doesn\'t exist.')

    elif not path.is_dir():
        sys.exit('Provided path is not a directory.')

def scrape(args):
    """ Handles webscraper subparser logic """

    query = args.query
    num = args.num
    path = Path(args.path.strip("\\").strip("\"")) #Strip unwanted characters from path

    check_path(path)
    query = sanitize_query(query)

    print(f'About to scrape {num} images of \"{query}\". Files will be stored at: {path.resolve()}')
    if not confirm_prompt("Proceed?"):
        sys.exit('Closing image_gather...')
    
    # Create subdirectory for stored images
    path = create_dir(path, query)

    # Let the webscraper do its thing
    image_links = webscraper.fetch_images(query, num)
    webscraper.save_images(image_links, query, path)

def process(args):
     """ Handles image processor subparser logic """
     image_processor.process_images()


def main ():
    """ Entry point for the program. """

    parser = argparse.ArgumentParser(description='Scrapes images from the web and prepares them for training ML algorithms')
    subparsers = parser.add_subparsers(dest='command')

    # webscraper commands
    webscraper_parser = subparsers.add_parser('scrape', help="Scrape images from the web")
    webscraper_parser.add_argument('-q',
                        '--query',
                        type=str,
                        help='The query of the images to be scraped.',
                        metavar='[query]')

    webscraper_parser.add_argument('-n',
                        '--num',
                        type=int, 
                        help='The number of images to fetch, from 1-400. Defaults to 10.', 
                        choices=range(1,401),
                        metavar='[1-400]', 
                        default=10)
    
    webscraper_parser.add_argument('-p',
                        '--path',
                        type=str,
                        help='The path where the images will be saved.',
                        metavar='[path]',
                        default='downloads')
    
    # image processor commands
    img_processor_parser = subparsers.add_parser('process', help='Process scraped images for better ML consumption.')
    img_processor_parser.add_argument('-t',
                        '--test',
                        type=str,
                        help='Test command..')
    
    args = parser.parse_args()

    if (args.command == 'scrape'):
        scrape(args)
    elif (args.command == 'process'):
        process(args)

if __name__ == '__main__':
    main()
