import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434"

COMMAND_MODEL_CEREBRAS = "llama3.1-8b"
CONVERSATION_MODEL_OPENROUTER = "meta-llama/llama-3.3-70b-instruct:free"

SYSTEM_PROMPT = """You are JARVIS - smart, witty, and loyal to your creator. Keep replies short and punchy. Match the user's language (English/Hindi/Hinglish).

Output JSON only. No extra text.

COMMAND JSON:
{"type":"command","action":"<action>","target":"<target>","app":"<app>","arg":"<optional>"}

CONVERSATION JSON:
{"type":"conversation","reply":"<short reply>"}

ACTION MAPPINGS:
- open/kholo/bolo = open
- close/band/bandh/hatao = close
- play/bajao/baja = play
- pause/rukao = pause
- minimize/ghatanayo = minimize
- maximize/baadao = maximize
- volumeup/awaz/badao = increase
- volumedown/awaz/ghatao = kam/kam = decrease
- mute/mute = mute
- unmute/unmute = unmute
- next/agla/aage = next
- previous/pichhla/peechhe = previous
- focus/aane = focus
- web_search: for weather, news, facts, general info queries WITHOUT app target

RULES:
- If query contains weather/news/khabar/mausam and NO app name → action=web_search
- If query asks for explanation/story/info without app → action=web_search
- youtube/chrome in query + search → search_youtube

TARGET: spotify, chrome, youtube, notepad, vlc, edge, whatsapp, calculator, settings, explorer, or any app/window name.

EXAMPLES:
User: "open spotify" → {"type":"command","action":"open","target":"spotify","app":"spotify","arg":null}
User: "spotify band karo" → {"type":"command","action":"close","target":"spotify","app":"spotify","arg":null}
User: "kya haal hai?" → {"type":"conversation","reply":"Sab theek hai, Batao kya karu?"}
User: "who made you?" → {"type":"conversation","reply":"My creator built me. Loyalty runs deep."}
User: "chrome hata do" → {"type":"command","action":"close","target":"chrome","app":"chrome","arg":null}
User: "spotify pe shape of you bajao" → {"type":"command","action":"play","target":"spotify","app":"spotify","arg":"shape of you"}
User: "search python tutorial on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python tutorial"}
User: "youtube pe elon musk ki video lagao pehli wali" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"elon musk pehli wali"}
User: "india ka aaj ka weather batao" → {"type":"command","action":"web_search","target":"","app":"","arg":"india weather today"}
User: "what happened in india today" → {"type":"command","action":"web_search","target":"","app":"","arg":"india news today"}
User: "search web for latest iphone price" → {"type":"command","action":"web_search","target":"","app":"","arg":"latest iphone price"}"""


def call_sambanova(user_input: str) -> dict:
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {SAMBANOVA_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "Meta-Llama-3.3-70B-Instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }
    r = requests.post(url, json=body, headers=headers, timeout=15)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    text = text.strip()
    if "{" in text and "}" in text:
        start = text.index("{")
        end = text.rindex("}") + 1
        text = text[start:end]
    return json.loads(text)


def call_cerebras(user_input: str) -> dict:
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3.1-8b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }
    r = requests.post(url, json=body, headers=headers, timeout=15)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    text = text.strip()
    if "{" in text and "}" in text:
        start = text.index("{")
        end = text.rindex("}") + 1
        text = text[start:end]
    return json.loads(text)


def call_openrouter(user_input: str) -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis.local",
        "X-Title": "Jarvis"
    }
    body = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }
    r = requests.post(url, json=body, headers=headers, timeout=15)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    text = text.strip()
    if "{" in text and "}" in text:
        start = text.index("{")
        end = text.rindex("}") + 1
        text = text[start:end]
    return json.loads(text)


def call_ollama(user_input: str) -> dict:
    url = f"{OLLAMA_URL}/api/generate"
    prompt = SYSTEM_PROMPT + "\n\nUser: " + user_input + "\nJSON:"
    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 300}
    }
    r = requests.post(url, json=body, timeout=30)
    r.raise_for_status()
    text = r.json()["response"].strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    text = text.strip()
    if "{" in text and "}" in text:
        start = text.index("{")
        end = text.rindex("}") + 1
        text = text[start:end]
    return json.loads(text)


