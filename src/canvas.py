import time
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests


def get_canvas_login():
    user = input("Username or Email: ")
    password = getpass()
    return user, password


def canvas_login(canvas_url, username, password):
    options = Options()
    options.headless = True

    browser = webdriver.Chrome(options=options)
    browser.get(canvas_url)

    user_input = browser.find_element(By.ID, "username")
    user_input.send_keys(username)

    password_input = browser.find_element(By.ID, "password")
    password_input.send_keys(password)

    browser.find_element(By.ID, "_eventId_proceed").click()

    time.sleep(2)

    if browser.title == "Dashboard":
        print("Successfully logged in!")
        return browser
    else:
        print("Failed logging in.")
        browser.close()


def create_requests_session():
    return requests.Session()


def transfer_cookies(session, browser):
    # Set correct user agent
    selenium_user_agent = browser.execute_script("return navigator.userAgent;")
    session.headers.update({"user-agent": selenium_user_agent})

    for cookie in browser.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    return session


def close_all_connections(session, browser):
    session.close()
    browser.close()
