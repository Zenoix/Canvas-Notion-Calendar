from getpass import getpass

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests


class CanvasAPIInterface:
    def __init__(self, canvas_url: str = None):
        self.__canvas_url = canvas_url if canvas_url else input()
        self.__username = None
        self.__password = None
        self.__driver = None
        self.__session = None

    def get_canvas_login(self) -> None:
        self.__username = input("Username or Email: ")
        self.__password = getpass()

    def canvas_login(self) -> None:
        options = Options()
        options.headless = True

        self.__driver = webdriver.Chrome(options=options)
        self.__driver.get(self.__canvas_url)

        user_input = self.__driver.find_element(By.ID, "username")
        user_input.send_keys(self.__username)

        password_input = self.__driver.find_element(By.ID, "password")
        password_input.send_keys(self.__password)

        self.__driver.find_element(By.ID, "_eventId_proceed").click()

        try:
            WebDriverWait(self.__driver, 5).until(
                EC.title_is("Dashboard")
            )
            print("Successfully logged in!")
        except TimeoutException:
            print("Failed logging in.")
            self.__driver.close()


    def create_requests_session(self) -> None:
        self.__session = requests.Session()

    def transfer_cookies(self):
        # Set correct user agent
        selenium_user_agent = self.__driver.execute_script("return navigator.userAgent;")
        self.__session.headers.update({"user-agent": selenium_user_agent})

        for cookie in self.__driver.get_cookies():
            self.__session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    def close_all_connections(self) -> None:
        self.__session.close()
        self.__driver.close()
