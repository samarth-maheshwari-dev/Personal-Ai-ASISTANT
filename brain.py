import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434"

COMMAND_MODEL_CEREBRAS = "llama3.1-8b"
CONVERSATION_MODEL_OPENROUTER = "meta-llama/llama-3.3-70b-instruct:free"

SYSTEM_PROMPT = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."


def classify_query(self, user_input):
    """Classify query into one of: command, chat, code, math, factual, educational"""
    import re
    text = user_input.lower().strip()

    # STEP 0 — Identity questions → always chat
    identity_phrases = [
        "who are you", "who are u", "who made you", "who made u", "what are you", "who created you",
        "who built you", "your name", "tumhara naam", "tum kaun ho",
        "kisne banaya", "aapko kisne", "who is jarvis", "introduce yourself",
        "what is your name", "tell me about yourself"
    ]
    if any(phrase in text for phrase in identity_phrases):
        return "chat"

    # STEP 0B — Fun/jokes → chat
    fun_phrases = [
        "joke", "jokes", "funny", "mazaak", "hasao", "comedy", "chutkula",
        "chutkule", "laugh", "mujhe hasao", "koi joke", "sunao joke"
    ]
    if any(phrase in text for phrase in fun_phrases):
        return "chat"

    # STEP 0C — Simple math like "2+2", "5*6" → math
    # This MUST come before question starters to catch "what is 5*6"
    import re
    if re.search(r'\d+\s*[\+\-\*\/\^]\s*\d+', text):
        return "math"

    # STEP 1 — Hard command keywords (ALWAYS command, no exception)
    command_keywords = [
        "open ", "close ", "minimize", "maximize", "restore",
        "volume up", "volume down", "mute", "unmute",
        "play ", "pause", "search on youtube", "open chrome",
        "shutdown", "restart", "band karo", "kholo", "chalu karo",
        "bnd karo", "focus ", "switch to"
    ]
    
    # Special patterns for flexible matching
    if "youtube" in text and ("search" in text or "search on" in text):
        return "command"
    for kw in command_keywords:
        if kw in text:
            return "command"

    # STEP 2 — Hard question indicators (NEVER command)
    question_starters = [
        "what", "why", "how", "when", "where", "who", "which",
        "explain", "define", "tell me", "describe",
        "what is", "what are", "can you"
    ]
    hindi_question_starters = [
        "kya", "kaisa", "kaun", "kab", "kyun", "kahan", "batao", "samjhao", "bolo"
    ]
    for starter in question_starters:
        if text.startswith(starter):
            # route to correct type
            if any(w in text for w in ["weather", "date", "today", "news",
                                        "current", "latest", "price", "score"]):
                return "factual"
            if any(w in text for w in ["code", "program", "function", "bug",
                                        "error", "write a", "implement"]):
                return "code"
            if any(w in text for w in ["calculate", "solve", "sequence",
                                        "next number", "pattern", "equation"]):
                return "math"
            return "educational"
    
    # Handle Hindi/Hinglish question starters → chat
    for starter in hindi_question_starters:
        if text.startswith(starter):
            return "chat"

    # STEP 3 — Math/Puzzle/Riddle detection
    math_indicators = [
        "next number", "sequence", "find the", "solve", "calculate",
        "missing", "rupee", "puzzle", "riddle", "trick question",
        "next term", "pattern", "?", "sum of", "product of", "₹",
        "pay", "each", "total", "average", "divide", "share"
    ]
    if any(ind in text for ind in math_indicators):
        return "math"

    # Comma-separated numbers = sequence = math
    import re
    if re.search(r'\d+\s*,\s*\d+\s*,\s*\d+', text):
        return "math"

    # Math operators
    if any(op in text for op in ["+", "-", "*", "/", "^", "√", "="]):
        if any(c.isdigit() for c in text):
            return "math"

    # Simple arithmetic like "2+2" or "5*6" → math
    import re
    if re.search(r'\d+\s*[\+\-\*\/\^]\s*\d+', text):
        return "math"

    # STEP 4 — Educational/CS/Electronics terms
    educational_terms = [
        "flipflop", "flip flop", "transistor", "resistor", "capacitor",
        "algorithm", "recursion", "binary", "sorting", "neural", "voltage",
        "circuit", "diode", "ohm", "frequency", "wavelength", "force",
        "momentum", "entropy", "quantum", "photon", "derivative", "integral",
        "matrix", "vector", "tensor", "stack", "queue", "graph", "tree",
        "linked list", "pointer", "memory", "cpu", "os", "kernel",
        "process", "thread", "mutex", "semaphore", "osi", "tcp", "http"
    ]
    if any(term in text for term in educational_terms):
        return "educational"

    # STEP 5 — Code detection
    code_terms = [
        "code", "program", "function", "class", "debug", "error",
        "implement", "write a script", "python", "javascript", "java",
        "c++", "array", "string", "loop", "if else", "api", "sql"
    ]
    if any(term in text for term in code_terms):
        return "code"

    # STEP 6 — Factual detection
    factual_terms = [
        "weather", "temperature", "today", "date", "time", "news",
        "current", "latest", "who is", "where is", "capital of",
        "population", "price", "score", "result", "live"
    ]
    if any(term in text for term in factual_terms):
        return "factual"

    # STEP 7 — Hindi/Hinglish detection → chat
    hindi_words = [
        "karo", "kar", "hai", "hain", "tha", "thi", "ho", "hoga",
        "kya", "nahi", "aur", "yeh", "voh", "mera", "tera", "humara",
        "theek", "accha", "bilkul", "zaroor", "shukriya", "namaste"
    ]
    hindi_count = sum(1 for w in hindi_words if w in text.split())
    if hindi_count >= 1:
        return "chat"  # Will be detected as Hinglish in router

    # DEFAULT — never return "command" if unsure
    return "chat"


def detect_language(self, user_input):
    """Detect if input is english, hindi, or hinglish"""
    text = user_input.lower()
    hindi_words = [
        "karo", "kar", "hai", "hain", "tha", "thi", "kya", "nahi",
        "aur", "yeh", "voh", "mera", "tera", "theek", "accha",
        "batao", "samjhao", "bolo", "kyun", "kahan", "kaisa", "kaun",
        "hoga", "chahiye", "lagta", "suno", "dekho", "bol", "sun"
    ]
    hindi_count = sum(1 for w in hindi_words if w in text.split())
    # Also check for Devanagari characters
    devanagari = any('\u0900' <= c <= '\u097f' for c in user_input)
    if devanagari or hindi_count >= 2:
        return "hindi"
    elif hindi_count == 1:
        return "hinglish"
    return "english"


def validate_response(self, response):
    """Validate that a response is good quality"""
    if not response:
        return False
    if len(response.strip().split()) < 3:
        return False
    bad_phrases = [
        "i cannot", "i don't know", "as an ai",
        "i am not able", "i'm not able", "i can't"
    ]
    lower = response.lower()
    if any(phrase in lower for phrase in bad_phrases):
        return False
    stripped = response.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return False
    return True


