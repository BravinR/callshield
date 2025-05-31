import os
import requests
import json

def main():
    token = os.getenv('LLAMA_KEY')
    if not token:
        raise ValueError("LLAMA_KEY environment variable is not set.")
    model = "Llama-4-Scout-17B-16E-Instruct-FP8"

    systemPrompt = "Null"

    url = "https://api.llama.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": systemPrompt
            },
            {
                "role": "user",
                "content": f"abc"
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    main()