import os
import requests
import json
from datetime import date

from dotenv import load_dotenv

load_dotenv()


class NotionAPIInterface:
    def __init__(self):
        self.__API_BASE_URL = "https://api.notion.com/v1/pages"
        self.__DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
        
    def create_title_properties(self, title="Untitled"):
        return {"title": [{"type": "text", "text": {"content": title}}]}

    def create_date_properties(self, event_date=None):
        if not event_date:
            todays_date = date.today().strftime("%Y-%m-%d")
        return {"date": {"start": event_date}}

    def create_website_properties(self, url=None):
        return {"type": "url", "url": url}

    def create_files_properties(self, files=None):
        pass

    def create_module_properties(self, module_name="None"):
        return {"type": "select", "select": {"name": module_name}}

    def create_type_properties(self, types):
        return {"type": "multi_select", "multi_select": [{"name": event_type} for event_type in types]}

    def create_payload(self):
        return {"parent": {"type": "database_id",
                           "database_id": self.__DATABASE_ID},
                "properties": {
                    "title": None,
                    "date": None,
                    "Website": None,
                    "Files": None,
                    "module": None,
                    "Type": None}}

    def create_notion_page(self,):
        headers = {
            "Authorization": os.getenv("NOTION_KEY"),
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json"
        }
        payload = self.create_payload()
        response = requests.post(self.__API_BASE_URL, json=payload, headers=headers)

        print(json.dumps(response.json(), indent=2))
