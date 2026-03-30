import requests
import os
import time

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
API_KEY = os.getenv("NVIDIA_API_KEY")

def generate_answer(question):
    if not API_KEY:
        return "API key missing"

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert Islamic scholar AI."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 1000
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for i in range(3):
        try:
            res = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            time.sleep(2)

    return "Service busy"
