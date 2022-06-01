import os
import requests
import json
from datetime import date

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://api.notion.com/v1/pages"
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# for testing
todays_date = date.today().strftime("%Y-%m-%d")


def create_title_properties(title="Untitled"):
    return {"title": [{"type": "text", "text": {"content": title}}]}


def create_date_properties(event_date=todays_date):
    return {"date": {"start": event_date}}


def create_website_properties(url=None):
    return {"type": "url", "url": url}


def create_files_properties(files=None):
    pass


def create_module_properties(module_name="None"):
    return {"type": "select", "select": {"name": module_name}}


def create_type_properties(types):
    return {"type": "multi_select", "multi_select": [{"name": event_type} for event_type in types]}


def create_payload():
    return {"parent": {"type": "database_id",
                          "database_id": DATABASE_ID},
               "properties": {
                   "title": None,
                   "date": None,
                   "Website": None,
                   "Files": None,
                   "module": None,
                   "Type": None}}


def create_notion_page():
    headers = {
        "Authorization": os.getenv("NOTION_KEY"),
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json"
    }
    payload = create_payload()
    response = requests.post(API_BASE_URL, json=payload, headers=headers)

    print(json.dumps(response.json(), indent=2))