def perform_web_search(self, query):
    """Perform web search and return raw results"""
    try:
        from ddgs import DDGS
        # Add context to query for better results
        enhanced_query = query
        
        # Add location context for common queries
        if 'weather' in query.lower():
            enhanced_query = query + " Indore"
        
        raw_results = list(DDGS().text(enhanced_query, max_results=5))
        if raw_results:
            formatted = ""
            for i, r in enumerate(raw_results, 1):
                formatted += f"SOURCE {i}: {r['title']}\n"
                formatted += f"CONTENT: {r['body']}\n"
                formatted += f"URL: {r['href']}\n\n"
            return formatted
    except Exception as e:
        print(f"[WebSearch] Failed: {e}")
    return None


def call_openrouter_summarize(self, search_results, user_query):
    """Summarize web search results using OpenRouter"""
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    summary_prompt = f"""Today's date is {current_date}.

The user asked: "{user_query}"

I searched the web and found these REAL results:

{search_results}

INSTRUCTIONS:
- Today's date is {current_date}. Use this to determine if information is current.
- Answer ONLY using the information in these search results above
- Do NOT use your training knowledge
- Reply in same language as the user's question
- Be concise — max 4 sentences
- If results contain specific numbers/facts, include them
- Start directly with the answer, no preamble"""
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis.local",
        "X-Title": "JARVIS"
    }
    body = {
        "model": "qwen/qwen3.6-plus-preview:free",
        "messages": [{"role": "user", "content": summary_prompt}],
        "temperature": 0.1,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return text
    except Exception as e:
        print(f"[OpenRouter Summarize] Failed: {e}")
        return None


def call_cerebras(self, messages, system_prompt):
    """Call Cerebras API with messages"""
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3.1-8b",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[Cerebras error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not text:
            print(f"[Cerebras] Empty response")
            return None
        return text
    except requests.Timeout:
        print(f"[Cerebras] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Cerebras] Connection error")
        return None
    except Exception as e:
        print(f"[Cerebras] Failed: {e}")
        return None


def call_sambanova(self, messages, system_prompt):
    """Call SambaNova API with messages"""
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {SAMBANOVA_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "Meta-Llama-3.3-70B-Instruct",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[SambaNova error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not text:
            print(f"[SambaNova] Empty response")
            return None
        return text
    except requests.Timeout:
        print(f"[SambaNova] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[SambaNova] Connection error")
        return None
    except Exception as e:
        print(f"[SambaNova] Failed: {e}")
        return None


def call_nvidia_nemotron(self, messages, system_prompt):
    """Call NVIDIA Nemotron API with messages"""
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "nvidia/nemotron-3-super-120b-a12b",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"[NVIDIA Nemotron error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not text:
            print(f"[NVIDIA Nemotron] Empty response")
            return None
        return text
    except requests.Timeout:
        print(f"[NVIDIA Nemotron] Timeout after 15s")
        return None
    except requests.ConnectionError:
        print(f"[NVIDIA Nemotron] Connection error")
        return None
    except Exception as e:
        print(f"[NVIDIA Nemotron] Failed: {e}")
        return None


def call_mistral(self, messages, system_prompt):
    """Call Mistral API with messages"""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistral-small-3.1-24b-instruct",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[Mistral error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not text:
            print(f"[Mistral] Empty response")
            return None
        return text
    except requests.Timeout:
        print(f"[Mistral] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Mistral] Connection error")
        return None
    except Exception as e:
        print(f"[Mistral] Failed: {e}")
        return None


def call_openrouter(self, messages, system_prompt):
    """Call OpenRouter API with messages"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis.local",
        "X-Title": "Jarvis"
    }
    body = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return text
    except requests.Timeout:
        print(f"[OpenRouter] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[OpenRouter] Connection error")
        return None
    except Exception as e:
        print(f"[OpenRouter] Failed: {e}")
        return None


def call_ollama(self, messages, system_prompt):
    """Call Ollama local model with messages"""
    url = f"{OLLAMA_URL}/api/generate"
    # Build prompt from messages
    prompt = system_prompt + "\n\n"
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"{role.title()}: {content}\n"
    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 300}
    }
    try:
        r = requests.post(url, json=body, timeout=8)
        r.raise_for_status()
        text = r.json()["response"].strip()
        return text
    except requests.Timeout:
        print(f"[Ollama] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Ollama] Connection error")
        return None
    except Exception as e:
        print(f"[Ollama] Failed: {e}")
        return None


def route_to_best_model(self, query_type, user_input, messages):
    """Route query to best model based on type"""
    lang = self.detect_language(user_input)

    # --- SYSTEM PROMPTS per type ---
    prompts = {
        "chat_english":     "You are JARVIS, an AI assistant created by SAMARTH. You are NOT Samarth - you are the AI he built. When asked \"how are you\", say you are doing great as an AI 😊. Be SHORT (2-3 lines), witty, conversational. Use emojis.",
        "chat_hindi":       "Tum JARVIS ho, ek AI assistant jo Samarth ne banaya hai. Tum SAMARTH nahi ho. Jab puche \"kya haal hai\", toh bolo \"main ek AI hoon, theek hoon\" 😊. Natural bolo, 2-3 line.",
        "code":             "You are JARVIS. Write clean, working code with minimal comments. Brief explanation after code only. No unnecessary filler text.",
        "math":             "You are JARVIS. Think step by step, but keep it concise. For sequences: find pattern first, then apply. For puzzles/riddles: find the logical trick. Give the answer first, then brief explanation.",
        "educational":      "You are JARVIS. Explain clearly in 3-5 lines max. Use one example if needed. No lengthy lectures. Sound like a smart friend explaining, not a professor.",
        "factual":         "You are JARVIS. Give factual, direct answer based on search results. Be brief.",
    }

    # --- ROUTING TABLE ---
    # Each entry: (system_prompt_key, [ordered provider functions])

    if query_type == "command":
        return None  # Let existing command handler take it

    elif query_type == "chat":
        sp = "chat_hindi" if lang in ["hindi", "hinglish"] else "chat_english"
        providers = [
            ("Cerebras", self.call_cerebras),
            ("Mistral", self.call_mistral),
            ("SambaNova", self.call_sambanova),
            ("OpenRouter", self.call_openrouter),
            ("Ollama", self.call_ollama)
        ]

    elif query_type == "code":
        sp = "code"
        providers = [
            ("SambaNova", self.call_sambanova),
            ("Cerebras", self.call_cerebras),
            ("NVIDIA Nemotron", self.call_nvidia_nemotron),
            ("OpenRouter", self.call_openrouter),
            ("Ollama", self.call_ollama)
        ]

    elif query_type == "math":
        sp = "math"
        providers = [
            ("NVIDIA Nemotron", self.call_nvidia_nemotron),
            ("SambaNova", self.call_sambanova),
            ("Mistral", self.call_mistral),
            ("OpenRouter", self.call_openrouter),
            ("Ollama", self.call_ollama)
        ]

    elif query_type == "educational":
        sp = "educational"
        providers = [
            ("Cerebras", self.call_cerebras),
            ("Mistral", self.call_mistral),
            ("SambaNova", self.call_sambanova),
            ("NVIDIA Nemotron", self.call_nvidia_nemotron),
            ("Ollama", self.call_ollama)
        ]

    elif query_type == "factual":
        sp = "factual"
        # Web search FIRST — no LLM for factual
        web_result = self.perform_web_search(user_input)
        if web_result:
            summary = self.call_openrouter_summarize(web_result, user_input)
            if summary:
                return {"type": "conversation", "reply": summary, "provider": "OpenRouter"}
        # If web fails, fallback to LLMs
        providers = [
            ("Cerebras", self.call_cerebras),
            ("SambaNova", self.call_sambanova),
            ("Mistral", self.call_mistral),
            ("Ollama", self.call_ollama)
        ]

    else:
        sp = "chat_english"
        providers = [("Cerebras", self.call_cerebras), ("SambaNova", self.call_sambanova), ("Ollama", self.call_ollama)]

    system_prompt = prompts.get(sp, prompts["chat_english"])

    # --- EXECUTE CHAIN ---
    for provider_name, provider in providers:
        try:
            result = provider(messages, system_prompt)
            if self.validate_response(result):
                print(f"[{provider_name}] Responding...")
                # Return as dict with provider info for jarvis.py compatibility
                return {"type": "conversation", "reply": result, "provider": provider_name}
        except Exception as e:
            print(f"[{provider_name}] Failed: {e}")
            continue

    return {"type": "conversation", "reply": "I'm having trouble connecting right now. Please try again.", "provider": "None"}


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
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[SambaNova error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except requests.Timeout:
        print(f"[SambaNova] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[SambaNova] Connection error")
        return None
    except Exception as e:
        print(f"[SambaNova] Failed: {e}")
        return None
    if not text:
        print(f"[SambaNova] Empty response")
        return None
    # Check if response is JSON command or plain text
    if text.startswith("{") and "}" in text:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            json_str = text[start:end]
            result = json.loads(json_str)
            if result.get("type") == "command":
                return result
        except:
            pass
    # Return as conversation
    return {"type": "conversation", "reply": text}


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
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[Cerebras error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except requests.Timeout:
        print(f"[Cerebras] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Cerebras] Connection error")
        return None
    except Exception as e:
        print(f"[Cerebras] Failed: {e}")
        return None
    if not text:
        print(f"[Cerebras] Empty response")
        return None
    # Check if response is JSON command or plain text
    if text.startswith("{") and "}" in text:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            json_str = text[start:end]
            result = json.loads(json_str)
            if result.get("type") == "command":
                return result
        except:
            pass
    # Return as conversation
    return {"type": "conversation", "reply": text}


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
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
    except requests.Timeout:
        print(f"[OpenRouter] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[OpenRouter] Connection error")
        return None
    except Exception as e:
        print(f"[OpenRouter] Failed: {e}")
        return None
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    if "{" in text and "}" in text:
        start = text.index("{")
        depth = 0
        end = start
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
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
    try:
        r = requests.post(url, json=body, timeout=8)
        r.raise_for_status()
        text = r.json()["response"].strip()
    except requests.Timeout:
        print(f"[Ollama] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Ollama] Connection error")
        return None
    except Exception as e:
        print(f"[Ollama] Failed: {e}")
        return None
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    if "{" in text and "}" in text:
        start = text.index("{")
        depth = 0
        end = start
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        text = text[start:end]
    return json.loads(text)


def call_openrouter_command(user_input: str) -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis.local",
        "X-Title": "Jarvis"
    }
    command_prompt = """You are a Windows PC command parser.
Output ONLY one valid JSON object. No code. No explanation. Ever.

FORMAT: {"type":"command","action":"<action>","target":"<target>","app":"<app>","arg":"<arg>"}

CRITICAL: "calculator" = Windows app. NEVER write calculator code.
CRITICAL: If input has "then/aur/phir" → process FIRST action only.
CRITICAL: NEVER output anything except one JSON object.

band/bandh/hatao = close
kholo/chalao = open
minimize/chota = minimize
maximize/bada = maximize
restore = restore
focus = focus
If no app name → target=""

EXAMPLES:
"calculator kholo" → {"type":"command","action":"open","target":"calculator","app":"","arg":""}
"band karo" → {"type":"command","action":"close","target":"","app":"","arg":""}
"maximize karo" → {"type":"command","action":"maximize","target":"","app":"","arg":""}
"calculator kholo phir maximize karo" → {"type":"command","action":"open","target":"calculator","app":"","arg":""}
"notepad band karo" → {"type":"command","action":"close","target":"notepad","app":"","arg":""}
"chrome kholo" → {"type":"command","action":"open","target":"chrome","app":"","arg":""}
"play shape of you on spotify" → {"type":"command","action":"play_song","target":"spotify","app":"spotify","arg":"shape of you"}
"search python on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python"}
    "search code with harry on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"code with harry"}
    "search lofi music on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"lofi music"}
    "search python tutorial for beginners on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python tutorial for beginners"}
    "next on spotify" → {"type":"command","action":"next","target":"spotify","app":"spotify","arg":""}
    "pause on spotify" → {"type":"command","action":"pause","target":"spotify","app":"spotify","arg":""}
    "previous on spotify" → {"type":"command","action":"previous","target":"spotify","app":"spotify","arg":""}
    "play on spotify" → {"type":"command","action":"play","target":"spotify","app":"spotify","arg":""}"""

    FREE_MODELS = [
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "qwen/qwen3-4b:free",
    ]
    for model in FREE_MODELS:
        try:
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": command_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.0,
                "max_tokens": 150
            }
            r = requests.post(url, json=body, headers=headers, timeout=8)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"].strip()
                if "{" in text and "}" in text:
                    start = text.index("{")
                    depth = 0
                    end = start
                    for i, ch in enumerate(text[start:], start):
                        if ch == "{": depth += 1
                        elif ch == "}":
                            depth -= 1
                            if depth == 0:
                                end = i + 1
                                break
                    text = text[start:end]
                return json.loads(text)
        except Exception:
            continue
    raise Exception("OpenRouter command failed")


def classify_input(text: str) -> str:
    t = text.lower().strip()
    
    if ' then ' in t or ' phir ' in t or ' aur ' in t or ' and ' in t:
        import re
        first_part = re.split(r'\s+then\s+|\s+phir\s+|\s+aur\s+|\s+and\s+', t)[0]
        return classify_input(first_part)
    
    app_command_patterns = [
        'band karo', 'band kar', 'close karo', 'hatao',
        'minimize karo', 'maximize karo', 'focus karo',
        'restore karo', 'chota karo', 'bada karo',
    ]
    if any(p in t for p in app_command_patterns):
        return 'command'
    
    if t.startswith('memory'):
        return 'command'
    
    # BLOCK 1 — App name present + action word = always command
    app_names = [
        'calculator', 'notepad', 'chrome', 'spotify', 'whatsapp',
        'youtube', 'settings', 'explorer', 'file explorer', 'vlc',
        'discord', 'telegram', 'instagram', 'paint', 'camera',
        'teams', 'word', 'excel', 'powerpoint', 'antigravity',
    ]
    hinglish_actions = [
        'kholo', 'band', 'karo', 'minimize', 'maximize',
        'focus', 'restore', 'chalao', 'hatao', 'khul', 'bandh',
        'open', 'close', 'start', 'launch',
    ]
    
    has_app = any(app in t for app in app_names)
    has_action = any(action in t for action in hinglish_actions)
    
    if has_app and has_action:
        return 'command'
    
    # Also: first word is app name = command
    first_word = t.split()[0] if t.split() else ''
    if first_word in app_names:
        return 'command'
    
    # Music commands → always command, never conversation
    music_patterns = [
        'play ', 'bajao', 'suno', 'gaana', 'song', 'music',
        'on spotify', 'spotify pe', 'on youtube', 'youtube pe',
    ]
    # But exclude "play next/previous" which are media controls
    if any(p in t for p in music_patterns):
        if 'next' not in t and 'previous' not in t and 'prev' not in t:
            return 'command'
    
    # HIGHEST PRIORITY: YouTube/search patterns → always command
    youtube_patterns = [
        'search', 'dhundho', 'dhundo', 'find',
        'youtube pe', 'youtube par', 'youtube mein',
        'on youtube', 'yt pe', 'play on youtube',
        'video lagao', 'video chalao', 'video dikhao',
    ]
    if any(p in t for p in youtube_patterns):
        return 'command'
    
    # HIGHEST PRIORITY: Specific app commands → always command
    app_command_patterns = [
        'band karo', 'band kar', 'kholna', 'kholo',
        'minimize karo', 'maximize karo', 'focus karo',
        'close karo', 'open karo', 'start karo',
    ]
    if any(p in t for p in app_command_patterns):
        return 'command'

    greetings = ['hi', 'hello', 'hey', 'hii', 'helo', 'sup',
                 'yo', 'namaste', 'namaskar', 'jai shri ram',
                 'good morning', 'good evening', 'good night',
                 'gm', 'gn', 'bye', 'goodbye', 'alvida']
    if t.strip() in greetings:
        return 'conversation'
    
    if any(t.startswith(g) for g in ['hi ', 'hello ', 'hey ']):
        return 'conversation'
    
    youtube_search_patterns = [
        'search on youtube', 'youtube pe search',
        'youtube mein search', 'search youtube',
        'youtube par search', 'yt pe search',
    ]
    if any(p in t for p in youtube_search_patterns):
        return 'command'
    
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
    
    command_prompt = """You are a command parser for a Windows PC assistant.
Your ONLY job is to convert user input into JSON.
You NEVER write code. You NEVER explain anything.
You ONLY output a single valid JSON object.

OUTPUT FORMAT:
{"type":"command","action":"<action>","target":"<target>","app":"<app>","arg":"<arg>"}

ACTIONS LIST:
open, close, minimize, maximize, restore, focus, play, pause, 
next, previous, play_song, search_youtube, web_search,
increase, decrease, mute, unmute, set_volume

CRITICAL RULES:
1. NEVER write Python code or any code
2. NEVER explain anything
3. ALWAYS output ONLY one JSON object
4. If input has "then/aur/phir" — process FIRST action only
5. "calculator" is a Windows app name, NOT a coding request
6. "band/bandh/hatao" = close action
7. "kholo/chalaao" = open action
8. "minimize/chota karo" = minimize action
9. "maximize/bada karo" = maximize action
10. If no app name given → target=""

HINDI/HINGLISH MAPPINGS:
band/bandh/hatao/bund → close
kholo/chalao/chalu/khole → open
bajao/sunao → play_song
agla → next
pichla → previous
badhaao/tej → increase
ghatao/dhima → decrease

EXAMPLES:
"chrome kholo" → {"type":"command","action":"open","target":"chrome","app":"","arg":""}
"notepad band karo" → {"type":"command","action":"close","target":"notepad","app":"","arg":""}
"calculator kholo" → {"type":"command","action":"open","target":"calculator","app":"","arg":""}
"minimize karo" → {"type":"command","action":"minimize","target":"","app":"","arg":""}
"maximize karo" → {"type":"command","action":"maximize","target":"","app":"","arg":""}
"band karo" → {"type":"command","action":"close","target":"","app":"","arg":""}
"calculator kholo then minimize karo" → {"type":"command","action":"open","target":"calculator","app":"","arg":""}
"open spotify.com" → {"type":"command","action":"open","target":"https://spotify.com","app":"chrome","arg":""}
"play shape of you on spotify" → {"type":"command","action":"play_song","target":"spotify","app":"spotify","arg":"shape of you"}
"search python on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python"}
"search code with harry on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"code with harry"}
"search lofi music on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"lofi music"}
"search python tutorial for beginners on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python tutorial for beginners"}
"next on spotify" → {"type":"command","action":"next","target":"spotify","app":"spotify","arg":""}
"pause on spotify" → {"type":"command","action":"pause","target":"spotify","app":"spotify","arg":""}
"previous on spotify" → {"type":"command","action":"previous","target":"spotify","app":"spotify","arg":""}
"play on spotify" → {"type":"command","action":"play","target":"spotify","app":"spotify","arg":""}
"indore weather" → {"type":"command","action":"web_search","target":"","app":"","arg":"indore weather today"}
"awaaz badhaao" → {"type":"command","action":"increase","target":"volume","app":"","arg":""}
"awaaz band karo" → {"type":"command","action":"mute","target":"","app":"","arg":""}
"volume 40 karo" → {"type":"command","action":"set_volume","target":"40","app":"","arg":""}
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
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
    except requests.Timeout:
        print(f"[CerebrasCommand] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[CerebrasCommand] Connection error")
        return None
    except Exception as e:
        print(f"[CerebrasCommand] Failed: {e}")
        return None
    if "{" in text and "}" in text:
        start = text.index("{")
        depth = 0
        end = start
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        text = text[start:end]
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
    
    conversation_prompt = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."
    
    messages = [{"role": "system", "content": conversation_prompt}]
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": user_input})
    
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4000
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
    except requests.Timeout:
        print(f"[Groq] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Groq] Connection error")
        return None
    except Exception as e:
        print(f"[Groq] Failed: {e}")
        return None
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
    
    conversation_prompt = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."
    
    messages = [{"role": "system", "content": conversation_prompt}]
    if history:
        messages.extend(history[-4:])
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
                "max_tokens": 2000
            }
            r = requests.post(url, json=body, headers=headers, timeout=8)
            if r.status_code == 200:
                try:
                    data = r.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    if text:
                        return {"type": "conversation", "reply": text}
                except Exception as e:
                    print(f"[OpenRouter parse error] {e}")
                    continue
        except requests.Timeout:
            print(f"[OpenRouterConv] Timeout after 8s")
            continue
        except requests.ConnectionError:
            print(f"[OpenRouterConv] Connection error")
            continue
        except Exception as e:
            print(f"[OpenRouterConv] Failed: {e}")
            continue
    
    raise Exception("All OpenRouter models failed")


