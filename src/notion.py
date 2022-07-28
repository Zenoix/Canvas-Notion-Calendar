import os
import requests
import json
import datetime

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

    def create_title_properties(self, title="Untitled"):
        return {"title": [{"type": "text", "text": {"content": title}}]}

    def create_date_properties(self, event_date=None):
        if not event_date:
            event_date = datetime.date.today().strftime("%Y-%m-%d")
        return {"date": {"start": event_date}}

    def create_website_properties(self, url=None):
        return {"type": "url", "url": url}

    def create_module_properties(self, module_name=None):
        return {"type": "select", "select": {"name": module_name}}

    def create_type_properties(self, types):
        return {"type": "multi_select", "multi_select": [{"name": event_type} for event_type in types]}

    def create_payload(self, title: str, date: str, assignment_url: str = None, course_name: str = "test",
                       assignment_type: list[dict[str, str]] = None):
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
                    "multi_select": assignment_type
                },
            }
        }

    def create_notion_page(self):
        headers = {
            "Authorization": os.getenv("NOTION_KEY"),
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json"
        }
        payload = self.create_payload("Testing", datetime.datetime.now().isoformat())
        response = requests.post(self.__API_BASE_URL, json=payload, headers=headers)

        print(json.dumps(response.json(), indent=2))


n = NotionAPIInterface()
n.create_notion_page()
