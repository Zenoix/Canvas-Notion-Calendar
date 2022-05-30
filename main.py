import os
import requests

from dotenv import load_dotenv

load_dotenv()

url = "https://api.notion.com/v1/pages"
database_id = os.getenv("NOTION_DATABASE_ID")

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
                        "content": "Test"
                    }
                }
            ]
        },
        "date": {
            "date": {
                "start": "2022-05-31"
            }
        },
    },
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
