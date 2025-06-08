import os
import requests
import json
import sys

def run_llama_request(user_prompt):
    token = os.getenv('LLAMA_KEY')
    if not token:
        raise ValueError("LLAMA_KEY environment variable is not set.")
    model = "Llama-4-Scout-17B-16E-Instruct-FP8"

    with open(os.path.join(os.path.dirname(__file__), '../prompts/system_prompt.txt'), 'r', encoding='utf-8') as f:
        systemPrompt = f.read()

    with open(os.path.join(os.path.dirname(__file__), '../prompts/structured_output.json'), 'r', encoding='utf-8') as f:
        structuredOutputSchema = json.load(f)

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
                "content": user_prompt
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "scam_call_analysis",
                "schema": structuredOutputSchema
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.status_code)
    print(response.json())

    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python llama_request.py '<user prompt>'")
        sys.exit(1)
    user_prompt = sys.argv[1]
    run_llama_request(user_prompt)
