import requests, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('GROQ_API_KEY')
print('Key found:', bool(key), key[:15] if key else 'NOT FOUND')

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

# Test 1: Simple request
body = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "say hello"}],
    "max_tokens": 50
}

r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    json=body, headers=headers, timeout=15
)
print('Status:', r.status_code)
print('Response:', r.text[:500])