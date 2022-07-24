from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def access_canvas(url):
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    print(driver.title)

    driver.close()