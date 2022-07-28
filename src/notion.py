import os
import requests
import time

from dotenv import load_dotenv

load_dotenv()


class NotionAPIInterface:
    def __init__(self):
        self.__API_BASE_URL = "https://api.notion.com/v1/pages"
        self.__DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
        self.__assignments = None

    @property
    def assignments(self) -> list[dict[str, str | int]] | None:
        """
        Getter method that returns the assignments list.

        :return: A list containing assignment dictionaries for all courses if the run method has be executed otherwise
        returns None. If the return is a list, each dictionary will be for a single assignment with the relevant pieces
        of information
        """
        return self.__assignments

    @assignments.setter
    def assignments(self, assignments_list: list[dict[str, str | int]]):
        self.__assignments = assignments_list

    @staticmethod
    def __get_assignment_types(assignment):
        types = [{"name": "Deadline"}]

        valid_types = ("quiz", "test", "tutorial", "lab", "assignment", "exam")
        for assignment_type in valid_types:
            if assignment_type in assignment["assignment_type"].lower() or assignment["name"].lower():
                types.append({"name": assignment_type.title()})
                break
        else:
            types.append({"name": "Unknown"})
        return types

    def create_payload_json(self, title: str, date: str, assignment_url: str = None, course_name: str = "test",
                            assignment_types: list[dict[str, str]] = None):
        return {
            "parent": {"type": "database_id",
                       "database_id": self.__DATABASE_ID},
            "properties": {
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "date": {
                    "date": {
                        "start": date
                    }
                },
                "Completed": {
                    "type": "checkbox",
                    "checkbox": False
                },
                "Website": {
                    "type": "url",
                    "url": assignment_url
                },
                "module": {
                    "type": "select",
                    "select": {
                        "name": course_name
                    }
                },
                "Type": {
                    "type": "multi_select",
                    "multi_select": assignment_types
                },
            }
        }

    def extract_assignment_information(self, assignment):
        assignment_types = self.__get_assignment_types(assignment)
        return assignment.get("name"), assignment.get("due_at"), assignment.get("html_url"), \
               assignment.get("course_name"), assignment_types

    def create_notion_page(self, assignment, headers):
        assignment_information = self.extract_assignment_information(assignment)
        payload = self.create_payload_json(*assignment_information)

        print(f"{assignment_information[3]} - {assignment_information[0]}")

        requests.post(self.__API_BASE_URL, json=payload, headers=headers)
        time.sleep(2)

    def run(self):
        if not self.__assignments:
            print("No assignment data given. Use NotionAPIInterface.assignments = ... "
                  "to pass in assignment data before running again.")
            return

        headers = {
            "Authorization": os.getenv("NOTION_KEY"),
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json"
        }
        for assignment in self.__assignments:
            self.create_notion_page(assignment, headers)