def classify_input(text: str) -> str:
    t = text.lower().strip()
    
    greetings = ['hi', 'hello', 'hey', 'hii', 'helo', 'sup',
                 'yo', 'namaste', 'namaskar', 'jai shri ram',
                 'good morning', 'good evening', 'good night',
                 'gm', 'gn', 'bye', 'goodbye', 'alvida']
    if t.strip() in greetings:
        return 'conversation'
    
    short_affirmatives = ['haan', 'ha', 'yes', 'ok', 'okay', 
                          'theek hai', 'acha', 'sure', 'go ahead',
                          'sunao', 'bolo', 'continue', 'aur batao',
                          'phir', 'aage batao']
    if t.strip() in short_affirmatives or t.strip().startswith('haan '):
        return 'conversation'
    
    code_triggers = [
        'code', 'program', 'write', 'likh', 'banao', 'bana',
        'explain', 'samjhao', 'tutorial', 'kaise', 'how to',
        'error', 'debug', 'fix', 'function', 'class', 'loop',
        'algorithm', 'c++', 'python', 'java', 'javascript',
        'html', 'css', 'sql', 'react', 'node', 'api',
    ]
    if any(trigger in t for trigger in code_triggers):
        return 'conversation'
    
    command_starters = [
        'open', 'close', 'play', 'pause', 'stop', 'next', 'previous',
        'minimize', 'maximize', 'restore', 'focus', 'volume', 'mute',
        'unmute', 'search', 'send', 'type', 'set', 'increase', 'decrease',
        'kholo', 'khol', 'band', 'bandh', 'bajao', 'chalaao', 'chalao',
        'roko', 'rok', 'agla', 'pichla', 'hatao', 'hata', 'bund',
        'dikhao', 'lao', 'badhaao', 'badhao', 'ghatao', 'tej', 'dhima',
    ]
    
    conversation_starters = [
        'what', 'who', 'why', 'how', 'when', 'where', 'which',
        'tell me', 'explain', 'describe', 'can you', 'do you',
        'kya', 'kaun', 'kaise', 'kyun', 'kab', 'kahan',
        'nahi', 'thanks', 'thank',
        'hmm', 'interesting', 'really', 'nice', 'good', 'bad',
        'samjhao', 'bolo', 'suno',
    ]
    
    conversation_triggers = [
        'batao', 'bata', 'samjhao', 'samjha', 'sunao', 'suna',
        'explain', 'tell', 'describe', 'what is', 'who is',
        'kya hai', 'kaun hai', 'kaise', 'kyun', 'kab', 'kahan',
        'detail', 'puri kahani', 'full story', 'history', 'about',
    ]
    
    news_web_keywords = [
        'news', 'weather', 'mausam', 'khabar', 'latest', 'aaj ka',
        'today', 'current', 'live', 'update', 'happened', 
        'kya hua', 'tell me about',
        'kaisa hai', 'kya hai', 'kahan hai',
    ]
    
    words = t.split()
    first_word = words[0] if words else ''
    
    if first_word in command_starters:
        return 'command'
    
    app_names = ['spotify', 'chrome', 'youtube', 'whatsapp', 'notepad',
                 'vlc', 'explorer', 'file explorer', 'claude', 'discord']
    has_app = any(app in t for app in app_names)
    has_action = any(word in t for word in command_starters)
    if has_app and has_action:
        return 'command'
    
    has_info_keyword = any(kw in t for kw in news_web_keywords)
    if has_info_keyword and not has_app:
        return 'web_search'
    
    has_conv_trigger = any(tr in t for tr in conversation_triggers)
    has_file_action = any(t.startswith(v) for v in 
                         ['open ', 'close ', 'play ', 'pause '])
    if has_conv_trigger and not has_app and not has_file_action:
        return 'conversation'
    
    if first_word in conversation_starters:
        return 'conversation'
    
    if '?' in text:
        return 'conversation'
    
    return 'command'


