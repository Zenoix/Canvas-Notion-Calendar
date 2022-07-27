from __future__ import annotations
from getpass import getpass
import re
import json
import sys
import time
from typing import Union, Type, Any

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests

JSONType = Union[dict[str, Any], list[Any], int, str, float, bool, Type[None]]


class CanvasAPIInterface:
    def __init__(self, canvas_url: str = None):
        self.__canvas_url = self.__verify_canvas_url(canvas_url)
        self.__username = None
        self.__password = None
        self.__driver = None
        self.__session = self.__create_requests_session()

    @staticmethod
    def __verify_canvas_url(canvas_url: str | None) -> str:
        url_pattern = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\/?"
        if not canvas_url:
            canvas_url = input("Enter your full Canvas url: ")
        while not re.search(url_pattern, canvas_url) or "canvas" not in canvas_url:
            print("Invalid Canvas url.")
            canvas_url = input("Enter your full Canvas url: ")
        if canvas_url[-1] != "/":
            return canvas_url + "/"
        return canvas_url

    @staticmethod
    def __create_requests_session() -> requests.sessions.Session:
        return requests.Session()

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
        print("Attempting to log in to canvas.")
        try:
            WebDriverWait(self.__driver, 5).until(
                EC.title_is("Dashboard")
            )
            print("Successfully logged in!")
        except TimeoutException:
            print("Failed logging in.")
            self.__driver.close()

    def transfer_cookies(self):
        # Set correct user agent
        selenium_user_agent = self.__driver.execute_script("return navigator.userAgent;")
        self.__session.headers.update({"user-agent": selenium_user_agent})

        for cookie in self.__driver.get_cookies():
            self.__session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    def __request_api_data(self, api_suffix: str) -> JSONType:
        request_url = f"{self.__canvas_url}api/v1/{api_suffix}{'?' if '?' not in api_suffix else '&'}per_page=50"
        response = self.__session.get(request_url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed response. Closing all connections and quitting.")
            self.close_all_connections()
            time.sleep(3)
            sys.exit()

    def get_course_info(self) -> JSONType:
        return self.__request_api_data("courses.json?enrollment_state=active")

    def get_course_assignments(self, course_id: int) -> JSONType:
        return self.__request_api_data(f"courses/{course_id}/assignments")

    @staticmethod
    def extract_assignment_info(assignment_json: JSONType) -> list[dict[str , int | str]]:
        useful_keys = ["id", "description", "due_at", "unlock_at", "name", "html_url"]
        return [{key: assignment.get(key) for key in useful_keys} for assignment in assignment_json]

    def close_all_connections(self) -> None:
        self.__session.close()
        self.__driver.close()
        print("All connections closed!")
