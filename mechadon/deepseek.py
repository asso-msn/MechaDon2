import requests

from . import config

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"


def chat(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(
        f"{BASE_URL}/chat/completions", json=payload, headers=headers
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def summarize(text: str) -> str:
    prompt = (
        "Please summarize the following chat log. "
        "Write the summary in the same language as the chat log. "
        "Keep it short. "
        "Do not use bullet points — write in plain prose. "
        "Focus on listing the topics that were discussed rather than detailing their content. "
        "Quote a few messages you deem important or representative, including the username of the sender.\n\n"
        f"{text}"
    )
    return chat(prompt)
