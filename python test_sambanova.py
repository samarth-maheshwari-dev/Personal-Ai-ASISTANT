import requests, os, json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('SAMBANOVA_API_KEY')
print('Key loaded:', bool(key))

SYSTEM_PROMPT = """You are JARVIS. Reply ONLY with valid JSON.
Example: {"type":"command","action":"open","target":"spotify","app":"","extra":{}}"""

headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}
body = {
    'model': 'Meta-Llama-3.3-70B-Instruct',
    'messages': [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': 'open spotify'}
    ],
    'temperature': 0.1,
    'max_tokens': 500
}

r = requests.post('https://api.sambanova.ai/v1/chat/completions',
                  json=body, headers=headers, timeout=15)
print('Status:', r.status_code)
text = r.json()['choices'][0]['message']['content'].strip()
print('Raw response:', repr(text))

try:
    parsed = json.loads(text)
    print('Parsed OK:', parsed)
except Exception as e:
    print('JSON parse failed:', e)