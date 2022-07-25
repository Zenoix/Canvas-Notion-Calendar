import time
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def access_canvas(url):
    user = input("Username or Email: ")
    password = getpass()
    time.sleep(2)

    options = Options()
    options.headless = True

    browser = webdriver.Chrome(options=options)
    browser.get(url)

    user_input = browser.find_element(By.ID, "username")
    user_input.send_keys(user)

    password_input = browser.find_element(By.ID, "password")
    password_input.send_keys(password)

    browser.find_element(By.ID, "_eventId_proceed").click()

    time.sleep(2)

    print("Successfully logged in!" if browser.title == "Dashboard" else "Failed logging in")

    browser.close()