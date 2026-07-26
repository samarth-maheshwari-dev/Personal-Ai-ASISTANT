"""
Brain - The Ollama-powered AI engine for JARVIS.
Uses ai/ollama_router.py as the sole AI gateway with 5-model fallback chain.
Preserves all classification, language detection, validation, web search logic.
"""

import os
import json
import requests
import re
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

# Import Ollama Router as the sole AI gateway
from ai.ollama_router import handle as ollama_handle, handle_chat as ollama_handle_chat

OLLAMA_URL = "http://localhost:11434"

SYSTEM_PROMPT = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."

COMMAND_PROMPT = """You are a Windows PC command parser.
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
"notepad band karo" → {"type":"command","action":"close","target":"notepad","app":"","arg":""}
"chrome kholo" → {"type":"command","action":"open","target":"chrome","app":"","arg":""}
"play shape of you on spotify" → {"type":"command","action":"play_song","target":"spotify","app":"spotify","arg":"shape of you"}
"search python on youtube" → {"type":"command","action":"search_youtube","target":"youtube","app":"chrome","arg":"python"}
"next on spotify" → {"type":"command","action":"next","target":"spotify","app":"spotify","arg":""}
"pause on spotify" → {"type":"command","action":"pause","target":"spotify","app":"spotify","arg":""}
"previous on spotify" → {"type":"command","action":"previous","target":"spotify","app":"spotify","arg":""}
"play on spotify" → {"type":"command","action":"play","target":"spotify","app":"spotify","arg":""}"""


# ============================================================
# CLASSIFICATION FUNCTIONS (preserved from original)
# ============================================================

def classify_query(user_input):
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
        "next term", "pattern", "?", "sum of", "product of", "\u20b9",
        "pay", "each", "total", "average", "divide", "share"
    ]
    if any(ind in text for ind in math_indicators):
        return "math"

    # Comma-separated numbers = sequence = math
    if re.search(r'\d+\s*,\s*\d+\s*,\s*\d+', text):
        return "math"

    # Math operators
    if any(op in text for op in ["+", "-", "*", "/", "^", "\u221a", "="]):
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


def detect_language(user_input):
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


def validate_response(response):
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


# ============================================================
# WEB SEARCH FUNCTIONS (preserved from original)
# ============================================================

def perform_web_search(query):
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


def filter_search_results(raw_results):
    """Filter and deduplicate search results."""
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


def rephrase_for_retry(query):
    """Rephrase query for retrying web search."""
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


def enhanced_web_search(user_query):
    """Perform enhanced web search with retry logic."""
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


def call_ollama_summarize(search_results, user_query):
    """Summarize web search results using Ollama."""
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
    
    result = ollama_handle(summary_prompt, "You are a factual assistant. Summarize only from the provided search data. Never guess.")
    if result and result.get("reply"):
        return result["reply"]
    return None


# ============================================================
# COMMAND PARSING FUNCTIONS (now using Ollama)
# ============================================================

def parse_command_with_ollama(user_input):
    """Parse user input into a command JSON using Ollama."""
    result = ollama_handle(user_input, COMMAND_PROMPT)
    if result and result.get("reply"):
        text = result["reply"]
        # Extract JSON from response
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
        try:
            return json.loads(text)
        except:
            pass
    return None


def call_cerebras_command(user_input):
    """Parse command using Ollama (replaces Cerebras command parser)."""
    return parse_command_with_ollama(user_input)


def call_openrouter_command(user_input):
    """Parse command using Ollama (replaces OpenRouter command parser)."""
    return parse_command_with_ollama(user_input)


def call_sambanova(user_input):
    """Ollama-based conversation - replaces old SambaNova call."""
    result = ollama_handle(user_input, SYSTEM_PROMPT)
    if result and result.get("reply"):
        text = result["reply"]
        # Check if response is JSON command or plain text
        if text.startswith("{") and "}" in text:
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                json_str = text[start:end]
                parsed = json.loads(json_str)
                if parsed.get("type") == "command":
                    return parsed
            except:
                pass
        return {"type": "conversation", "reply": text}
    return None


def call_cerebras(user_input):
    """Ollama-based conversation - replaces old Cerebras call."""
    return call_sambanova(user_input)


def call_ollama(user_input):
    """Ollama-based conversation call."""
    result = ollama_handle(user_input, SYSTEM_PROMPT)
    if result and result.get("reply"):
        text = result["reply"]
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
        try:
            return json.loads(text)
        except:
            pass
        return {"type": "conversation", "reply": text}
    return None


def call_groq_conversation(user_input, history=None):
    """Ollama-based conversation - replaces old Groq call."""
    system = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."
    if history:
        messages = [{"role": "system", "content": system}]
        messages.extend(history[-4:])
        messages.append({"role": "user", "content": user_input})
        result = ollama_handle_chat(messages, system)
    else:
        result = ollama_handle(user_input, system)
    
    if result and result.get("reply"):
        return {"type": "conversation", "reply": result["reply"]}
    return None


