from __future__ import annotations
import re
import sys
import time
import json
import itertools
from getpass import getpass
from typing import Union, Type, Any

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests

# Create a decent type hint for JSON files
JSONType = Union[dict[str, Any], list[Any], int, str, float, bool, Type[None]]


class CanvasAPIInterface:
    def __init__(self):
        # Load the config file
        with open("config/canvas.json") as cfg:
            self.__config = json.load(cfg)
        self.__canvas_url = self.__verify_canvas_url(self.__config["canvas_url"])
        self.__username = None
        self.__password = None
        self.__driver = None
        self.__session = self.__create_requests_session()
        self.__assignments = None

    @staticmethod
    def __verify_canvas_url(canvas_url: str | None) -> str:
        """
        Verify that the Canvas url is a valid url and has a slash at the end. If canvas_url is invalid,
        it will ask until a valid url is given.

        :param canvas_url: A possibly invalid Canvas url to attempt to log into
        :return: A valid Canvas url
        """
        url_pattern = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\/?"
        if not canvas_url or not isinstance(canvas_url, str):
            canvas_url = input("Enter your full Canvas url: ")
        while not re.search(url_pattern, canvas_url) or "canvas" not in canvas_url:
            print("Invalid Canvas url.")
            canvas_url = input("Enter your full Canvas url: ")
        if canvas_url[-1] != "/":
            return canvas_url + "/"
        return canvas_url

    @staticmethod
    def __create_requests_session() -> requests.sessions.Session:
        """
        Creates and returns a new requests session

        :return: Returns a requests session
        """
        return requests.Session()

    def __get_canvas_login(self) -> None:
        """
        If a Canvas login has not been stored, ask the user to input their username and password.
        The password input will be hidden.

        :return: None
        """
        if not self.__username and not self.__password:
            self.__username = input("Username or Email: ")
            self.__password = getpass()

    def __canvas_login(self) -> None:
        """
        Create a headless browser and attempt to log in to Canvas.

        :return: None
        """
        options = Options()
        options.headless = True

        self.__driver = webdriver.Chrome(options=options)
        self.__driver.get(self.__canvas_url)

        html_ids = self.__config["canvas_login_html_ids"]
        user_input = self.__driver.find_element(By.ID, html_ids["username_id"])
        user_input.send_keys(self.__username)

        password_input = self.__driver.find_element(By.ID, html_ids["password_id"])
        password_input.send_keys(self.__password)

        self.__driver.find_element(By.ID, html_ids["login_button_id"]).click()
        print("Attempting to log in to canvas.")
        try:
            WebDriverWait(self.__driver, 5).until(
                EC.title_is(self.__config["canvas_page_title"])
            )
            print("Successfully logged in!\n")
        except TimeoutException:
            print("Failed logging in.")
            self.__driver.close()

    def __transfer_cookies(self):
        """
        Transfer the Canvas cookies from the headless browser into the request session.

        :return: None
        """
        # Code adapted from https://stackoverflow.com/a/58171737
        selenium_user_agent = self.__driver.execute_script("return navigator.userAgent;")
        self.__session.headers.update({"user-agent": selenium_user_agent})

        for cookie in self.__driver.get_cookies():
            self.__session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    def __request_api_data(self, api_suffix: str) -> JSONType | None:
        """
        Request data from the Canvas API with a given suffix.

        :param api_suffix: The suffix to append to the api base url
        :return: A json of the response if the status code is 200
        """
        request_url = f"{self.__canvas_url}api/v1/{api_suffix}{'?' if '?' not in api_suffix else '&'}" \
                      f"per_page={self.__config['api_max_results']}"
        response = self.__session.get(request_url)
        if response.status_code == 200:
            return response.json()
        else:  # If the response was not a success, close all connections and quit the program
            print("Failed response. Closing all connections and quitting.")
            self.__close_all_connections()
            time.sleep(3)
            sys.exit()

    def __get_course_info(self) -> JSONType:
        """
        Get information on all currently enrolled courses.

        :return: A json of course data if the api request was a success
        """
        return self.__request_api_data("courses.json?enrollment_state=active")

    def __get_course_assignments(self, course_id: int) -> JSONType:
        """
        Get information on all assignments for a given course ID.

        :param: The ID of the course whose assignments are of interest
        :return: A json of assignment information if the api request was a success
        """
        return self.__request_api_data(f"courses/{course_id}/assignments")

    def __get_course_assignment_groups(self, course_id: int) -> dict[int, str]:
        """
        Get the assignment groups for a given course ID. From there, it returns a new

        :param course_id: The ID of the course whose assignment groups are of interest
        :return: Dictionary with assignment group id as key, and the assignment type as the value
        """
        assignment_groups = self.__request_api_data(f"courses/{course_id}/assignment_groups")
        return {group["id"]: group["name"] for group in assignment_groups}

    def __extract_assignment_info(self, course_name: str, assignment_groups: dict[int, str],
                                  assignment_json: JSONType) -> list[dict[str, int | str]]:
        """
        Extract the relevant pieces of information from an assignment json.
        The relevant pieces of information will be used in the creation of the Notion calendar pages.

        :param course_name: Name of the course
        :param: assignment_groups: Dictionary with assignment group id as key, and the assignment type as the value
        :param assignment_json: The json of all assignments for the given course
        :return: A list containing assignment dictionaries for a given course.
        Each dictionary will be for a single assignment with the relevant pieces of information
        """
        useful_keys = self.__config["relevant_assignment_keys"]
        return [
            {"course_name": course_name} | {"assignment_type": assignment_groups[assignment["assignment_group_id"]]} | {
                key: assignment.get(key)
                for key in useful_keys}
            for assignment in assignment_json]

    def __extract_all_assignment_info(self, courses: JSONType) -> list[dict[str, str | int]]:
        """
        Extract assignment information from all courses.

        :param courses: A json containing course information for all currently enrolled courses
        :return: A list containing assignment dictionaries for all courses.
        Each dictionary will be for a single assignment with the relevant pieces of information
        """
        assignments = []
        for course in courses:
            course_name = course["course_code"]
            print(f"Grabbing assignment data for {course_name}")
            # Check if the course name matches a given pattern
            if not re.match(self.__config["course_name_regex"], course_name):
                print(f"{course_name} is not a valid course. Skipping.")
                time.sleep(4)
                continue
            assignment_json = self.__get_course_assignments(course["id"])
            time.sleep(2)  # Sleep to prevent too many api calls too quickly
            assignment_groups = self.__get_course_assignment_groups(course["id"])
            assignment_info = self.__extract_assignment_info(course_name, assignment_groups, assignment_json)
            assignments.append(assignment_info)
            time.sleep(2.5)  # Sleep to prevent too many api calls too quickly
        print()
        # Unpack all the different assignments into just one list of dictionaries
        return list(itertools.chain(*assignments))

    def __close_all_connections(self) -> None:
        """
        Close the request session and headless browser

        :return: None
        """
        self.__session.close()
        self.__driver.close()
        print("All connections closed!")

    @property
    def assignments(self) -> list[dict[str, str | int]] | None:
        """
        Getter method that returns the assignments list.

        :return: A list containing assignment dictionaries for all courses if the run method has be executed otherwise
        returns None. If the return is a list, each dictionary will be for a single assignment with the relevant pieces
        of information
        """
        return self.__assignments

    def run(self) -> None:
        """
        Method to run the whole assignment extraction pipeline. After the process is complete, the assignments that have
        been extracted will be stored as the instance variable "assignment"

        :return: None
        """
        self.__get_canvas_login()
        self.__canvas_login()
        self.__transfer_cookies()
        courses = self.__get_course_info()
        self.__assignments = self.__extract_all_assignment_info(courses)
        self.__close_all_connections()
