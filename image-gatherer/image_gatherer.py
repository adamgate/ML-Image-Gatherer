# Entry point for the program

import sys
import argparse
from pathlib import Path

from webscraper import fetch_images
from image_processor import process_images

def confirm_prompt(question: str) -> bool:
    reply = None
    while reply not in ("y", "n", "1", "2"):
        reply = input(f"{question} (y/n): ").casefold()
    return (reply == "y" or reply == "1")


def check_path(path: Path):
    if not path.exists():
        sys.exit('Provided path doesn\'t exist.')

    if not path.is_dir():
        sys.exit('Provided path is not a directory.')


def main ():
    parser = argparse.ArgumentParser(description='Scrapes images from the web and prepares them for training ML algorithms')

    parser.add_argument('-s',
                        '--subject',
                        type=str,
                        help='The subject of the images to be scraped.',
                        metavar='[subject]')

    parser.add_argument('-n',
                        '--num',
                        type=int, 
                        help='The number of images to fetch, from 1-1000. Defaults to 10.', 
                        choices=range(1,1000),
                        metavar='[1-1000]', 
                        default=10)
    
    parser.add_argument('-p',
                        '--path',
                        type=str,
                        help='The path where the images will be saved.',
                        metavar='[path]',
                        default='downloads')

    args = parser.parse_args()
    
    # Ensure path is exists and is a directory
    check_path(Path(args.path))

    print(f'About to scrape {args.num} images of \"{args.subject}\". Files will be stored at: {Path(args.path).resolve()}')
    if not confirm_prompt("Proceed?"):
        sys.exit('Closing image_gather...')

    # Let the webscraper do its thing
    fetch_images(args.subject, args.num, args.path)


if __name__ == '__main__':
    main()