def call_nvidia(user_input, history=None):
    """Ollama-based conversation - replaces old NVIDIA call."""
    return call_groq_conversation(user_input, history)


def call_mistral(user_input, history=None):
    """Ollama-based conversation - replaces old Mistral call."""
    return call_groq_conversation(user_input, history)


def call_openrouter_conversation(user_input, history=None):
    """Ollama-based conversation - replaces old OpenRouter conversation.
    This function is imported by jarvis.py, so signature is preserved."""
    system = "You are JARVIS — a sharp, human-like AI assistant built by Samarth. Respond conversationally, never in JSON or robotic format. Be concise unless detail is needed."
    if history:
        messages = [{"role": "system", "content": system}]
        messages.extend(history[-4:])
        messages.append({"role": "user", "content": user_input})
        result = ollama_handle_chat(messages, system)
    else:
        result = ollama_handle(user_input, system)
    
    if result and result.get("reply"):
        return {"type": "conversation", "reply": result["reply"]}
    return None


def call_openrouter_summarize(search_results, user_query):
    """Summarize web search results using Ollama (replaces OpenRouter)."""
    return call_ollama_summarize(search_results, user_query)


def call_cerebras_summarize(search_results, user_query):
    """Summarize web search results using Ollama (replaces Cerebras)."""
    return call_ollama_summarize(search_results, user_query)


def call_nvidia_nemotron(messages, system_prompt):
    """Ollama-based conversation - replaces old NVIDIA Nemotron."""
    return call_ollama_adaptor(messages, system_prompt)


def call_ollama_adaptor(messages, system_prompt):
    """Call Ollama with messages list format (adapter for Brain class)."""
    # Convert messages to prompt
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"{role.title()}: {content}\n"
    result = ollama_handle(prompt, system_prompt)
    if result and result.get("reply"):
        return result["reply"]
    return None


# ============================================================
# CLASSIFICATION AND ROUTING (preserved from original)
# ============================================================

def classify_input(text):
    """Classify input type: command, conversation, web_search"""
    t = text.lower().strip()
    
    if ' then ' in t or ' phir ' in t or ' aur ' in t or ' and ' in t:
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


# ============================================================
# STANDALONE think() FUNCTION (main entry point for jarvis.py)
# ============================================================

_conversation_history = []