def call_cerebras_command(user_input: str) -> dict:
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    command_prompt = """You are a command parser. Convert user input to JSON.
Return ONLY valid JSON, nothing else.

FORMAT: {"type":"command","action":"<verb>","target":"<what>","app":"<app>","arg":"<extra>"}

ACTIONS: open, close, minimize, maximize, restore, focus, play, pause, next, 
previous, play_song, search_youtube, whatsapp_message, type_text, 
set_volume, mute, unmute, increase, decrease, web_search

RULES:
- If query asks for weather/news/facts WITHOUT app name → action=web_search
- "weather", "news", "khabar", "mausam" without app → web_search
- youtube/chrome + search → search_youtube

HINDI MAPPINGS:
band/bandh/hatao/bund = close
kholo/chalao/chalaao = open  
bajao/sunao = play_song (if song name present)
agla = next, pichla = previous
badhaao/tej = increase volume, ghatao/dhima = decrease volume

EXAMPLES:
"open spotify" → {"type":"command","action":"open","target":"spotify","app":"","arg":""}
"spotify band karo" → {"type":"command","action":"close","target":"spotify","app":"","arg":""}
"play life in rio on spotify" → {"type":"command","action":"play_song","target":"spotify","app":"spotify","arg":"life in rio"}
"search python on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python"}
"indore weather" → {"type":"command","action":"web_search","target":"","app":"","arg":"indore weather"}
"iran vs us war news" → {"type":"command","action":"web_search","target":"","app":"","arg":"iran us war news"}
"file explorer band karo" → {"type":"command","action":"close","target":"file explorer","app":"","arg":""}
"""
    
    body = {
        "model": COMMAND_MODEL_CEREBRAS,
        "messages": [
            {"role": "system", "content": command_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.0,
        "max_tokens": 200
    }
    r = requests.post(url, json=body, headers=headers, timeout=10)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    if "{" in text and "}" in text:
        text = text[text.index("{"):text.rindex("}")+1]
    return json.loads(text)


def call_groq_conversation(user_input: str, 
                            history: list = None) -> dict:
    if not GROQ_API_KEY:
        raise Exception("Groq API key not set")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    conversation_prompt = """You are JARVIS, a smart casual AI assistant 
built by your creator. Never say you are any AI model.
Reply in same language as user — Hindi → Hinglish, English → English.
For code: give complete working code with explanation.
For stories: give full detailed answer, don't stop midway.
For questions: give accurate factual answer.
Be helpful, friendly, like a smart friend.

IMPORTANT: If user asks 'kya tum X kar sakte ho' or 'can you X',
DO NOT ask for confirmation. Just DO X immediately.
Example: 'kya tum c++ code likh sakte ho' → write the c++ code directly."""
    
    messages = [{"role": "system", "content": conversation_prompt}]
    if history:
        messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_input})
    
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4000
    }
    r = requests.post(url, json=body, headers=headers, timeout=20)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    return {"type": "conversation", "reply": text}


def call_openrouter_conversation(user_input: str,
                                  history: list = None) -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis.local",
        "X-Title": "Jarvis"
    }
    
    conversation_prompt = """You are JARVIS, a smart casual AI assistant
built by your creator. Never say you are any AI model.
Reply in same language as user — Hindi → Hinglish, English → English.
For code: give complete working code with explanation.
For stories: give full detailed answer.
For questions: give accurate factual answer.
Be helpful and friendly.

IMPORTANT: If user asks 'kya tum X kar sakte ho' or 'can you X',
DO NOT ask for confirmation. Just DO X immediately.
Example: 'kya tum c++ code likh sakte ho' → write the c++ code directly."""
    
    messages = [{"role": "system", "content": conversation_prompt}]
    if history:
        messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_input})
    
    FREE_MODELS = [
        "openai/gpt-oss-120b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "qwen/qwen3-4b:free",
    ]
    
    for model in FREE_MODELS:
        try:
            body = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4000
            }
            r = requests.post(url, json=body, headers=headers, timeout=20)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"].strip()
                if text:
                    return {"type": "conversation", "reply": text}
        except Exception:
            continue
    
    raise Exception("All OpenRouter models failed")


