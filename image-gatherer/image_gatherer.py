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

def check_file(filepath: Path):
    """ Ensures the provided file exists and is a txt file """

    if not str(filepath).endswith('.txt'):
        sys.exit("Batch file is not a txt file.")

    if not Path(filepath).exists():
        sys.exit(f'Provided file \"{filepath}\" doesn\'t exist.')

def load_file(filepath: Path):
    """ Loads each line of a txt file into an array """

    queries = []
    with open(filepath) as my_file:
        for line in my_file:
            queries.append(line)
    
    return queries


def scrape(args):
    """ Handles webscraper subparser logic """

    query = args.query
    num = args.num
    path = Path(args.path.strip("\\").strip("\"")) #Strip unwanted characters from path
    headless = args.headless
    check_path(path)

    # batch file, need multiple queries
    if args.batch is not None:
        check_file(args.batch)
        queries = load_file(args.batch)

        print(f'About to scrape {len(queries)} queries from file: \"{args.batch}\". Files will be stored at: \"{path.resolve()}\"')
        if not confirm_prompt("Proceed?"):
            sys.exit('Closing image gatherer...')

        for item in queries:
            # Create subdirectory for stored images
            item = sanitize_query(item)
            new_path = create_dir(path, item)

            # Let the webscraper do its thing
            image_links = webscraper.fetch_images(item, num, headless)
            webscraper.save_images(image_links, item, new_path)

    # Do a single query if no batch file
    else:
        print(f'About to scrape {num} images of \"{query}\". Files will be stored at: {path.resolve()}')
        if not confirm_prompt("Proceed?"):
            sys.exit('Closing image gatherer...')

        query = sanitize_query(query)

        # Create subdirectory for stored images
        path = create_dir(path, query)

        # Let the webscraper do its thing
        image_links = webscraper.fetch_images(query, num, headless)
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
    action = webscraper_parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-q',
                        '--query',
                        type=str,
                        help='The query of the images to be scraped.',
                        metavar='[query]')
    
    action.add_argument('-b',
                        '--batch',
                        type=str,
                        help='Path to a txt file with a query on each line.',
                        metavar='[path to batch txt file]')

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
                                    help='The path where the images will be saved. Defaults to ./downloads',
                                    metavar='[path]',
                                    default='downloads')
    
    webscraper_parser.add_argument('--headless',
                                    action=argparse.BooleanOptionalAction,
                                    help='The mode the scraper runs in. Headless or real. Defaults to headless.',
                                    default=True)
        
    # image processor commands
    img_processor_parser = subparsers.add_parser('process', help='Process scraped images for better ML consumption.')
    img_processor_parser.add_argument('-t',
                                      '--test',
                                      type=str,
                                      help='Test command..')
    
    args = parser.parse_args()

    # Main decision tree
    if (args.command == 'scrape'):
        scrape(args)
    elif (args.command == 'process'):
        process(args)

if __name__ == '__main__':
    main()