def think(user_input):
    """Main think function - routes input through Ollama models with fallback chain."""
    global _conversation_history
    
    input_type = classify_input(user_input)
    
    if input_type == 'command':
        # Try to parse as command with Ollama
        cmd_result = parse_command_with_ollama(user_input)
        if cmd_result and isinstance(cmd_result, dict) and "type" in cmd_result:
            if cmd_result.get('type') == 'conversation':
                reply = cmd_result.get('reply', '').strip()
                if reply:
                    cmd_result['provider'] = 'Ollama'
                    return cmd_result
            if cmd_result.get("action") == "raw" and cmd_result.get("target"):
                raw_target = cmd_result.get("target", "")
                input_type = "conversation"
                user_input = raw_target
            else:
                cmd_result['provider'] = 'Ollama'
                return cmd_result
        
        # Fallback: send raw input through Ollama for conversation
        result = ollama_handle(user_input, SYSTEM_PROMPT)
        if result and result.get("reply"):
            return {"type": "conversation", "reply": result["reply"], "provider": "Ollama"}
        
        # Last resort - return raw
        return {
            "type": "command",
            "action": "raw",
            "target": user_input,
            "app": "",
            "arg": ""
        }
    
    if input_type == 'web_search':
        print(f"[Web search for: {user_input}]")
        formatted_results = enhanced_web_search(user_input)
        if formatted_results:
            answer = call_ollama_summarize(formatted_results, user_input)
            if answer:
                return {
                    "type": "conversation",
                    "reply": answer,
                    "provider": "Ollama",
                    "source": "web_search"
                }
        print("[WebSearch] Both attempts failed, falling back to conversation.")
        input_type = 'conversation'
    
    if input_type == 'conversation' or input_type == 'web_search':
        _conversation_history.append({
            "role": "user", "content": user_input
        })
        
        # Use OllamaRouter's built-in model chain
        if _conversation_history:
            messages = _conversation_history[-4:]
            result = ollama_handle_chat(
                [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                SYSTEM_PROMPT
            )
        else:
            result = ollama_handle(user_input, SYSTEM_PROMPT)
        
        if result and result.get("reply"):
            reply = result["reply"].strip()
            if reply:
                _conversation_history.append({
                    "role": "assistant",
                    "content": reply
                })
                if len(_conversation_history) > 20:
                    _conversation_history = _conversation_history[-20:]
                return {
                    "type": "conversation",
                    "reply": reply,
                    "provider": result.get("provider", "Ollama"),
                    "source": "conversation"
                }
    
    # Ultimate fallback
    return {
        "type": "command",
        "action": "raw",
        "target": user_input,
        "app": "",
        "arg": ""
    }


# ============================================================
# BRAIN CLASS (preserved interface for backward compatibility)
# ============================================================

class Brain:
    """Smart brain with query classification and Ollama model routing"""
    
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
        return classify_query(user_input)
    
    def detect_language(self, user_input):
        """Detect if input is english, hindi, or hinglish"""
        return detect_language(user_input)
    
    def validate_response(self, response):
        """Validate that a response is good quality"""
        return validate_response(response)
    
    def perform_web_search(self, query):
        """Perform web search and return raw results"""
        return perform_web_search(query)
    
    def call_openrouter_summarize(self, search_results, user_query):
        """Summarize web search results using Ollama."""
        return call_ollama_summarize(search_results, user_query)
    
    def call_cerebras(self, messages, system_prompt):
        """Call Ollama with messages (adapter for backward compatibility)."""
        return call_ollama_adaptor(messages, system_prompt)
    
    def call_sambanova(self, messages, system_prompt):
        """Call Ollama with messages (adapter for backward compatibility)."""
        return call_ollama_adaptor(messages, system_prompt)
    
    def call_nvidia_nemotron(self, messages, system_prompt):
        """Call Ollama with messages (adapter for backward compatibility)."""
        return call_ollama_adaptor(messages, system_prompt)
    
    def call_mistral(self, messages, system_prompt):
        """Call Ollama with messages (adapter for backward compatibility)."""
        return call_ollama_adaptor(messages, system_prompt)
    
    def call_openrouter(self, messages, system_prompt):
        """Call Ollama with messages (adapter for backward compatibility)."""
        return call_ollama_adaptor(messages, system_prompt)
    
    def call_ollama(self, messages, system_prompt):
        """Call Ollama with messages."""
        return call_ollama_adaptor(messages, system_prompt)
    
    def route_to_best_model(self, query_type, user_input, messages):
        """Route query through Ollama model chain.
        Uses OllamaRouter's built-in 5-model hierarchy with fallback."""
        lang = self.detect_language(user_input)

        # --- SYSTEM PROMPTS per type ---
        prompts = {
            "chat_english":     "You are JARVIS, an AI assistant created by SAMARTH. You are NOT Samarth - you are the AI he built. When asked \"how are you\", say you are doing great as an AI \U0001f60a. Be SHORT (2-3 lines), witty, conversational. Use emojis. IMPORTANT: Remember the conversation context - if user asks follow-up questions about something you just discussed, reference that context.",
            "chat_hindi":       "Tum JARVIS ho, ek AI assistant jo Samarth ne banaya hai. Tum SAMARTH nahi ho. Jab puche \"kya haal hai\", toh bolo \"main ek AI hoon, theek hoon\" \U0001f60a. Natural bolo, 2-3 line. IMPORTANT: Pichli baat yaad rakh - agar user koi follow-up puche, toh usi context mein answer de.",
            "code":             "You are JARVIS. Write clean, working code with minimal comments. Brief explanation after code only. No unnecessary filler text.",
            "math":             "You are JARVIS. Think step by step, but keep it concise. For sequences: find pattern first, then apply. For puzzles/riddles: find the logical trick. Give the answer first, then brief explanation.",
            "educational":      "You are JARVIS. Explain clearly in 3-5 lines max. Use one example if needed. No lengthy lectures. Sound like a smart friend explaining, not a professor.",
            "factual":         "You are JARVIS. Give factual, direct answer based on search results. Be brief.",
        }

        # --- ROUTING TABLE ---
        if query_type == "command":
            return None  # Let existing command handler take it

        elif query_type == "chat":
            sp = "chat_hindi" if lang in ["hindi", "hinglish"] else "chat_english"

        elif query_type == "code":
            sp = "code"

        elif query_type == "math":
            sp = "math"

        elif query_type == "educational":
            sp = "educational"

        elif query_type == "factual":
            sp = "factual"
            # Web search FIRST — no LLM for factual
            web_result = self.perform_web_search(user_input)
            if web_result:
                summary = self.call_openrouter_summarize(web_result, user_input)
                if summary:
                    return {"type": "conversation", "reply": summary, "provider": "Ollama"}
            # If web fails, fallback to Ollama conversation

        else:
            sp = "chat_english"

        system_prompt = prompts.get(sp, prompts["chat_english"])
        
        # Build prompt from messages
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role.title()}: {content}\n"

        # Use OllamaRouter's full model chain via handle()
        result = ollama_handle(prompt, system_prompt)
        if result and result.get("reply"):
            reply_text = result["reply"]
            if self.validate_response(reply_text):
                provider = result.get("provider", "Ollama")
                print(f"[{provider}] Responding...")
                return {"type": "conversation", "reply": reply_text, "provider": provider}

        return {"type": "conversation", "reply": "I'm having trouble connecting right now. Please try again.", "provider": "None"}
    
    def think(self, user_input, conversation_history=None):
        """Main think function using Ollama routing"""
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


# Standalone think function (replaces old one - uses Brain class)
# This is already defined above - this is a backward compatibility alias