def call_nvidia(user_input: str, history: list = None) -> dict:
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    conversation_prompt = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."
    
    messages = [{"role": "system", "content": conversation_prompt}]
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": user_input})
    
    body = {
        "model": "nvidia/nemotron-3-super-120b-a12b",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[NVIDIA error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except requests.Timeout:
        print(f"[NVIDIA] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[NVIDIA] Connection error")
        return None
    except Exception as e:
        print(f"[NVIDIA] Failed: {e}")
        return None
    if not text:
        print(f"[NVIDIA] Empty response")
        return None
    return {"type": "conversation", "reply": text}


def call_mistral(user_input: str, history: list = None) -> dict:
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    conversation_prompt = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."
    
    messages = [{"role": "system", "content": conversation_prompt}]
    if history:
        messages.extend(history[-4:])
    messages.append({"role": "user", "content": user_input})
    
    body = {
        "model": "mistral-small-3.1-24b-instruct",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"[Mistral error] Status {r.status_code}: {r.text[:100]}")
            return None
        r.raise_for_status()
        data = r.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except requests.Timeout:
        print(f"[Mistral] Timeout after 8s")
        return None
    except requests.ConnectionError:
        print(f"[Mistral] Connection error")
        return None
    except Exception as e:
        print(f"[Mistral] Failed: {e}")
        return None
    if not text:
        print(f"[Mistral] Empty response")
        return None
    return {"type": "conversation", "reply": text}


def call_cerebras_summarize(search_results: str, user_query: str) -> str:
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    prompt = f"""Today is {current_date}.
User asked: "{user_query}"

Web search results:
{search_results}

STRICT RULES:
- Answer ONLY from these results. Zero guessing.
- 2-3 sentences max. Be direct.
- Include specific numbers/facts if present in results.
- If results have no clear answer, say exactly: "I couldn't find a clear answer from current sources."
- Match the language of the user's question (Hindi question = Hindi answer, English = English)."""

    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CEREBRAS_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama3.1-8b",
        "messages": [
            {"role": "system", "content": "You are a factual assistant. Summarize only from the provided search data. Never guess."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 250
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        print(f"[CerebrasSum] Status {r.status_code}")
        return None
    except Exception as e:
        print(f"[CerebrasSum] Failed: {e}")
        return None


def filter_search_results(raw_results: list) -> list:
    if not raw_results:
        return []
    filtered = []
    seen_domains = set()
    for r in raw_results:
        body = r.get('body', '').strip()
        title = r.get('title', '').strip()
        url = r.get('href', '')
        if len(body) < 80:
            continue
        if not title:
            continue
        if url.lower().endswith(('.pdf', '.doc', '.ppt', '.docx')):
            continue
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
        except Exception:
            domain = url
        if domain in seen_domains:
            continue
        seen_domains.add(domain)
        filtered.append({
            'title': title,
            'body': body[:350],
            'source': domain
        })
    return filtered[:5]


def rephrase_for_retry(query: str) -> str:
    q = query.lower().strip()
    time_words = ['weather', 'price', 'rate', 'news', 'score',
                  'result', 'mausam', 'khabar', 'bhav', 'aaj']
    if any(w in q for w in time_words) and 'today' not in q:
        return query + " today"
    for prefix in ['what is ', 'what are ', 'tell me ',
                   'how much is ', 'batao ', 'bata ', 'kitna hai ']:
        if q.startswith(prefix):
            return query[len(prefix):]
    return query + " latest 2025"


def enhanced_web_search(user_query: str) -> str:
    try:
        from ddgs import DDGS

        search_query = user_query
        location_keywords = ['weather', 'mausam', 'temperature', 'garmi', 'sardi']
        if any(w in user_query.lower() for w in location_keywords):
            if 'indore' not in user_query.lower():
                search_query = user_query + " Indore"

        print(f"[WebSearch] Attempt 1: {search_query}")
        raw = list(DDGS().text(search_query, max_results=8))
        filtered = filter_search_results(raw)

        if len(filtered) < 2:
            retry_query = rephrase_for_retry(user_query)
            print(f"[WebSearch] Attempt 2: {retry_query}")
            try:
                raw2 = list(DDGS().text(retry_query, max_results=8))
                filtered2 = filter_search_results(raw2)
                seen = {r['source'] for r in filtered}
                for r in filtered2:
                    if r['source'] not in seen:
                        filtered.append(r)
            except Exception as retry_err:
                print(f"[WebSearch] Retry failed: {retry_err}")

        if not filtered:
            print("[WebSearch] No usable results after both attempts.")
            return None

        output = ""
        for i, r in enumerate(filtered, 1):
            output += f"SOURCE {i} [{r['source']}]:\n{r['title']}\n{r['body']}\n\n"
        return output.strip()

    except Exception as e:
        print(f"[WebSearch] Pipeline failed: {e}")
        return None


_conversation_history = []

def think(user_input: str) -> dict:
    global _conversation_history
    
    input_type = classify_input(user_input)
    
    if input_type == 'command':
        providers = [
            ("Cerebras", call_cerebras_command),
            ("SambaNova", call_sambanova),
            ("OpenRouter", call_openrouter_command),
            ("Ollama", call_ollama),
        ]
        for name, fn in providers:
            print(f"[Trying {name}...]")
            try:
                result = fn(user_input)
                if isinstance(result, dict) and "type" in result:
                    if result.get('type') == 'conversation':
                        reply = result.get('reply', '').strip()
                        if not reply:
                            continue
                        result['provider'] = name  # Track which provider gave answer
                        return result
                    if result.get("action") == "raw" and result.get("target"):
                        raw_target = result.get("target", "")
                        input_type = "conversation"
                        user_input = raw_target
                        break
                    result['provider'] = name
                    return result
            except Exception as e:
                print(f"[{name} failed] {e}")
                continue
    
    if input_type == 'web_search':
        print(f"[Web search for: {user_input}]")
        formatted_results = enhanced_web_search(user_input)
        if formatted_results:
            answer = call_cerebras_summarize(formatted_results, user_input)
            if answer:
                return {
                    "type": "conversation",
                    "reply": answer,
                    "provider": "Cerebras",
                    "source": "web_search"
                }
        print("[WebSearch] Both attempts failed, falling back to conversation.")
        input_type = 'conversation'
    
    if input_type == 'web_search':
        input_type = 'conversation'
    
    if input_type == 'conversation':
        _conversation_history.append({
            "role": "user", "content": user_input
        })
        
        providers = [
            ("Cerebras", call_cerebras),
            ("SambaNova", call_sambanova),
            ("NVIDIA", lambda x: call_nvidia(x, _conversation_history)),
            ("Mistral", lambda x: call_mistral(x, _conversation_history)),
            ("OpenRouter", lambda x: call_openrouter_conversation(
                x, _conversation_history)),
            ("Ollama", call_ollama),
        ]
        for name, fn in providers:
            print(f"[Trying {name}...]")
            try:
                result = fn(user_input)
                if result and isinstance(result, dict) and "type" in result:
                    if result["type"] == "conversation":
                        reply = result.get("reply", "").strip()
                        if not reply:
                            print(f"[{name} returned empty]")
                            continue
                        result['provider'] = name
                        result['source'] = 'conversation'
                        _conversation_history.append({
                            "role": "assistant",
                            "content": reply
                        })
                        if len(_conversation_history) > 20:
                            _conversation_history = _conversation_history[-20:]
                    return result
            except Exception as e:
                print(f"[{name} failed] {e}")
                continue
    
    return {
        "type": "command",
        "action": "raw",
        "target": user_input,
        "app": "",
        "arg": ""
    }


# ============================================================
# NEW: Class-based Brain with smart routing
# ============================================================

class Brain:
    """Smart brain with query classification and model routing"""
    
    def __init__(self):
        self.conversation_history = []
    
    def add_to_history(self, role, content):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        # Keep only last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def classify_query(self, user_input):
        """Classify query into one of: command, chat, code, math, factual, educational"""
        text = user_input.lower().strip()

        # STEP 0 — Identity questions → always chat
        identity_phrases = [
            "who are you", "who are u", "who made you", "who made u", "what are you", "who created you",
            "who built you", "your name", "tumhara naam", "tum kaun ho",
            "kisne banaya", "aapko kisne", "who is jarvis", "introduce yourself",
            "what is your name", "tell me about yourself"
        ]
        if any(phrase in text for phrase in identity_phrases):
            return "chat"

        # STEP 0B — Fun/jokes → chat
        fun_phrases = [
            "joke", "jokes", "funny", "mazaak", "hasao", "comedy", "chutkula",
            "chutkule", "laugh", "mujhe hasao", "koi joke", "sunao joke"
        ]
        if any(phrase in text for phrase in fun_phrases):
            return "chat"

        # STEP 0C — Simple math like "2+2", "5*6", "what is 5*6" → math
        # This MUST come before question starters to catch "what is 5*6"
        import re
        if re.search(r'\d+\s*[\+\-\*\/\^]\s*\d+', text):
            return "math"

        # STEP 1 — Hard command keywords (ALWAYS command, no exception)
        command_keywords = [
            "open ", "close ", "minimize", "maximize", "restore",
            "volume up", "volume down", "mute", "unmute",
            "play ", "pause", "search on youtube", "open chrome",
            "shutdown", "restart", "band karo", "kholo", "chalu karo",
            "bnd karo", "focus ", "switch to"
        ]
        
        # Special patterns for flexible matching
        if "youtube" in text and ("search" in text or "search on" in text):
            return "command"
        for kw in command_keywords:
            if kw in text:
                return "command"

        # STEP 2 — Hard question indicators (NEVER command)
        question_starters = [
            "what", "why", "how", "when", "where", "who", "which",
            "explain", "define", "tell me", "describe",
            "what is", "what are", "can you"
        ]
        hindi_question_starters = [
            "kya", "kaisa", "kaun", "kab", "kyun", "kahan", "batao", "samjhao", "bolo"
        ]
        for starter in question_starters:
            if text.startswith(starter):
                # route to correct type
                if any(w in text for w in ["weather", "date", "today", "news",
                                            "current", "latest", "price", "score"]):
                    return "factual"
                if any(w in text for w in ["code", "program", "function", "bug",
                                            "error", "write a", "implement"]):
                    return "code"
                if any(w in text for w in ["calculate", "solve", "sequence",
                                            "next number", "pattern", "equation"]):
                    return "math"
                return "educational"
        
        # Handle Hindi/Hinglish question starters → chat
        for starter in hindi_question_starters:
            if text.startswith(starter):
                return "chat"

        # STEP 3 — Math/Puzzle/Riddle detection
        math_indicators = [
            "next number", "sequence", "find the", "solve", "calculate",
            "missing", "rupee", "puzzle", "riddle", "trick question",
            "next term", "pattern", "?", "sum of", "product of", "₹",
            "pay", "each", "total", "average", "divide", "share"
        ]
        if any(ind in text for ind in math_indicators):
            return "math"

        # Comma-separated numbers = sequence = math
        import re
        if re.search(r'\d+\s*,\s*\d+\s*,\s*\d+', text):
            return "math"

        # Math operators
        if any(op in text for op in ["+", "-", "*", "/", "^", "√", "="]):
            if any(c.isdigit() for c in text):
                return "math"

        # Simple arithmetic like "2+2" or "5*6" → math
        if re.search(r'\d+\s*[\+\-\*\/\^]\s*\d+', text):
            return "math"

        # STEP 4 — Educational/CS/Electronics terms
        educational_terms = [
            "flipflop", "flip flop", "transistor", "resistor", "capacitor",
            "algorithm", "recursion", "binary", "sorting", "neural", "voltage",
            "circuit", "diode", "ohm", "frequency", "wavelength", "force",
            "momentum", "entropy", "quantum", "photon", "derivative", "integral",
            "matrix", "vector", "tensor", "stack", "queue", "graph", "tree",
            "linked list", "pointer", "memory", "cpu", "os", "kernel",
            "process", "thread", "mutex", "semaphore", "osi", "tcp", "http"
        ]
        if any(term in text for term in educational_terms):
            return "educational"

        # STEP 5 — Code detection
        code_terms = [
            "code", "program", "function", "class", "debug", "error",
            "implement", "write a script", "python", "javascript", "java",
            "c++", "array", "string", "loop", "if else", "api", "sql"
        ]
        if any(term in text for term in code_terms):
            return "code"

        # STEP 6 — Factual detection
        factual_terms = [
            "weather", "temperature", "today", "date", "time", "news",
            "current", "latest", "who is", "where is", "capital of",
            "population", "price", "score", "result", "live"
        ]
        if any(term in text for term in factual_terms):
            return "factual"

        # STEP 7 — Hindi/Hinglish detection → chat
        hindi_words = [
            "karo", "kar", "hai", "hain", "tha", "thi", "ho", "hoga",
            "kya", "nahi", "aur", "yeh", "voh", "mera", "tera", "humara",
            "theek", "accha", "bilkul", "zaroor", "shukriya", "namaste"
        ]
        hindi_count = sum(1 for w in hindi_words if w in text.split())
        if hindi_count >= 1:
            return "chat"  # Will be detected as Hinglish in router

        # DEFAULT — never return "command" if unsure
        return "chat"

    def detect_language(self, user_input):
        """Detect if input is english, hindi, or hinglish"""
        text = user_input.lower()
        hindi_words = [
            "karo", "kar", "hai", "hain", "tha", "thi", "kya", "nahi",
            "aur", "yeh", "voh", "mera", "tera", "theek", "accha",
            "batao", "samjhao", "bolo", "kyun", "kahan", "kaisa", "kaun",
            "hoga", "chahiye", "lagta", "suno", "dekho", "bol", "sun"
        ]
        hindi_count = sum(1 for w in hindi_words if w in text.split())
        # Also check for Devanagari characters
        devanagari = any('\u0900' <= c <= '\u097f' for c in user_input)
        if devanagari or hindi_count >= 2:
            return "hindi"
        elif hindi_count == 1:
            return "hinglish"
        return "english"

    def validate_response(self, response):
        """Validate that a response is good quality"""
        if not response:
            return False
        if len(response.strip().split()) < 3:
            return False
        bad_phrases = [
            "i cannot", "i don't know", "as an ai",
            "i am not able", "i'm not able", "i can't"
        ]
        lower = response.lower()
        if any(phrase in lower for phrase in bad_phrases):
            return False
        stripped = response.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            return False
        return True

    def perform_web_search(self, query):
        """Perform web search and return raw results"""
        try:
            from ddgs import DDGS
            # Add context to query for better results
            enhanced_query = query
            
            # Add location context for common queries
            if 'weather' in query.lower():
                enhanced_query = query + " Indore"
            
            raw_results = list(DDGS().text(enhanced_query, max_results=5))
            if raw_results:
                formatted = ""
                for i, r in enumerate(raw_results, 1):
                    formatted += f"SOURCE {i}: {r['title']}\n"
                    formatted += f"CONTENT: {r['body']}\n"
                    formatted += f"URL: {r['href']}\n\n"
                return formatted
        except Exception as e:
            print(f"[WebSearch] Failed: {e}")
        return None

    def call_openrouter_summarize(self, search_results, user_query):
        """Summarize web search results using OpenRouter"""
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        summary_prompt = f"""Today's date is {current_date}.

The user asked: "{user_query}"

I searched the web and found these REAL results:

{search_results}

INSTRUCTIONS:
- Today's date is {current_date}. Use this to determine if information is current.
- Answer ONLY using the information in these search results above
- Do NOT use your training knowledge
- Reply in same language as the user's question
- Be concise — max 4 sentences
- If results contain specific numbers/facts, include them
- Start directly with the answer, no preamble"""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jarvis.local",
            "X-Title": "JARVIS"
        }
        body = {
            "model": "qwen/qwen3.6-plus-preview:free",
            "messages": [{"role": "user", "content": summary_prompt}],
            "temperature": 0.1,
            "max_tokens": 500
        }
        try:
            r = requests.post(url, json=body, headers=headers, timeout=8)
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"].strip()
            return text
        except Exception as e:
            print(f"[OpenRouter Summarize] Failed: {e}")
            return None

    def call_cerebras(self, messages, system_prompt):
        """Call Cerebras API with messages"""
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "llama3.1-8b",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        try:
            r = requests.post(url, json=body, headers=headers, timeout=8)
            if r.status_code != 200:
                print(f"[Cerebras error] Status {r.status_code}: {r.text[:100]}")
                return None
            r.raise_for_status()
            data = r.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not text:
                print(f"[Cerebras] Empty response")
                return None
            return text
        except requests.Timeout:
            print(f"[Cerebras] Timeout after 8s")
            return None
        except requests.ConnectionError:
            print(f"[Cerebras] Connection error")
            return None
        except Exception as e:
            print(f"[Cerebras] Failed: {e}")
            return None

    def call_sambanova(self, messages, system_prompt):
        """Call SambaNova API with messages"""
        url = "https://api.sambanova.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {SAMBANOVA_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "Meta-Llama-3.3-70B-Instruct",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        try:
            r = requests.post(url, json=body, headers=headers, timeout=8)
            if r.status_code != 200:
                print(f"[SambaNova error] Status {r.status_code}: {r.text[:100]}")
                return None
            r.raise_for_status()
            data = r.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not text:
                print(f"[SambaNova] Empty response")
                return None
            return text
        except requests.Timeout:
            print(f"[SambaNova] Timeout after 8s")
            return None
        except requests.ConnectionError:
            print(f"[SambaNova] Connection error")
            return None
        except Exception as e:
            print(f"[SambaNova] Failed: {e}")
            return None

    def call_nvidia_nemotron(self, messages, system_prompt):
        """Call NVIDIA Nemotron API with messages"""
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "nvidia/nemotron-3-super-120b-a12b",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        try:
            r = requests.post(url, json=body, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"[NVIDIA Nemotron error] Status {r.status_code}: {r.text[:100]}")
                return None
            r.raise_for_status()
            data = r.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not text:
                print(f"[NVIDIA Nemotron] Empty response")
                return None
            return text
        except requests.Timeout:
            print(f"[NVIDIA Nemotron] Timeout after 15s")
            return None
        except requests.ConnectionError:
            print(f"[NVIDIA Nemotron] Connection error")
            return None
        except Exception as e:
            print(f"[NVIDIA Nemotron] Failed: {e}")
            return None

    def call_mistral(self, messages, system_prompt):
        """Call Mistral API with messages"""
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "mistral-small-3.1-24b-instruct",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        try:
            r = requests.post(url, json=body, headers=headers, timeout=8)
            if r.status_code != 200:
                print(f"[Mistral error] Status {r.status_code}: {r.text[:100]}")
                return None
            r.raise_for_status()
            data = r.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not text:
                print(f"[Mistral] Empty response")
                return None
            return text
        except requests.Timeout:
            print(f"[Mistral] Timeout after 8s")
            return None
        except requests.ConnectionError:
            print(f"[Mistral] Connection error")
            return None
        except Exception as e:
            print(f"[Mistral] Failed: {e}")
            return None

    def call_openrouter(self, messages, system_prompt):
        """Call OpenRouter API with messages"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jarvis.local",
            "X-Title": "Jarvis"
        }
        body = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        try:
            r = requests.post(url, json=body, headers=headers, timeout=8)
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"].strip()
            return text
        except requests.Timeout:
            print(f"[OpenRouter] Timeout after 8s")
            return None
        except requests.ConnectionError:
            print(f"[OpenRouter] Connection error")
            return None
        except Exception as e:
            print(f"[OpenRouter] Failed: {e}")
            return None

    def call_ollama(self, messages, system_prompt):
        """Call Ollama local model with messages"""
        url = f"{OLLAMA_URL}/api/generate"
        # Build prompt from messages
        prompt = system_prompt + "\n\n"
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role.title()}: {content}\n"
        body = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300}
        }
        try:
            r = requests.post(url, json=body, timeout=8)
            r.raise_for_status()
            text = r.json()["response"].strip()
            return text
        except requests.Timeout:
            print(f"[Ollama] Timeout after 8s")
            return None
        except requests.ConnectionError:
            print(f"[Ollama] Connection error")
            return None
        except Exception as e:
            print(f"[Ollama] Failed: {e}")
            return None

    def route_to_best_model(self, query_type, user_input, messages):
        """Route query to best model based on type"""
        lang = self.detect_language(user_input)

        # --- SYSTEM PROMPTS per type ---
        prompts = {
            "chat_english":     "You are JARVIS, an AI assistant created by SAMARTH. You are NOT Samarth - you are the AI he built. When asked \"how are you\", say you are doing great as an AI 😊. Be SHORT (2-3 lines), witty, conversational. Use emojis. IMPORTANT: Remember the conversation context - if user asks follow-up questions about something you just discussed, reference that context.",
            "chat_hindi":       "Tum JARVIS ho, ek AI assistant jo Samarth ne banaya hai. Tum SAMARTH nahi ho. Jab puche \"kya haal hai\", toh bolo \"main ek AI hoon, theek hoon\" 😊. Natural bolo, 2-3 line. IMPORTANT: Pichli baat yaad rakh - agar user koi follow-up puche, toh usi context mein answer de.",
            "code":             "You are JARVIS. Write clean, working code with minimal comments. Brief explanation after code only. No unnecessary filler text.",
            "math":             "You are JARVIS. Think step by step, but keep it concise. For sequences: find pattern first, then apply. For puzzles/riddles: find the logical trick. Give the answer first, then brief explanation.",
            "educational":      "You are JARVIS. Explain clearly in 3-5 lines max. Use one example if needed. No lengthy lectures. Sound like a smart friend explaining, not a professor.",
            "factual":         "You are JARVIS. Give factual, direct answer based on search results. Be brief.",
        }

        # --- ROUTING TABLE ---
        # Each entry: (system_prompt_key, [ordered provider functions])

        if query_type == "command":
            return None  # Let existing command handler take it

        elif query_type == "chat":
            sp = "chat_hindi" if lang in ["hindi", "hinglish"] else "chat_english"
            providers = [
                ("Cerebras", self.call_cerebras),
                ("Mistral", self.call_mistral),
                ("SambaNova", self.call_sambanova),
                ("OpenRouter", self.call_openrouter),
                ("Ollama", self.call_ollama)
            ]

        elif query_type == "code":
            sp = "code"
            providers = [
                ("SambaNova", self.call_sambanova),
                ("Cerebras", self.call_cerebras),
                ("NVIDIA Nemotron", self.call_nvidia_nemotron),
                ("OpenRouter", self.call_openrouter),
                ("Ollama", self.call_ollama)
            ]

        elif query_type == "math":
            sp = "math"
            providers = [
                ("NVIDIA Nemotron", self.call_nvidia_nemotron),
                ("SambaNova", self.call_sambanova),
                ("Mistral", self.call_mistral),
                ("OpenRouter", self.call_openrouter),
                ("Ollama", self.call_ollama)
            ]

        elif query_type == "educational":
            sp = "educational"
            providers = [
                ("Cerebras", self.call_cerebras),
                ("Mistral", self.call_mistral),
                ("SambaNova", self.call_sambanova),
                ("NVIDIA Nemotron", self.call_nvidia_nemotron),
                ("Ollama", self.call_ollama)
            ]

        elif query_type == "factual":
            sp = "factual"
            # Web search FIRST — no LLM for factual
            web_result = self.perform_web_search(user_input)
            if web_result:
                summary = self.call_openrouter_summarize(web_result, user_input)
                if summary:
                    return summary
            # If web fails, fallback to LLMs
            providers = [
                ("Cerebras", self.call_cerebras),
                ("SambaNova", self.call_sambanova),
                ("Mistral", self.call_mistral),
                ("Ollama", self.call_ollama)
            ]

        else:
            sp = "chat_english"
            providers = [("Cerebras", self.call_cerebras), ("SambaNova", self.call_sambanova), ("Ollama", self.call_ollama)]

        system_prompt = prompts.get(sp, prompts["chat_english"])

        # --- EXECUTE CHAIN ---
        for provider_name, provider in providers:
            try:
                result = provider(messages, system_prompt)
                if self.validate_response(result):
                    print(f"[{provider_name}] Responding...")
                    return {"type": "conversation", "reply": result, "provider": provider_name}
            except Exception as e:
                print(f"[{provider_name}] Failed: {e}")
                continue

        return {"type": "conversation", "reply": "I'm having trouble connecting right now. Please try again.", "provider": "None"}

    def think(self, user_input, conversation_history=None):
        """Main think function using smart routing"""
        # Use internal conversation history if none provided
        if conversation_history is None:
            conversation_history = self.conversation_history
        
        messages = conversation_history[-4:] if conversation_history else []
        messages.append({"role": "user", "content": user_input})

        # Step 1: Classify
        query_type = self.classify_query(user_input)
        print(f"[Query Type: {query_type}]")  # debug

        # Step 2: If command — return None so jarvis.py handles it
        if query_type == "command":
            return None

        # Step 3: Route to best model
        response = self.route_to_best_model(query_type, user_input, messages)
        
        # Add to history (only for non-command responses)
        self.add_to_history("user", user_input)
        if response and isinstance(response, dict):
            reply = response.get("reply", "")
            if reply:
                self.add_to_history("assistant", reply)
        
        return response


# Global Brain instance for backward compatibility
_brain_instance = None

def get_brain():
    """Get or create global Brain instance"""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = Brain()
    return _brain_instance


def think(user_input: str) -> dict:
    """Standalone think function - uses Brain class with persistent memory"""
    # Get Brain instance (singleton with persistent memory)
    brain = get_brain()
    
    result = brain.think(user_input)  # Let brain handle history internally
    
    # If Brain returns None (command), use old command handling
    if result is None:
        # Use old classify_input and command processing
        input_type = classify_input(user_input)
        
        if input_type == 'command':
            providers = [
                ("Cerebras", call_cerebras_command),
                ("SambaNova", call_sambanova),
                ("OpenRouter", call_openrouter_command),
                ("Ollama", call_ollama),
            ]
            for name, fn in providers:
                print(f"[Trying {name}...]")
                try:
                    cmd_result = fn(user_input)
                    if isinstance(cmd_result, dict) and "type" in cmd_result:
                        if cmd_result.get('type') == 'conversation':
                            reply = cmd_result.get('reply', '').strip()
                            if not reply:
                                continue
                            cmd_result['provider'] = name
                            return cmd_result
                        if cmd_result.get("action") == "raw" and cmd_result.get("target"):
                            raw_target = cmd_result.get("target", "")
                            input_type = "conversation"
                            user_input = raw_target
                            break
                        cmd_result['provider'] = name
                        return cmd_result
                except Exception as e:
                    print(f"[{name} failed] {e}")
                    continue
    
    # Convert string response to dict format for backward compatibility
    if isinstance(result, str):
        return {"type": "conversation", "reply": result}
    
    return result