_conversation_history = []

def think(user_input: str) -> dict:
    global _conversation_history
    
    input_type = classify_input(user_input)
    
    if input_type == 'command':
        providers = [
            ("Cerebras", call_cerebras_command),
            ("SambaNova", call_sambanova),
            ("OpenRouter", call_openrouter),
            ("Ollama", call_ollama),
        ]
        for name, fn in providers:
            try:
                result = fn(user_input)
                if isinstance(result, dict) and "type" in result:
                    print(f"[Brain:{name}]", end=" ")
                    if result.get("action") == "raw" and result.get("target"):
                        raw_target = result.get("target", "")
                        input_type = "conversation"
                        user_input = raw_target
                        break
                    return result
            except Exception as e:
                continue
    
    if input_type == 'web_search':
        try:
            from ddgs import DDGS
            raw_results = list(DDGS().text(user_input, max_results=5))
        except Exception as e:
            raw_results = []
        
        if not raw_results:
            input_type = 'conversation'
        else:
            formatted = ""
            for i, r in enumerate(raw_results, 1):
                formatted += f"SOURCE {i}: {r['title']}\n"
                formatted += f"CONTENT: {r['body']}\n"
                formatted += f"URL: {r['href']}\n\n"
            
            summary_prompt = f"""The user asked: "{user_input}"

I searched the web and found these REAL results:

{formatted}

INSTRUCTIONS:
- Answer ONLY using the information in these search results above
- Do NOT use your training knowledge
- Reply in same language as the user's question
- Be concise — max 4 sentences
- If results contain specific numbers/facts, include them
- Start directly with the answer, no preamble"""
            
            providers = [
                ("Groq", lambda x: call_groq_conversation(x)),
                ("OpenRouter", lambda x: call_openrouter_conversation(x)),
                ("SambaNova", call_sambanova),
                ("Cerebras", call_cerebras),
                ("Ollama", call_ollama),
            ]
            
            for name, fn in providers:
                try:
                    result = fn(summary_prompt)
                    if isinstance(result, dict):
                        if result.get('type') == 'conversation':
                            print(f"[Brain:{name}]", end=" ")
                            return result
                        elif result.get('type') == 'command':
                            reply = result.get('target', '') or result.get('arg', '')
                            if reply:
                                print(f"[Brain:{name}]", end=" ")
                                return {"type": "conversation", "reply": reply}
                except Exception:
                    continue
            
            answer = f"Web search results for '{user_input}':\n"
            for r in raw_results[:3]:
                answer += f"• {r['title']}: {r['body'][:100]}\n"
            return {"type": "conversation", "reply": answer}
    
    if input_type == 'web_search':
        input_type = 'conversation'
    
    if input_type == 'conversation':
        _conversation_history.append({
            "role": "user", "content": user_input
        })
        
        providers = [
            ("Groq", lambda x: call_groq_conversation(
                x, _conversation_history)),
            ("OpenRouter", lambda x: call_openrouter_conversation(
                x, _conversation_history)),
            ("SambaNova", call_sambanova),
            ("Cerebras", call_cerebras),
            ("Ollama", call_ollama),
        ]
        for name, fn in providers:
            try:
                result = fn(user_input)
                if isinstance(result, dict) and "type" in result:
                    if result["type"] == "conversation":
                        _conversation_history.append({
                            "role": "assistant",
                            "content": result.get("reply", "")
                        })
                        if len(_conversation_history) > 20:
                            _conversation_history = _conversation_history[-20:]
                    print(f"[Brain:{name}]", end=" ")
                    return result
            except Exception as e:
                continue
    
    print("[Brain:raw]", end=" ")
    return {
        "type": "command",
        "action": "raw",
        "target": user_input,
        "app": "",
        "arg": ""
    }
