# ML Image Gatherer
A python CLI app that scrapes images from the web and prepares them for training image classification machine learning algorithms.

---

## Setup
If you wish to run this yourself, follow the steps below:

1. Ensure that you have Python 3 installed.
2. Run `pip install -r requirements.txt` to install necessary dependencies (I recommend doing this in a virtual environment).
3. Ensure that you have [Google Chrome](https://www.google.com/chrome/) and [Chrome Webdriver](https://chromedriver.chromium.org/downloads) installed.
4. Create a file called `env.cfg` in the root of the project, and paste the following text into it:

```
[DEFAULT]
CHROMEDRIVER_PATH = <PATH_TO_CHROME_WEBDRIVER_HERE>
```

5. Insert the path to the chrome webdriver you installed in the file.

That should be all you need to do to get the program up and running.

---

## Usage
Here's an example of how to use the app.

**There are 2 main ways to scrape images from the web. The first way is through individual queries, as shown below.**

If you wish to get images to train a ML model to differentiate between cats and dogs, here's what to do:

1. Navigate to the root folder of the application in your terminal.
2. To get 100 images of cats, run the following command: `py image_gatherer.py scrape --query cat --num 100`
3. To get 100 images of dogs: `py image_gatherer.py scrape --query dog --num 100`

**The second method is running a batch of queries from a file.**

Here are the steps:

1. Create a txt file with a different query on each line, like so:

```
dog
cat
<put as many queries as you want here>
```

2. Feed the query file into the `--batch` command: `py image-gatherer.py scrape --batch queries.txt --num 100`. This will get 100 images of each item in the queries file, so 100 dog and 100 cat images in this case.

*Once you have your images, make sure you verify you want to keep all of them. Then they're ready to be fed into your image classification algorithm.*

**Other Commands**
- The `--path` argument will determine where the scraped images are saved.
- Add the `--no-headless` flag to turn off headless mode and view the scraper as it works.
- Run `py image_gatherer.py --help` to get a list of all possible commands and options.
