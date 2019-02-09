import requests
import json
import os
from time import time

# from wahkhen.api.settings import get_logger

# logger = get_logger(__name__)


def send_slack_notification(title, description, fallback="",
                            task_status="success", worker="None",
                            author="Wahkhen", severity="good"):

    # color: good, warning, danger

    if fallback == "":
        fallback = description

    slack_hook_url = os.getenv("SLACK_HOOK_URL")

    payload = {
        "attachments": [
            {
                "fallback": fallback,
                "color": severity,
                "author_name": author,
                "title": title,
                "text": description,
                "fields": [
                    {
                        "title": "Status",
                        "value": task_status,
                        "short": True
                    },
                    {
                        "title": "Worker",
                        "value": worker,
                        "short": True
                    }
                ],
                "ts": time()
            }
        ]
    }

    headers = {
        'Content-Type': "application/json",
        }

    response = requests.request("POST", slack_hook_url, data=json.dumps(payload), headers=headers)

    # logger.debug(response.text)

