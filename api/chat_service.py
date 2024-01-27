import requests
import os
from udew.settings import OPENAI_CHAT_HEADERS, OPENAI_ASS_ID


def create_chat_thread():
    url = "https://api.openai.com/v1/threads"

    response = requests.post(url, headers=OPENAI_CHAT_HEADERS)

    if response.ok:
        data = response.json()
        thread_id = data.get("id")
        if thread_id:
            return thread_id
        else:
            raise ValueError("Thread ID not found in the response")
    else:
        response.raise_for_status()


def run_chat_assistant(thread_id: str):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"

    response = requests.post(url, headers=OPENAI_CHAT_HEADERS, json={"assistant_id": OPENAI_ASS_ID})

    if response.ok:
        data = response.json()
        run_id = data.get("id")
        if run_id:
            return run_id
        else:
            raise ValueError("Assistant is not runned")
    else:
        response.raise_for_status()


def get_chat(thread_id: str):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"

    response = requests.get(url, headers=OPENAI_CHAT_HEADERS)
    data = response.json()
    transformed_messages = []

    for message in data["data"]:
        role = message["role"]
        content_blocks = message["content"]

        for content_block in content_blocks:
            if content_block["type"] == "text":
                content = content_block["text"]["value"]
                transformed_messages.append({"role": role, "content": content})

    return transformed_messages
