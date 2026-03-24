import requests, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('OPENROUTER_API_KEY')
print('Key found:', bool(key), key[:15] if key else 'NOT FOUND')

models = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://jarvis.local",
    "X-Title": "Jarvis"
}

for model in models:
    print(f"\nTrying: {model}")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "say hello"}],
        "max_tokens": 50
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=body, headers=headers, timeout=15
        )
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")