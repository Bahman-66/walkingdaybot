import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
MODEL = os.getenv('MODEL')


def call_openai_api(prompt):
    """Interacts with OpenAI API (replace with your implementation)"""
    url = f"{OPENAI_BASE_URL}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch response from OpenAI API: {response.status_code}")
        return None