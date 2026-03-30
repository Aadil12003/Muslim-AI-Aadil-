import requests
import os

API_KEY = os.getenv("NVIDIA_API_KEY")
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def generate_answer(question):
    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "You are expert Islamic AI"},
            {"role": "user", "content": question}
        ],
        "max_tokens": 2000
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post(API_URL, headers=headers, json=payload)
    return res.json()["choices"][0]["message"]["content"]
