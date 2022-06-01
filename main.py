import os
import requests
import json
from datetime import date

from dotenv import load_dotenv

load_dotenv()

url = "https://api.notion.com/v1/pages"
database_id = os.getenv("NOTION_DATABASE_ID")

todays_date = date.today().strftime("%Y-%m-%d")

headers = {
    "Authorization": os.getenv("NOTION_KEY"),
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json"
}

payload = {
    "parent": {"type": "database_id",
               "database_id": database_id},
    "properties": {
        "title": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "API Test"
                    }
                }
            ]
        },
        "date": {
            "date": {
                "start": todays_date
            }
        },
        "Completed": {
            "type": "checkbox",
            "checkbox": False
        },
        "Website": {
            "type": "url",
            "url": None
        },
        "Files": {
            "type": "rich_text",
            "rich_text": []
        },
        "module": {
            "type": "select",
            "select": {
                "name": "test"
            }
        },
        "notes": {
              "type": "rich_text",
              "rich_text": []
            },
        "Type": {
              "type": "multi_select",
              "multi_select": [{
                  "name": "api_tests"
              }]
            },
    }
}

response = requests.post(url, json=payload, headers=headers)

print(json.dumps(response.json(), indent=2))
