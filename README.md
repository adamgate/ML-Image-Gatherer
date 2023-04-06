# ML Image Gatherer
A python CLI app that scrapes images from the web and prepares them for training an image classification machine learning algorithm.

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

## Usage
Here's an example of how to use the app.

If you wish to get images to train a ML model to differentiate between cats and dogs, here's what to do:

1. Get 100 images of cats: `py image-gatherer/image_gatherer.py -s cat -n 100`
2. Get 100 images of dogs: `py image-gatherer/image_gatherer.py -s dog -n 100`
3. Prepare images for consumption (this portion of the app is still in progress)

Run `py image-gatherer/image_gatherer.py -h` to get a list of all possible commands.
