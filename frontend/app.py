import requests

API_KEY = "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"

def get_ai_response(question):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "You are an Islamic assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {str(e)}"
