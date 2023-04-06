# ML Image Gatherer
A python CLI app that scrapes images from the web and prepares them for training an image classification machine learning algorithm.

## Setup
If you wish to run this yourself, follow the steps below:

1. Ensure that you have Python 3 installed.
2. Run `pip install -r requirements.txt` to install necessary dependencies.
3. Ensure that you have [Google Chrome](https://www.google.com/chrome/) and [Chrome Webdriver](https://chromedriver.chromium.org/downloads) installed.
4. Create a file called `env.cfg` in the root of the project, and paste the following text into it:

```
[DEFAULT]
CHROMEDRIVER_PATH = <PATH_TO_CHROME_WEBDRIVER_HERE>
```

5. Insert the path to the chrome webdriver you installed in the file.

That should be all you need to do to get the program up and running.
