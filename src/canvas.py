import time
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests


def get_canvas_login() -> tuple[str, str]:
    user = input("Username or Email: ")
    password = getpass()
    return user, password


def canvas_login(canvas_url: str, username: str, password: str) -> webdriver.Chrome | None:
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get(canvas_url)

    user_input = driver.find_element(By.ID, "username")
    user_input.send_keys(username)

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)

    driver.find_element(By.ID, "_eventId_proceed").click()

    time.sleep(2)

    if driver.title == "Dashboard":
        print("Successfully logged in!")
        return driver
    else:
        print("Failed logging in.")
        driver.close()


def create_requests_session() -> requests.sessions.Session:
    return requests.Session()


def transfer_cookies(session: requests.sessions.Session, driver: webdriver.Chrome) -> requests.sessions.Session:
    # Set correct user agent
    selenium_user_agent = driver.execute_script("return navigator.userAgent;")
    session.headers.update({"user-agent": selenium_user_agent})

    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    return session


def close_all_connections(session: requests.sessions.Session, driver: webdriver.Chrome) -> None:
    session.close()
    driver.close()
