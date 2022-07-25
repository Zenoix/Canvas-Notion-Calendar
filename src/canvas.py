from time import sleep
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def access_canvas(url):
    password = getpass()
    sleep(2)

    options = Options()
    # options.headless = True

    browser = webdriver.Chrome(options=options)
    browser.get(url)

    print(browser.title)

    browser.close()