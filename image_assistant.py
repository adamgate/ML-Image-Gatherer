# Entry point for the program

import argparse
from pathlib import Path

import webscraper
import image_processor


def main ():
    parser = argparse.ArgumentParser(description='Scrapes images from the web and prepares them for training ML algorithms')

    parser.add_argument('--subject',
                        '-s',
                        type=str,
                        help='the subject of the images to be scraped',
                        metavar='[subject]')

    parser.add_argument('--num',
                        '-n',
                        type=int, 
                        help='the number of images to fetch', 
                        choices=range(1,1000),
                        metavar='[1-1000]', 
                        default=10)
    
    parser.add_argument('--path',
                        '-p',
                        type=str,
                        help='path where images will be saved',
                        metavar='[path]')

    args = parser.parse_args()
 

if __name__ == '__main__':
    main()
