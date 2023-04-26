##################################################################
# An assistant for training image classification ML models.
# Gathers images from the web and prepares them for consumption.
#
# Author: Adam Applegate
##################################################################

import sys
from pathlib import Path
import concurrent.futures
from datetime import datetime
import time
import requests

import argparse
from rich_argparse import RichHelpFormatter
from rich.console import Console

import webscraper

# fancy consoles
console = Console()
error_console = Console(stderr=True, style="bold red")

########################################################
#
#                   UTIL FUNCTIONS
#
#########################################################
def close_app(msg: str):
    """ Prints the message and closes the app. """
    console.print(f'[red]{msg}\n')
    sys.exit()


def confirm_prompt(question: str) -> bool:
    """ Easy way to get confirmation from user. """

    reply = None
    while reply not in ("y", "n", "1", "2"):
        reply = console.input(f"[yellow]{question} (y/n): ").casefold()
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

    if not path.exists() and (path == Path('downloads') or path == Path('debug')):
        path.mkdir(parents=True, exist_ok=True)
        console.print(f"Created folder {path}.")

    elif not path.exists():
        close_app(f'Provided path \"{path}\" doesn\'t exist.')

    elif not path.is_dir():
        close_app('Provided path is not a directory.')


def check_file(filepath: Path):
    """ Ensures the provided file exists and is a text file """

    if not str(filepath).endswith('.txt'):
        close_app("Provided file is not a text file.")

    if not Path(filepath).exists():
        close_app(f'Provided file \"{filepath}\" doesn\'t exist.')


def load_file(filepath: Path):
    """ Loads each line of a txt file into an array """

    queries = []
    with open(filepath) as my_file:
        for line in my_file:
            queries.append(line)
    
    return queries

########################################################
#
#                  CORE FUNCTIONS
#
#########################################################
def check_connection():
    """ Checks that the app can connect to the internet and google """
    try:
        response = requests.get('https://www.google.com')

        if (response.status_code == 200):
            console.print('[green]Successfully connected to Google.')
            return
        else:
            close_app(f'There was an issue connecting to Google - \"{response.status_code}\"')
            
    except Exception as e:
        close_app(f'Unable to connect to the internet - {e}')


def scrape(query, path, num, arg_options):
    """ Handles all the pieces necessary to scrape and store images """

    # Create subdirectory for stored images
    query = sanitize_query(query)
    new_path = create_dir(path, query)

    # Let the webscraper do its thing
    driver = webscraper.initialize_webdriver(arg_options)

    image_links = webscraper.fetch_images(query, num, driver)

    if (image_links is None):
        console.print(f'[red bold]Couldn\'t get images for {query}.')
        return
    try:
        driver.quit()
    except Exception as e:
        print(e)

    webscraper.save_images(image_links, query, new_path)


def main():
    """ Entry point for the program. """

    parser = argparse.ArgumentParser(description='Scrapes images from the web for training image classification ML algorithms',
                                     formatter_class=RichHelpFormatter)

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-q',
                        '--query',
                        type=str,
                        help='The query of the images to be scraped.',
                        metavar='[query]')
    
    action.add_argument('-b',
                        '--batch',
                        type=str,
                        help='Path to a text file with a query on each line.',
                        metavar='[path to file]')

    # Options for --batch and --query
    parser.add_argument('-n',
                        '--num',
                        type=int, 
                        help='The number of images to fetch, from 1-400. Defaults to 10.', 
                        choices=range(1,401),
                        metavar='[# of images]', 
                        default=10)
    
    parser.add_argument('-p',
                        '--path',
                        type=str,
                        help='The path where the images will be saved. Defaults to ./downloads',
                        metavar='[path to folder]',
                        default='downloads')
    
    parser.add_argument('-t',
                        '--threads',
                        type=int,
                        help='The number of concurrent processes to run. Only works with --batch and not --query.',
                        choices=range(1,60),
                        metavar='[# of threads]',
                        default=2)
    
    parser.add_argument('--headless',
                        action=argparse.BooleanOptionalAction,
                        help='The mode the scraper runs in. Headless or real. Defaults to headless.',
                        default=True)
    
    parser.add_argument("--debug",
                        action=argparse.BooleanOptionalAction,
                        help="Enables debug logging.",
                        default=False)

    
    args = parser.parse_args()

    num = args.num
    path = Path(args.path.strip("\\").strip("\"")) # Strip unwanted characters from path
    arg_options = [args.headless, args.debug] # optional flags

    # ensure internet & google are working
    check_connection()

    # Check user provided path
    check_path(path)

    # Create debug folder
    check_path(Path('debug'))

    # output errors to log file unless --debug is set
    if args.debug is False:
        sys.stderr = open(f'debug/report_{time.strftime("%Y-%m-%d_%I-%M-%S-%p")}.txt', 'w+')
        error_console.print(f"Report Generated {datetime.now().ctime()}")

    # batch file, need multiple queries
    if args.batch is not None:
        check_file(args.batch)
        queries = load_file(args.batch)

        console.print(f'About to scrape {num} images for each of {len(queries)} queries found in file: \"{args.batch}\".')
        console.print(f'Images will be stored at: [yellow]\"{path.resolve()}\"')
        console.print(f'{args.threads} queries will be scraped at a time.')
        if not confirm_prompt("Proceed?"):
            close_app('Closing image gatherer...')

        # Keep a pool of <X> processes and move to the next query when a thread is finished
        worker_pool = concurrent.futures.ProcessPoolExecutor(max_workers=args.threads)
        results = []
        try:
            for query in queries:
                results.append(worker_pool.submit(scrape, query, path, num, arg_options))

            worker_pool.shutdown(wait=True)
            console.print('[bold green]*****************************************************')
            console.print('[bold green]Finished saving images for the full batch of queries.')
            console.print('[bold green]*****************************************************')
        except Exception as e:
            console.print(e)
            pass
            
    # Do a single query if no batch file
    else:
        query = args.query
        console.print(f'[b]About to scrape {num} images of \"{query}\". Files will be stored at: [yellow]{path.resolve()}')
        if not confirm_prompt("Proceed?"):
            close_app('Closing image gatherer...')
            
        scrape(query, path, num, arg_options)
        console.print('[bold green]Finished saving images for the query.\n')

    # Close debug file
    sys.stderr.close()



if __name__ == '__main__':
    main()
