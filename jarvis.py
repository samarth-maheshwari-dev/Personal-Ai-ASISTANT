import os
import subprocess
import sys
import time
import re
from pathlib import Path

from memory.memory_manager import MemoryManager

NIRCMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nircmd.exe')
NIRCMD_AVAILABLE = os.path.isfile(NIRCMD)

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_EXE):
    CHROME_EXE = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

def open_in_chrome(url: str):
    """Always open URL in Chrome, never Edge or default browser."""
    subprocess.Popen([CHROME_EXE, url])


if not NIRCMD_AVAILABLE:
    print("[Jarvis] WARNING: nircmd.exe not found in JARVIS folder. Volume control is disabled.")


def install_packages(packages):
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


install_packages(["pyautogui", "pygetwindow", "pywin32", "rapidfuzz", "psutil", "winrt-runtime", "winrt-Windows.Media.Control", "winrt-Windows.Foundation", "winrt-Windows.Foundation.Collections", "python-dotenv", "requests", "yt-dlp", "ddgs", "pycaw", "comtypes"])


import pyautogui
import pygetwindow as gw
from rapidfuzz import fuzz
import psutil
import win32gui
import win32con
import win32api
import win32com.client
import asyncio
import concurrent.futures
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as WinRTMediaManager


def web_search(query: str, max_results: int = 5) -> str:
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return f"No results found for: {query}"
        
        formatted = f"Web search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            formatted += f"{i}. {r['title']}\n"
            formatted += f"   {r['body'][:200]}\n"
            formatted += f"   URL: {r['href']}\n\n"
        return formatted
    except Exception as e:
        return f"Web search failed: {e}"


from brain import think


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


HINGLISH_KEYWORDS = {
    'kholo', 'khol', 'khul', 'kare', 'karo', 'karna', 'karega', 'khulega',
    'band', 'bando', 'bandho', 'bandh', 'bandhkar', 'bandkaro',
    'badhao', 'badha', 'ghatao', 'ghata', 'kam', 'zyada',
    'gaana', 'gana', 'gaane', 'gane', 'song', 'songs',
    'agla', 'agle', 'agali', 'agleya', 'agla', 'agle', 'agleyi',
    'pichhla', 'pichla', 'pehla', 'previous', 'back',
    'chalao', 'chalu', 'chalau', 'chalana', 'start', 'start karo',
    'rukho', 'ruko', 'rukna', 'stop', 'stop karo', 'band karo',
    'bajao', 'baja', 'bajana', 'play', 'play karo',
    'suno', 'sun', 'sunna', 'lauge', 'lena', 'lijiye', 'lo',
    'kaisa', 'kaisi', 'kitna', 'kitni', 'how', 'what',
    'batao', ' bata', 'batana', 'tell', 'say',
    'awaaz', 'aawaz', 'awaz', 'volume', 'sound',
    'sir', 'boss', 'sirf', 'bas', 'only', 'just',
    'aur', 'and', 'phir', 'then', 'ab', 'now',
    'mein', 'me', 'par', 'on', 'ko', 'se', 'ka', 'ki', 'ke',
    'ab', 'abhi', 'now', 'phir', 'fir', 'baad', 'after',
    'haan', 'nahi', 'nahin', 'yes', 'no', 'okay', 'ok',
    'thoda', 'kuch', 'some', 'bahut', 'zyada', 'more', 'less',
    'youtube', 'chrome', 'spotify', 'vlc', 'browser', 'app',
    'karta', 'kare', 'karega', 'hota', 'ho', 'the',
    'raha', 'rahi', 'rahe', 'hain', 'tha', 'thi',
}

VERB_MAP = {
    'kholo': 'open', 'khol': 'open', 'khul': 'open', 'kare': 'open',
    'karo': 'open', 'karna': 'open', 'karega': 'open', 'khulega': 'open',
    'band': 'close', 'bando': 'close', 'bandho': 'close', 'bandh': 'close',
    'bandhkar': 'close', 'bandkaro': 'close',
    'badhao': 'increase', 'badha': 'increase',
    'ghatao': 'decrease', 'ghata': 'decrease',
    'gaana': 'next', 'gana': 'next', 'gaane': 'next', 'gane': 'next',
    'agla': 'next', 'agle': 'next', 'agali': 'next', 'agleya': 'next',
    'pichhla': 'previous', 'pichla': 'previous', 'pehla': 'previous',
    'chalao': 'play', 'chalu': 'play', 'chalau': 'play', 'chalana': 'play',
    'rukho': 'pause', 'ruko': 'pause', 'rukna': 'pause',
    'suno': 'pause', 'sun': 'pause', 'sunna': 'pause',
    'bajao': 'play', 'baja': 'play', 'bajana': 'play',
    'batao': 'list', 'bata': 'list', 'batana': 'list',
}

TARGET_MAP = {
    'spotify': 'spotify', 'chrome': 'chrome', 'youtube': 'chrome',
    'browser': 'chrome', 'vlc': 'vlc', 'edge': 'edge', 'firefox': 'firefox',
    'app': None, 'apps': None, 'application': None, 'application': None,
}

VOLUME_MAP = {
    'awaaz': 'volume', 'aawaz': 'volume', 'awaz': 'volume',
    'sound': 'volume', 'awaz': 'volume',
    'badhao': 'up', 'badha': 'up', 'zyada': 'up', 'bahut': 'up',
    'ghatao': 'down', 'ghata': 'down', 'kam': 'down', ' kam': 'down',
}

MEDIA_MAP = {
    'gaana': 'next', 'gana': 'next', 'gaane': 'next', 'gane': 'next',
    'song': 'next', 'songs': 'next',
    'agla': 'next', 'agle': 'next', 'agali': 'next', 'agleya': 'next',
    'pichhla': 'previous', 'pichla': 'previous', 'pehla': 'previous',
}


def detect_hinglish(text):
    text_lower = text.lower()
    words = set(text_lower.split())
    keyword_count = sum(1 for w in words if w in HINGLISH_KEYWORDS)
    if keyword_count >= 1:
        return True
    for kw in HINGLISH_KEYWORDS:
        if kw in text_lower:
            return True
    return False


def hinglish_to_english(text):
    original = text.strip()
    t = text.lower().strip()

    multi_word_volume = {
        'awaaz band karo': 'mute',
        'awaaz band kar': 'mute',
        'awaaz bandh karo': 'mute',
        'sound band karo': 'mute',
        'awaaz wapas lao': 'unmute',
        'awaaz wapas': 'unmute',
        'sound wapas lao': 'unmute',
        'awaaz badao': 'increase volume',
        'awaaz badhao': 'increase volume', 
        'awaaz badhaao': 'increase volume',
        'awaaz ghataao': 'decrease volume',
        'awaaz ghatao': 'decrease volume',
        'awaaz ghato': 'decrease volume',
        'awaaz tej karo': 'increase volume',
        'awaaz tej kar': 'increase volume',
        'awaaz zyada karo': 'increase volume',
        'awaaz ghatao': 'decrease volume',
        'awaaz kam karo': 'decrease volume',
        'awaaz dhima karo': 'decrease volume',
        'volume badao': 'increase volume',
        'volume badhao': 'increase volume',
        'volume ghato': 'decrease volume',
        'volume ghatao': 'decrease volume',
        'volume badhaao': 'increase volume',
        'volume ghatao': 'decrease volume',
        'volume band karo': 'mute',
        'volume wapas lao': 'unmute',
    }

    t = re.sub(
        r'^(\w+)\s+(band karo|band kar|bandh karo|bandh kar|hatao)$',
        r'close \1',
        t
    )
    t = re.sub(
        r'^(\w+)\s+(kholo|khol|karo|chalao)$',
        r'open \1',
        t
    )
    t = re.sub(
        r'^(\w+)\s+(minimize karo|minimize kar|chota karo)$',
        r'minimize \1',
        t
    )
    t = re.sub(
        r'^(\w+)\s+(maximize karo|maximize kar|bada karo)$',
        r'maximize \1',
        t
    )

    for phrase, english in multi_word_volume.items():
        if phrase in t:
            return english

    chrome_url_patterns = [
        (r'(.+?)\s+(?:kholo|open\s+karo)\s+chrome\s+(?:mein|pe|par|me)', 'open_in_chrome'),
        (r'chrome\s+(?:mein|pe)\s+(.+?)\s+(?:kholo|open\s+karo)', 'open_in_chrome'),
    ]
    
    for pattern, action in chrome_url_patterns:
        match = re.search(pattern, t)
        if match:
            url = match.group(1).strip()
            url_tlds = ['.com', '.org', '.net', '.io', '.dev', '.co']
            if any(tld in url for tld in url_tlds):
                if not url.startswith('http'):
                    url = 'https://' + url
                return f"open {url}"

    vol_pattern = re.search(r'(?:volume|awaaz)\s+(\d+)', t)
    if not vol_pattern:
        vol_pattern = re.search(r'(\d+)\s+(?:pe\s+)?(?:lao|karo|kar|set)', t)
    if vol_pattern:
        num = vol_pattern.group(1)
        if 0 <= int(num) <= 100:
            return f"set volume {num}"

    # ── STEP 1: Extract target from ORIGINAL text FIRST (before any stripping) ──
    known_targets = [
        'spotify', 'chrome', 'youtube', 'whatsapp', 'notepad',
        'vlc', 'settings', 'calculator', 'camera', 'edge',
        'word', 'excel', 'powerpoint', 'teams', 'discord',
        'telegram', 'instagram', 'twitter', 'photos', 'paint',
        'file explorer', 'explorer', 'task manager', 'antigravity',
        'claude', 'music', 'video', 'song', 'gaana', 'gana',
        'dono', 'both', 'sab', 'sabhi',
        # Multi-word app names
        'microsoft store', 'visual studio', 'windows terminal',
        'windows powershell', 'command prompt',
    ]

    found_target = ''
    for target in known_targets:
        if target in t:
            found_target = target
            break

    # Also check for URLs
    url_tlds = ['.com', '.org', '.net', '.io', '.dev', '.co']
    words_in_t = t.split()
    for word in words_in_t:
        if any(tld in word for tld in url_tlds):
            found_target = word
            break

    # Also check for numbers (for volume commands)
    numbers = re.findall(r'\b\d+\b', t)

    # ── STEP 2: Detect action from text ──
    # Use word boundary matching — NOT substring replace
    action_map = {
        # Open variants
        'kholo': 'open', 'khole': 'open', 'khol': 'open',
        'chalaao': 'open', 'chalao': 'open', 'chhalo': 'open',
        'launch': 'open', 'start': 'open', 'open': 'open',
        'chalu': 'open',

        # Close variants
        'band': 'close', 'bund': 'close', 'bandh': 'close',
        'hatao': 'close', 'hata': 'close', 'close': 'close',
        'hat': 'close',

        # Play variants
        'bajao': 'play', 'bajaa': 'play', 'play': 'play',
        'chala': 'play', 'bajne': 'play',

        # Pause variants
        'roko': 'pause', 'rok': 'pause', 'pause': 'pause',
        'rukja': 'pause', 'ruk': 'pause',

        # Next
        'agla': 'next', 'agli': 'next', 'agle': 'next',
        'next': 'next', 'skip': 'next', 'aagla': 'next',

        # Previous
        'pichla': 'previous', 'pichle': 'previous',
        'previous': 'previous', 'wapas': 'previous',
        'peechla': 'previous',

        # Focus
        'focus': 'focus', 'dekho': 'focus', 'lao': 'focus',
        'dikhao': 'focus', 'aao': 'focus',

        # Minimize
        'minimize': 'minimize', 'chota': 'minimize',
        'chhupa': 'minimize', 'neeche': 'minimize',

        # Maximize
        'maximize': 'maximize', 'bada': 'maximize',
        'bara': 'maximize', 'fullscreen': 'maximize',
        'poora': 'maximize',

        # Restore
        'restore': 'restore',

        # Mute
        'mute': 'mute', 'chup': 'mute', 'khamosh': 'mute',

        # Unmute
        'unmute': 'unmute',

        # Volume increase
        'badhaao': 'increase volume', 'badhao': 'increase volume',
        'tej': 'increase volume', 'tez': 'increase volume',
        'louder': 'increase volume', 'increase': 'increase volume',

        # Volume decrease
        'ghatao': 'decrease volume', 'ghataao': 'decrease volume',
        'softer': 'decrease volume', 'dhima': 'decrease volume',
        'decrease': 'decrease volume',

        # Volume
        'volume': 'volume', 'awaaz': 'volume',
    }

    # Multi-word action phrases — check BEFORE single words
    multi_word_map = {
        'awaaz band': 'mute',
        'awaaz badhaao': 'increase volume',
        'awaaz badhao': 'increase volume',
        'awaaz ghatao': 'decrease volume',
        'awaaz ghataao': 'decrease volume',
        'awaaz tej': 'increase volume',
        'awaaz dhima': 'decrease volume',
        'kam karo': 'decrease volume',
        'zyada karo': 'increase volume',
        'wapas lao': 'restore',
    }

    found_action_english = ''

    # Check multi-word first
    for phrase, eng in multi_word_map.items():
        if phrase in t:
            found_action_english = eng
            break

    # Then check individual words (split by space only — no substring replace)
    if not found_action_english:
        words = t.split()
        for word in words:
            # Strip punctuation from word
            clean_word = word.strip('.,!?/')
            if clean_word in action_map:
                found_action_english = action_map[clean_word]
                break

    # ── STEP 3: BUILD ENGLISH COMMAND ──
    # Special handling for close commands
    close_all_targets = {'sab', 'sabhi', 'all', 'sare', 'sarhi', 'sabhi apps', 'all apps', 'sab kuch'}
    close_action_only_patterns = {'all apps', 'close all'}
    
    if found_action_english == 'close':
        # Check for close all patterns first
        t_check = t.strip().lower()
        if any(pat in t_check for pat in close_action_only_patterns):
            return "close all"
        # Then check targets
        if found_target and found_target.lower() in close_all_targets:
            return "close all"
        elif found_target:
            # Single close like "close chrome" or "close both"
            return f"close {found_target}"
        else:
            return "close"
    
    if found_action_english and found_target:
        if found_action_english in ('increase volume', 'decrease volume', 'mute', 'unmute'):
            return found_action_english
        return f"{found_action_english} {found_target}"

    elif found_action_english == 'volume' and numbers:
        return f"set volume {numbers[0]}"

    elif found_action_english in ('increase volume', 'decrease volume', 'mute', 'unmute'):
        return found_action_english

    elif found_action_english and not found_target:
        return found_action_english

    elif found_target and not found_action_english:
        # Hindi word order: target only → default open
        return f"open {found_target}"

    else:
        # Nothing Hindi detected — return original unchanged
        return original


FAST_COMMANDS = [
    "volume up", "volume down", "mute", "unmute",
    "increase volume", "decrease volume",
    "play", "pause", "next", "previous",
    "exit", "list", "media list",
]
FAST_VERBS = [
    "open ", "close ", "minimize ", "maximize ",
    "restore ", "focus ", "set volume",
    "play on ", "pause on ", "next on ", "previous on ",
    "search_youtube ", "play_song ",
]

SINGLE_WORD_COMMANDS = ['play', 'pause', 'next', 'previous', 
                        'mute', 'unmute', 'exit', 'list']


def is_fast_command(text):
    t = text.lower().strip()
    if t.startswith('memory'):
        return True
    if t.startswith('create file') or t.startswith('create a file'):
        return True
    if t.startswith('delete file') or (t.startswith('delete ') and '.' in t):
        return True
    if t in FAST_COMMANDS:
        return True
    fast_phrases = [
        'increase volume', 'decrease volume',
        'volume up', 'volume down',
        'mute', 'unmute',
    ]
    if t in fast_phrases:
        return True
    if t.startswith('set volume'):
        return True
    return any(t.startswith(v) for v in FAST_VERBS)


def split_into_parts(user_input):
    parts = re.split(r'\s+then\s+|\s+phir\s+', user_input)
    flattened = []
    for segment in parts:
        subparts = [p.strip() for p in re.split(r'\s+and\s+|\s+aur\s+|\s+or\s+', segment)]
        for p in subparts:
            if p:
                flattened.append(p)
    return flattened


class DependencyManager:
    @staticmethod
    def check():
        pass


class FileManager:
    
    DEFAULT_DIR = os.path.join(
        os.path.expanduser("~"), 
        "OneDrive", "Desktop"
    )
    # Fallback if OneDrive Desktop doesn't exist
    if not os.path.exists(DEFAULT_DIR):
        DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
    
    def create_file(self, filename: str, content: str = "") -> bool:
        try:
            if os.path.isabs(filename) or '\\' in filename or '/' in filename:
                filepath = filename
            else:
                filepath = os.path.join(self.DEFAULT_DIR, filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[Jarvis] ✅ File banayi: {filepath}")
            if content:
                lines = content.count('\n') + 1
                chars = len(content)
                print(f"[Jarvis] 📝 {lines} lines, {chars} characters likhe.")
                # Show first 3 lines as preview
                preview_lines = content.split('\n')[:3]
                print(f"[Jarvis] Preview:")
                for line in preview_lines:
                    if line.strip():
                        print(f"    {line[:60]}{('...' if len(line) > 60 else '')}")
            else:
                print(f"[Jarvis] 📄 Empty file banayi.")
            return True
            
        except Exception as e:
            print(f"[Jarvis] File banana fail hua: {e}")
            return False
    
    def show_in_explorer(self, filename: str) -> bool:
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            possible_paths = [
                os.path.join(desktop_path, filename),
                filename,
            ]
            
            found_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_path = path
                    break
            
            if found_path:
                subprocess.Popen(
                    f'explorer /select,"{found_path}"'
                )
                print(f"[Jarvis] File Explorer mein dikha raha hoon: {filename}")
                print(f"[Jarvis] Aap manually delete kar sakte hain.")
                return True
            else:
                subprocess.Popen(f'explorer "{desktop_path}"')
                print(f"[Jarvis] '{filename}' Desktop pe nahi mili.")
                print(f"[Jarvis] Desktop open kar diya — manually dhundho.")
                return False
                
        except Exception as e:
            print(f"[Jarvis] Explorer open fail: {e}")
            return False

    @staticmethod
    def search_and_open(search_term):
        desktop = Path(os.path.expanduser("~/Desktop"))
        downloads = Path(os.path.expanduser("~/Downloads"))
        search_paths = [desktop, downloads]
        
        all_files = []
        for base_path in search_paths:
            if base_path.exists():
                for root, dirs, files in os.walk(base_path):
                    for f in files:
                        all_files.append(os.path.join(root, f))
        
        matches = []
        for file_path in all_files:
            filename = os.path.basename(file_path)
            file_stem = os.path.splitext(filename)[0]
            
            full_score = fuzz.ratio(search_term.lower(), filename.lower())
            stem_score = fuzz.ratio(search_term.lower(), file_stem.lower())
            combined_score = max(full_score, stem_score)
            
            if combined_score >= 60:
                matches.append((file_path, combined_score))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        
        if len(matches) == 0:
            print(f"[Jarvis] No file found matching: {search_term}")
            return False
        
        if len(matches) == 1:
            os.startfile(matches[0][0])
            print(f"[Jarvis] Opened: {matches[0][0]}")
            return True
        
        print(f"\n[Jarvis] Multiple matches found ({len(matches)}):")
        for i, (path, score) in enumerate(matches[:10], 1):
            print(f"  {i}. {os.path.basename(path)}")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more")
        
        try:
            choice = input("Select number: ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(matches):
                    os.startfile(matches[idx][0])
                    print(f"[Jarvis] Opened: {matches[idx][0]}")
                    return True
        except (ValueError, EOFError):
            pass
        
        print("[Jarvis] Invalid selection.")
        return False


class AppManager:
    def __init__(self):
        self._apps_cache = None

    def get_installed_apps(self, force_refresh=False):
        if self._apps_cache and not force_refresh:
            return self._apps_cache
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-StartApps | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            apps = []
            import json
            data = json.loads(result.stdout)
            for item in data:
                app_name = item.get("Name", "").strip()
                app_id = item.get("AppID", "").strip()
                if app_name and app_id:
                    apps.append({"name": app_name, "id": app_id})
            
            self._apps_cache = apps
            return apps
        except Exception as e:
            print(f"Error getting apps: {e}")
            return []

    def find_app(self, query):
        apps = self.get_installed_apps()
        if not apps:
            return None
        
        best_match = None
        best_score = 45
        
        query_lower = query.lower()
        for app in apps:
            score = fuzz.ratio(query_lower, app["name"].lower())
            partial_score = fuzz.partial_ratio(query_lower, app["name"].lower())
            combined_score = max(score, partial_score)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = app
        
        return best_match

    def open_app(self, search_term):
        # If search term contains youtube.com or youtube → use Chrome directly
        if 'youtube.com' in search_term.lower() or search_term.lower() == 'youtube':
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            subprocess.Popen([chrome_path, 'https://www.youtube.com'])
            print("Opened: YouTube in Chrome")
            return True
        # This must come BEFORE the pyautogui Win Search flow
        
        pyautogui.press("win")
        time.sleep(1)
        pyautogui.write(search_term)
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(0.5)
        pyautogui.press("esc")
        time.sleep(3)
        
        wm = WindowManager()
        if wm.find_window(search_term):
            print(f"Opened: {search_term}")
            return True
        
        if "chrome" in search_term.lower():
            try:
                subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
                print("Opened: Chrome")
                return True
            except Exception as e:
                print(f"Chrome launch failed: {e}")
        
        app = self.find_app(search_term)
        if app:
            try:
                cmd = f'start explorer.exe "shell:AppsFolder\\{app["id"]}"'
                subprocess.run(["powershell", "-Command", cmd], timeout=10)
                print(f"Opened: {app['name']}")
                app_wait_times = {
                    'calculator': 3.0,
                    'settings': 2.0,
                    'microsoft store': 3.0,
                    'store': 3.0,
                    'paint': 2.0,
                    'notepad': 1.5,
                    'chrome': 2.0,
                    'spotify': 4.0,
                }
                app_lower = search_term.lower()
                extra_wait = 0
                for app_key, wait_time in app_wait_times.items():
                    if app_key in app_lower:
                        extra_wait = wait_time
                        break
                if extra_wait > 0:
                    time.sleep(extra_wait)
                return True
            except Exception as e:
                print(f"Fallback method failed: {e}")
        
        print(f"Could not open: {search_term}")
        return False


class BrowserManager:
    @staticmethod
    def is_url(term):
        if not term:
            return False
        term_lower = term.lower()
        if term_lower.startswith("http://") or term_lower.startswith("https://"):
            return True
        url_extensions = [".com", ".org", ".net", ".io", ".co", ".gov", ".edu", ".uk", ".us"]
        return any(term_lower.endswith(ext) or "." in term_lower for ext in url_extensions)
    
    def open_url(self, url_str):
        if ' ' in url_str or url_str.lower().startswith('open'):
            print(f"[Jarvis] Invalid URL: {url_str}")
            print("[Jarvis] Tip: Use 'then' between commands")
            return False
        
        if not url_str.startswith("http://") and not url_str.startswith("https://"):
            if not url_str.startswith("www."):
                url_str = "https://" + url_str
        
        chrome_running = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == 'chrome.exe':
                    chrome_running = True
                    break
            except:
                pass
        
        if chrome_running:
            # Bug 2 Fix: Retry loop for finding Chrome window
            windows = []
            for attempt in range(10):
                windows = [w for w in gw.getAllWindows() 
                           if "chrome" in w.title.lower() or "google" in w.title.lower()]
                if windows:
                    break
                time.sleep(0.8)
            
            if windows:
                win = windows[0]
                hwnd = win._hWnd
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                    except:
                        win.activate()
                    
                    time.sleep(0.4)
                    pyautogui.hotkey("ctrl", "t")
                    time.sleep(0.6)
                    pyautogui.write(url_str, interval=0.02)
                    pyautogui.press("enter")
                    print(f"[Jarvis] Opened URL in existing Chrome: {url_str}")
                    return True
                except Exception as e:
                    print(f"[Jarvis] Focus failed: {e}")
            else:
                print("[Jarvis] Chrome window not ready, try again")
                return False
        
        try:
            subprocess.Popen([CHROME_EXE, url_str])
            print(f"[Jarvis] Launched Chrome with: {url_str}")
            return True
        except Exception as e:
            print(f"[Jarvis] Failed to open URL: {e}")
            return False
    
    def navigate_chrome_to_url(self, url: str):
        """Navigate existing Chrome window to URL. Re-finds window fresh each call."""
        wins = [w for w in gw.getAllWindows()
                if ('chrome' in w.title.lower() or 'google' in w.title.lower())
                and 'edge' not in w.title.lower() and w.visible]
        if not wins:
            subprocess.Popen([CHROME_EXE, url])
            return
        win = wins[0]
        hwnd = win._hWnd
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.8)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.write(url, interval=0.03)
            pyautogui.press('enter')
        except Exception:
            subprocess.Popen([CHROME_EXE, url])

    def search_youtube_with_pick(self, query: str, pick: str):
        """Search YouTube and automatically pick result number."""
        import io
        import sys
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(pick + '\n')
        try:
            self.search_youtube(query, False)
        finally:
            sys.stdin = old_stdin

    def search_youtube_autopick(self, query: str, pick_num: str):
        """Search YouTube and auto-pick result number."""
        import io
        import sys
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(str(pick_num) + '\n')
        try:
            self.search_youtube(query, False)
        finally:
            sys.stdin = old_stdin

    def close_tab(self, url_query):
        stripped_query = url_query.lower().replace("www.", "").replace("https://", "").replace("http://", "")
        for tld in [".com", ".org", ".net", ".io", ".co", ".gov", ".edu", ".uk", ".us"]:
            stripped_query = stripped_query.replace(tld, "")
        stripped_query = stripped_query.split('.')[0]
        
        windows = []
        for attempt in range(10):
            windows = [w for w in gw.getAllWindows() if "google chrome" in w.title.lower()]
            if windows:
                break
            time.sleep(0.6)
        
        if not windows:
            print(f"[Jarvis] No Chrome window found")
            return False
        
        chrome_win = windows[0]
        hwnd = chrome_win._hWnd
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                chrome_win.activate()
            time.sleep(0.5)
        except Exception as e:
            print(f"[Jarvis] Failed to focus Chrome: {e}")
            return False
        
        pyautogui.hotkey("ctrl", "1")
        time.sleep(0.4)
        
        for i in range(20):
            try:
                active_win = gw.getActiveWindow()
                if active_win:
                    score = fuzz.WRatio(stripped_query, active_win.title.lower())
                    if score >= 45:
                        time.sleep(0.2)
                        pyautogui.hotkey("ctrl", "w")
                        print(f"[Jarvis] Closed tab: {url_query}")
                        return True
            except:
                pass
            
            if i < 19:
                pyautogui.hotkey("ctrl", "tab")
                time.sleep(0.6)
        
        print(f"[Jarvis] Tab not found: '{url_query}'")
        return False

    def _focus_tab(self, url_query):
        """Focus a specific tab by URL without closing it."""
        stripped_query = url_query.lower().replace("www.", "").replace("https://", "").replace("http://", "")
        for tld in [".com", ".org", ".net", ".io", ".co", ".gov", ".edu", ".uk", ".us"]:
            stripped_query = stripped_query.replace(tld, "")
        stripped_query = stripped_query.split('.')[0]
        
        # More windows to find Chrome - it might have multiple processes
        windows = []
        for attempt in range(15):
            windows = [w for w in gw.getAllWindows() if "google chrome" in w.title.lower() and w.visible]
            if windows:
                break
            time.sleep(0.5)
        
        if not windows:
            print(f"[Jarvis] No Chrome window found")
            return False
        
        chrome_win = windows[0]
        hwnd = chrome_win._hWnd
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                chrome_win.activate()
            time.sleep(0.8)  # More time to focus
        except Exception as e:
            print(f"[Jarvis] Failed to focus Chrome: {e}")
            return False
        
        # Start from current tab (don't force ctrl+1)
        time.sleep(0.3)
        
        for i in range(20):
            try:
                active_win = gw.getActiveWindow()
                if active_win:
                    title_lower = active_win.title.lower()
                    # Check if this is the tab we want - be more lenient with matching
                    score = fuzz.WRatio(stripped_query, title_lower)
                    # Also check if the stripped_query is part of the title
                    if score >= 40 or stripped_query in title_lower:
                        print(f"[Jarvis] Focused: {url_query}")
                        return True
            except:
                pass
            
            if i < 19:
                pyautogui.hotkey("ctrl", "tab")
                time.sleep(0.5)  # More time between tab switches
        
        print(f"[Jarvis] Tab not found to focus: '{url_query}'")
        return False

    def search_youtube(self, query: str, auto_play_first: bool = False):
        """
        YouTube search with reliable URL navigation:
        1. Open Chrome → go to YouTube via URL
        2. Navigate to search URL directly
        3. Fetch titles via yt-dlp
        4. Show numbered list
        5. User picks → play that video
        """
        import urllib.parse

        query = query.strip('"').strip("'")
        query = re.sub(r'\s+then\s*$', '', query, flags=re.IGNORECASE)
        query = re.sub(r'^search\s+', '', query, flags=re.IGNORECASE)
        query = query.strip()

        CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(CHROME_EXE):
            CHROME_EXE = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        subprocess.Popen([CHROME_EXE, '--new-tab', 'https://www.youtube.com'])
        print(f"[Jarvis] YouTube khul raha hai...")
        time.sleep(4.0)

        yt_win = None
        for attempt in range(15):
            wins = [w for w in gw.getAllWindows()
                    if 'youtube' in w.title.lower()
                    and 'google chrome' in w.title.lower()
                    and w.visible]
            if wins:
                yt_win = wins[0]
                break
            time.sleep(0.5)

        if not yt_win:
            for attempt in range(5):
                wins = [w for w in gw.getAllWindows()
                        if ('chrome' in w.title.lower()
                            or 'google chrome' in w.title.lower())
                        and 'edge' not in w.title.lower()
                        and w.visible]
                if wins:
                    yt_win = wins[0]
                    break
                time.sleep(0.5)

        if not yt_win:
            print("[Jarvis] Chrome window nahi mila.")
            return False

        hwnd = yt_win._hWnd
        orig_rect = win32gui.GetWindowRect(hwnd)
        was_maximized = (win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMAXIMIZED)

        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.15)
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1.2)
        except Exception as e:
            print(f"[Jarvis] Focus error: {e}")

        encoded = urllib.parse.quote(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"

        print(f"[Jarvis] YouTube pe '{query}' search kar raha hoon...")

        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(search_url, interval=0.03)
        pyautogui.press('enter')
        time.sleep(3.0)

        print("[Jarvis] Results load ho gaye, titles fetch kar raha hoon...")

        # ── STEP 4: Fetch titles via yt-dlp in background ──
        import yt_dlp
        videos = []
        try:
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                r = ydl.extract_info(f'ytsearch12:{query}', download=False)
                raw = r.get('entries', [])
                videos = [v for v in raw
                         if v.get('duration') and v.get('duration') > 30
                         and v.get('id')
                         and '/shorts/' not in v.get('webpage_url', '')]
                videos = videos[:10]
        except Exception as e:
            print(f"[Jarvis] Titles fetch failed: {e}")
            return False

        # ── STEP 5: Show numbered list in terminal ──
        print(f"\n[Jarvis] '{query}' ke {len(videos)} videos:\n")
        for i, v in enumerate(videos, 1):
            title = v.get('title') or 'Unknown'
            channel = v.get('channel') or v.get('uploader') or 'Unknown'
            dur = v.get('duration', 0)
            dur_str = f"{int(dur//60)}:{int(dur%60):02d}" if dur else "?"
            print(f"  {i:2}. {title}")
            print(f"      └─ {channel} | {dur_str}")
        print(f"\n   0. Cancel\n")

        # ── STEP 6: auto_play_first OR ask user ──
        if auto_play_first:
            video = videos[0] if videos else None
        else:
            choice = input("Kaunsa video play karein (0-10 ya naam): ").strip()
            if not choice or choice == '0':
                print("[Jarvis] Cancel.")
                if not was_maximized:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    left, top, right, bottom = orig_rect
                    win32gui.MoveWindow(hwnd, left, top, right-left, bottom-top, True)
                return False
            
            if choice.isdigit():
                idx = int(choice) - 1
                video = videos[idx] if 0 <= idx < len(videos) else None
            else:
                # Name match
                cl = choice.lower()
                video = next((v for v in videos
                             if cl in (v.get('title','').lower()) or
                             cl in (v.get('channel','').lower())), None)
            
            if not video:
                print("[Jarvis] Match nahi mila.")
                return False

        # ── STEP 7: Navigate Chrome to video URL (NO new window) ──
        url = (video.get('webpage_url') or
               f"https://www.youtube.com/watch?v={video['id']}")
        title = video.get('title', 'Unknown')
        channel = video.get('channel', video.get('uploader', ''))
        
        print(f"[Jarvis] Playing: {title} by {channel}")
        
        # Re-focus Chrome window
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            # Navigate using address bar
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.write(url, interval=0.03)
            pyautogui.press('enter')
            time.sleep(1.0)
        except:
            subprocess.Popen([CHROME_EXE, url])
        
        # Restore window if it was not maximized before
        if not was_maximized:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                left, top, right, bottom = orig_rect
                win32gui.MoveWindow(hwnd, left, top, right-left, bottom-top, True)
            except:
                pass
        
        return True


class MediaManager:
    def __init__(self):
        self._current_volume = 50
        self._is_muted = False
        self._is_hinglish = False

    def _print(self, english_msg, hinglish_msg=None):
        if self._is_hinglish and hinglish_msg:
            print(hinglish_msg)
        else:
            print(english_msg)

    def _run_nircmd(self, *args):
        """Safe nircmd wrapper — never runs without arguments."""
        if not NIRCMD_AVAILABLE:
            return
        if not args:
            return
        cmd = [NIRCMD] + list(args)
        subprocess.run(cmd,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW)

    def _read_system_volume(self):
        """Read current volume using Windows API — no nircmd needed."""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume_interface.GetMasterVolumeLevelScalar()
            return int(round(current * 100))
        except Exception:
            return self._current_volume

    def get_system_volume(self):
        return self._current_volume

    def set_volume(self, level):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return self._current_volume
        level = max(0, min(100, level))
        nircmd_value = int(65535 * level / 100)
        self._run_nircmd('setsysvolume', str(nircmd_value))
        time.sleep(0.1)
        self._current_volume = level
        if self._is_muted:
            self._run_nircmd('mutesysvolume', '0')
            time.sleep(0.1)
            self._run_nircmd('setsysvolume', str(nircmd_value))
            self._is_muted = False
        self._print(f"[Jarvis] Volume set to {self._current_volume}%", f"[Jarvis] Awaaz {self._current_volume}% ho gayi ✓")
        return self._current_volume

    def volume_up(self):
        new_vol = min(100, self._current_volume + 10)
        self.set_volume(new_vol)
        print(f"[Jarvis] Volume up: {self._current_volume}%")

    def volume_down(self):
        new_vol = max(0, self._current_volume - 10)
        self.set_volume(new_vol)
        print(f"[Jarvis] Volume down: {self._current_volume}%")

    def mute_volume(self):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return False
        if self._is_muted:
            self._print("[Jarvis] Already muted", "[Jarvis] Pehle se hi mute hai")
            return True
        self._run_nircmd('mutesysvolume', '1')
        self._is_muted = True
        self._print("[Jarvis] Volume muted", "[Jarvis] Awaz band ho gayi ✓")
        return True

    def unmute_volume(self):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return False
        if not self._is_muted:
            self._print("[Jarvis] Already unmuted", "[Jarvis] Pehle se hi unmuted hai")
            return True
        self._run_nircmd('mutesysvolume', '0')
        time.sleep(0.15)
        nircmd_value = int(65535 * self._current_volume / 100)
        self._run_nircmd('setsysvolume', str(nircmd_value))
        self._is_muted = False
        self._print(f"[Jarvis] Volume unmuted: {self._current_volume}%", f"[Jarvis] Awaaz {self._current_volume}% ho gayi ✓")
        return True


async def get_all_sessions_async():
    try:
        session_manager = await WinRTMediaManager.request_async()
        sessions_list = session_manager.get_sessions()
        result = {}
        for session in sessions_list:
            try:
                app_id = session.source_app_user_model_id
                if app_id:
                    result[app_id.lower()] = session
                    raw_id = app_id.lower()
                    if 'spotify' in raw_id:
                        short = 'spotify'
                    elif 'chrome' in raw_id:
                        short = 'chrome'
                    elif 'vlc' in raw_id:
                        short = 'vlc'
                    elif 'msedge' in raw_id or 'edge' in raw_id:
                        short = 'edge'
                    elif 'firefox' in raw_id:
                        short = 'firefox'
                    else:
                        short = raw_id.split('.')[0].replace('desktop','').replace('app','').replace('ab','').strip()
                    result[short] = session
            except Exception:
                pass
        return result
    except Exception as e:
        print(f"[Jarvis] Error getting media sessions: {e}")
        return {}


def get_all_sessions():
    return run_async(get_all_sessions_async())


def find_session(app_hint):
    sessions = get_all_sessions()
    if not sessions:
        return None

    if not app_hint:
        for app_name, session in sessions.items():
            try:
                info = session.get_playback_info()
                if info and info.playback_status == 4:
                    return session
            except Exception:
                pass
        seen = set()
        for session in sessions.values():
            sid = id(session)
            if sid not in seen:
                seen.add(sid)
                return session
        return None

    hint = app_hint.lower().strip()
    hint_map = {
        'youtube': 'chrome',
        'yt': 'chrome',
        'browser': 'chrome',
        'google': 'chrome',
    }
    hint = hint_map.get(hint, hint)

    if hint in sessions:
        return sessions[hint]

    for key, session in sessions.items():
        if hint in key:
            return session

    try:
        from rapidfuzz import fuzz, process as fuzz_process
        keys = list(sessions.keys())
        match = fuzz_process.extractOne(hint, keys,
                                        scorer=fuzz.WRatio,
                                        score_cutoff=50)
        if match:
            return sessions[match[0]]
    except Exception:
        pass

    return None


    def _youtube_keyboard_next(self):
        """Press Shift+N on YouTube tab — skips to next video."""
        import pyautogui
        import time
        
        if not self._focus_chrome_tab('youtube'):
            return
        
        pyautogui.hotkey('shift', 'n')
        time.sleep(0.2)

    def _youtube_keyboard_previous(self):
        """Press Shift+P on YouTube tab — goes to previous video."""
        import pyautogui
        import time
        
        if not self._focus_chrome_tab('youtube'):
            return
        
        pyautogui.hotkey('shift', 'p')
        time.sleep(0.2)

    if not was_maximized:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            left, top, right, bottom = orig_rect
            win32gui.MoveWindow(hwnd, left, top,
                                right - left, bottom - top, True)
        except Exception:
            pass


async def media_action_async(action, app_hint=None, jarvis_instance=None):
    session = find_session(app_hint)
    if not session:
        if app_hint:
            print(f"[Jarvis] No media session found for: {app_hint}")
        else:
            print("[Jarvis] No active media app found.")
        return False

    try:
        raw = session.source_app_user_model_id.lower()
        # Known app ID mappings
        if 'spotify' in raw:
            display = 'Spotify'
        elif 'chrome' in raw:
            display = 'Chrome'
        elif 'vlc' in raw:
            display = 'VLC'
        elif 'msedge' in raw or 'edge' in raw:
            display = 'Edge'
        elif 'firefox' in raw:
            display = 'Firefox'
        else:
            display = raw.split('.')[0].replace('desktop','').replace('ab','').title()
    except Exception:
        display = app_hint or "Unknown"

    try:
        is_chrome = False
        try:
            raw_id = session.source_app_user_model_id.lower()
            is_chrome = 'chrome' in raw_id or 'msedge' in raw_id
        except Exception:
            pass

        if action in ("play", "resume"):
            await session.try_play_async()
            print(f"[Jarvis] Play: {display}")

        elif action == "pause":
            await session.try_pause_async()
            print(f"[Jarvis] Pause: {display}")

        elif action in ("next", "skip"):
            if is_chrome and jarvis_instance:
                jarvis_instance._youtube_keyboard_next()
            elif is_chrome:
                _youtube_keyboard_next()
            else:
                await session.try_skip_next_async()
            print(f"[Jarvis] Next: {display}")

        elif action in ("prev", "previous"):
            if is_chrome and jarvis_instance:
                jarvis_instance._youtube_keyboard_previous()
            elif is_chrome:
                _youtube_keyboard_previous()
            else:
                await session.try_skip_previous_async()
            print(f"[Jarvis] Previous: {display}")

        else:
            print(f"[Jarvis] Unknown media action: {action}")
            return False
        return True
    except Exception as e:
        print(f"[Jarvis] Media action failed: {e}")
        return False


def handle_media(action, app_hint=None, jarvis_instance=None):
    return run_async(media_action_async(action, app_hint, jarvis_instance))


async def _list_sessions_async():
    sessions = await get_all_sessions_async()
    if not sessions:
        print("[Jarvis] No active media sessions")
        return
    seen = set()
    unique = []
    for key, session in sessions.items():
        sid = id(session)
        if sid not in seen:
            seen.add(sid)
            try:
                raw = session.source_app_user_model_id.lower()
                if 'spotify' in raw:
                    name = 'Spotify'
                elif 'chrome' in raw:
                    name = 'Chrome'
                elif 'vlc' in raw:
                    name = 'VLC'
                elif 'msedge' in raw or 'edge' in raw:
                    name = 'Edge'
                elif 'firefox' in raw:
                    name = 'Firefox'
                else:
                    name = raw.split('.')[0].replace('desktop','').replace('ab','').title()
                unique.append(name)
            except Exception:
                unique.append(key.title())
    print(f"\n[Jarvis] Active media apps: {', '.join(set(unique))}\n")


def list_media_sessions():
    run_async(_list_sessions_async())


class WindowManager:
    EXCLUDED_TITLES = ['powershell', 'cmd', 'popuphost', 
                       'windows input experience',
                       'program manager', 'rainmeter']

    def get_windows(self):
        try:
            windows = gw.getAllWindows()
            return [{"title": w.title, "hwnd": w._hWnd, "window": w} for w in windows if w.title.strip()]
        except Exception as e:
            print(f"Error getting windows: {e}")
            return []

    def _wait_for_window(self, query, timeout=8, interval=0.5):
        """Poll until window appears or timeout. Returns win dict or None."""
        import time
        elapsed = 0
        while elapsed < timeout:
            win = self.find_window(query)
            if win:
                return win
            time.sleep(interval)
            elapsed += interval
        return None

    def _is_excluded(self, title):
        title_lower = title.lower()
        return any(excl in title_lower for excl in self.EXCLUDED_TITLES)

    def _get_process_name(self, hwnd):
        try:
            import ctypes
            from ctypes import wintypes
            GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
            pid = wintypes.DWORD()
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            proc = psutil.Process(pid.value)
            return proc.name().lower()
        except:
            return None

    def find_window(self, query):
        windows = self.get_windows()
        if not windows:
            return None
        
        query_lower = query.lower()
        candidates = [w for w in windows if not self._is_excluded(w["title"])]
        
        if not candidates:
            return None
        
        # Step 0: Exact process name match (most reliable)
        process_map = {
            'notepad': 'notepad.exe',
            'chrome': 'chrome.exe',
            'calculator': 'calculatorapp.exe',
            'spotify': 'spotify.exe',
            'settings': 'systemsettings.exe',
            'explorer': 'explorer.exe',
            'file explorer': 'explorer.exe',
            'edge': 'msedge.exe',
            'vlc': 'vlc.exe',
            'discord': 'discord.exe',
            'whatsapp': 'whatsapp.exe',
        }
        
        target_process = process_map.get(query_lower)
        if target_process:
            for win in candidates:
                proc_name = self._get_process_name(win["hwnd"])
                if proc_name and target_process in proc_name.lower():
                    return win
        
        for win in candidates:
            proc_name = self._get_process_name(win["hwnd"])
            if proc_name and query_lower in proc_name.lower():
                return win

        query_words = query_lower.split()
        for win in candidates:
            title_lower = win["title"].lower()
            if all(word in title_lower for word in query_words):
                return win

        for win in candidates:
            if query_lower in win["title"].lower():
                return win

        terminal_aliases = {
            'terminal': ['windows powershell', 'powershell',
                         'command prompt', 'cmd', 'windows terminal',
                         'ps c:\\'],
            'cmd': ['command prompt', 'cmd.exe'],
            'powershell': ['windows powershell', 'powershell'],
        }

        if query_lower in terminal_aliases:
            search_terms = terminal_aliases[query_lower]
            for win in candidates:
                title_lower = win["title"].lower()
                if any(term in title_lower for term in search_terms):
                    return win

        best_match = None
        best_score = 70
        
        for win in candidates:
            score = fuzz.ratio(query_lower, win["title"].lower())
            partial_score = fuzz.partial_ratio(query_lower, win["title"].lower())
            combined_score = max(score, partial_score)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = win
        
        return best_match

    def focus_terminal(self):
        """Bring Jarvis terminal window to foreground."""
        try:
            # Find terminal/powershell window
            terminal_win = self.find_window('powershell')
            if not terminal_win:
                terminal_win = self.find_window('terminal')
            if not terminal_win:
                terminal_win = self.find_window('cmd')
            
            if terminal_win:
                hwnd = terminal_win['hwnd']
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                return True
        except:
            pass
        return False

    def _get_process_info(self, hwnd):
        try:
            import ctypes
            from ctypes import wintypes
            GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
            pid = wintypes.DWORD()
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return psutil.Process(pid.value)
        except:
            return None

    def close_window(self, query, original_name=None):
        win = self.find_window(query)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        hwnd = win["hwnd"]
        
        # Use original_name for display if provided, otherwise use window title
        display_name = original_name if original_name else title
        
        # Try normal close first
        try:
            win["window"].close()
            time.sleep(0.5)
            # Verify it actually closed
            still_open = self.find_window(query)
            if not still_open:
                print(f"[Jarvis] Closed: {display_name}")
                return True
        except:
            pass
        
        # Force kill process (works for UWP apps like Calculator)
        try:
            proc = self._get_process_info(hwnd)
            if proc:
                proc.kill()
                time.sleep(0.3)
                print(f"[Jarvis] Closed: {display_name}")
                return True
        except:
            pass
        
        # Last resort: taskkill
        try:
            import ctypes
            from ctypes import wintypes
            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(pid))
            subprocess.run(
                ['taskkill', '/F', '/PID', str(pid.value)],
                capture_output=True)
            print(f"[Jarvis] Closed: {display_name}")
            return True
        except:
            pass
        
        print(f"[Jarvis] Could not close: {display_name}")
        return False

    def minimize_window(self, query):
        win = self.find_window(query) or self._wait_for_window(query, timeout=8)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        hwnd = win["hwnd"]
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            time.sleep(0.3)
            print(f"[Jarvis] Minimized: {title}")
            return True
        except Exception as e:
            print(f"Failed to minimize: {e}")
            return False

    def maximize_window(self, title_keyword):
        matched = self.find_window(title_keyword) or self._wait_for_window(title_keyword, timeout=8)
        if not matched:
            print(f"[Jarvis] Window not found: {title_keyword}")
            return False
        
        hwnd = matched['hwnd']
        title = matched['title']
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
        except Exception:
            pass
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
            time.sleep(0.3)
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMAXIMIZED:
                print(f"[Jarvis] Maximized: {title}")
                return True
        except Exception:
            pass
        
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            import pyautogui
            pyautogui.hotkey('win', 'up')
            time.sleep(0.3)
            print(f"[Jarvis] Maximized: {title}")
            return True
        except Exception as e:
            print(f"[Jarvis] Maximize failed: {title} - {e}")
            return False

    def restore_window(self, query):
        win = self.find_window(query) or self._wait_for_window(query, timeout=8)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        hwnd = win["hwnd"]
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
            print(f"[Jarvis] Restored: {title}")
            return True
        except Exception as e:
            print(f"Failed to restore: {e}")
            return False

    def focus_window(self, query):
        win = self.find_window(query) or self._wait_for_window(query, timeout=8)
        if not win:
            print(f"Window not found: {query}")
            return False

        title = win["title"]
        hwnd = win["hwnd"]

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)

            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            print(f"[Jarvis] Focused: {title}")
            return True
        except Exception as e:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
                win32gui.SetForegroundWindow(hwnd)
                print(f"[Jarvis] Focused: {title}")
                return True
            except:
                print(f"Focus failed: {e}")
                return False


class Jarvis:
    def __init__(self):
        self.app_manager = AppManager()
        self.window_manager = WindowManager()
        self.file_manager = FileManager()
        self.browser_manager = BrowserManager()
        self.media_manager = MediaManager()
        self.memory = MemoryManager()
        self.running = True
        self._last_opened_app = self.memory.get_last_app()
        self._prev_opened_app = None
        self.last_was_hinglish = False
        self._brain_call_count = 0
        self._processing_input = False
        self._yt_auto_play = False
        self._yt_auto_pick = None
        # Track apps opened in CURRENT command chain (for "close dono")
        self._chain_opened_apps = []

    def _hinglish_print(self, english_msg, hinglish_msg):
        if self.last_was_hinglish and hinglish_msg:
            print(hinglish_msg)
        else:
            print(english_msg)

    def print_banner(self):
        # Premium JARVIS Banner with Rainbow Gradient (RGB)
        banner = """
\033[38;2;0;255;255m      ██╗\033[38;2;43;255;212m  █████╗\033[38;2;85;255;170m  ██████╗\033[38;2;128;255;128m  ██╗   ██╗\033[38;2;170;255;85m  ██╗\033[38;2;212;255;43m  ███████╗
\033[38;2;0;255;255m      ██║\033[38;2;43;255;212m ██╔══██╗\033[38;2;85;255;170m ██╔══██╗\033[38;2;128;255;128m ██║   ██║\033[38;2;170;255;85m ██║\033[38;2;212;255;43m  ██╔════╝
\033[38;2;0;255;255m      ██║\033[38;2;43;255;212m ███████║\033[38;2;85;255;170m ██████╔╝\033[38;2;128;255;128m ██║   ██║\033[38;2;170;255;85m ██║\033[38;2;212;255;43m  ███████╗
\033[38;2;0;255;255m██╗   ██║\033[38;2;43;255;212m ██╔══██║\033[38;2;85;255;170m ██╔══██║\033[38;2;128;255;128m ╚██╗ ██╔╝\033[38;2;170;255;85m ██║\033[38;2;212;255;43m  ╚════██║
\033[38;2;0;255;255m╚██████╔╝\033[38;2;43;255;212m ██║  ██║\033[38;2;85;255;170m ██║  ██║\033[38;2;128;255;128m  ╚████╔╝\033[38;2;170;255;85m  ██║\033[38;2;212;255;43m  ███████║
\033[38;2;0;255;255m ╚═════╝\033[38;2;43;255;212m  ╚═╝  ╚═╝\033[38;2;85;255;170m ╚═╝  ╚═╝\033[38;2;128;255;128m   ╚═══╝\033[38;2;170;255;85m   ╚═╝\033[38;2;212;255;43m  ╚══════╝\033[0m
\033[93m                      Your Terminal Assistant\033[0m
        """
        print(banner)
        print("\033[95m WELCOME SIR, HOW MAY I HELP YOU ?\033[0m\n")

    def parse_command(self, line):
        parts = line.strip().split(maxsplit=1)
        if not parts:
            return None, None
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        return cmd, arg

    def _create_file_with_content(self, filename, topic):
        import os
        
        content_prompt = f"""Generate complete, detailed content for a file about: {topic}
        
Format it properly with:
- Clear headings and sections
- Complete explanations  
- Code examples if relevant
- No placeholder text — real useful content only

Generate the full file content now:"""
        
        try:
            from brain import think
            result = think(content_prompt)
            if result.get('type') == 'conversation':
                content = result.get('reply', '').strip()
                provider = result.get('provider', 'Unknown')
                print(f"[Generating file using {provider}...]")
            else:
                content = f"# {topic}\n\nContent about {topic}."
        except Exception as e:
            content = f"# {topic}\n\nContent about {topic}."
        
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[Jarvis] File created: {filepath}")
        print(f"[Jarvis] Content preview: {content[:100]}...")
        return filepath

    def handle_command(self, cmd, arg):
        if cmd in ('close', 'band', 'bandh', 'hatao'):
            cmd = 'close'
        
        WINDOW_ACTIONS = {'close', 'minimize', 'maximize', 'restore', 'focus'}
        if cmd in WINDOW_ACTIONS:
            if not arg or arg.lower().strip() in {'karo', 'kar', 'kro', 'kardo', 'krdo', 'do', 'dena', 'dijiye', 'de', 'please', 'plz', 'na', 'toh', 'to', 'bhi', 'hi', 'jaldi', 'abhi', 'zara', 'jara'}:
                arg = self._last_opened_app or self.memory.get_last_app()
                if not arg:
                    print("[Jarvis] Kaunsa app? Pehle koi app kholo.")
                    return
        
        HINDI_PARTICLES = {
            'karo', 'kar', 'kro', 'kardo', 'krdo',
            'do', 'dena', 'dijiye', 'de',
            'please', 'plz', 'na', 'toh', 'to',
            'bhi', 'hi', 'jaldi', 'abhi', 'zara',
            'jara', 'karna', 'krna', 'ja', 'jao',
        }
        if arg and arg.lower().strip() in HINDI_PARTICLES:
            arg = None

        self.media_manager._is_hinglish = self.last_was_hinglish
        if cmd == "exit":
            self.running = False
            print("Goodbye!")
            
        elif cmd == "go to":
            if not arg:
                print("Usage: go to <URL>")
            else:
                self.browser_manager.open_url(arg)

        elif cmd == "search":
            if arg and ('youtube' in arg.lower() or 'yt' in arg.lower()):
                query = arg.lower().replace('youtube', '').replace(
                        'yt', '').replace('on', '').replace(
                        'pe', '').strip()
                self.browser_manager.search_youtube(query)
            else:
                if arg:
                    self.browser_manager.open_url(
                        f"https://www.google.com/search?q={arg}")
            
        elif cmd == "open":
            if not arg:
                print("Usage: open <app name or filename or URL>")
            # Bug 1 Fix: Priority order - File extension -> URL -> App
            # Extension check first
            elif any(arg.lower().endswith(ext) for ext in ['.pdf', '.txt', '.docx', '.xlsx', '.pptx', '.mp4', '.mp3', '.png', '.jpg', '.jpeg', '.zip', '.rar', '.csv', '.py', '.js', '.html']):
                self.file_manager.search_and_open(arg)
            # URL check second
            elif self.browser_manager.is_url(arg):
                self.browser_manager.open_url(arg)
                # Track URL in chain for "close dono" feature
                if arg not in self._chain_opened_apps:
                    self._chain_opened_apps.append(arg)
            # App check third
            else:
                # Check if already open — focus instead of reopen
                existing = self.window_manager.find_window(arg)
                if existing and not self.browser_manager.is_url(arg):
                    self.window_manager.focus_window(arg)
                    self._prev_opened_app = self._last_opened_app
                    self._last_opened_app = arg
                    self.memory.set_last_app(arg)
                    print(f"[Jarvis] Already open, focused: {arg}")
                    return
                
                # Not open — proceed with normal open
                result = self.app_manager.open_app(arg)
                if result is not False:
                    self._prev_opened_app = self._last_opened_app
                    self._last_opened_app = arg
                    self.memory.set_last_app(arg)
                    self.memory.log_activity('app_opened', {'app': arg})
                    # Track in chain for "close dono" feature
                    if arg not in self._chain_opened_apps:
                        self._chain_opened_apps.append(arg)
                else:
                    print("[Jarvis] Tip: If this is a file, try: open filename.ext")
                
        elif cmd == "close":
            target = arg
            close_all_patterns = [
                'sab', 'sabhi', 'all', 'sare', 'sarhi', 'sabhi apps',
                'sabhi apps band karo', 'sab band karo', 'sabhi band karo',
                'all apps', 'close all', 'sab kuch band karo'
            ]
            if target and target.strip().lower() in close_all_patterns:
                windows = self.window_manager.get_windows()
                
                # Get all windows but filter out system/terminal windows
                # Use WindowManager's exclusion logic + extra filters
                never_close_keywords = [
                    'jarvis', 'powershell', 'cmd', 'terminal', 
                    'visual studio', 'program manager', 'rainmeter', 
                    'desktop', 'explorer', 'settings', 'windows input',
                    'input experience', 'search', 'start', 'notification',
                    'task view', 'calendar', 'phone', 'maps', 'weather',
                    'store', 'microsoft store', 'edge', 'chrome',
                    '.ini', 'antigravity', 'mond', 'clock', 'weather', 'recycle bin',
                ]
                
                # Filter windows to close
                apps_to_close = []
                for w in windows:
                    title = w.get('title', '')
                    title_lower = title.lower()
                    
                    # Skip empty titles
                    if not title.strip():
                        continue
                    
                    # Skip if matches never_close keywords
                    if any(kw in title_lower for kw in never_close_keywords):
                        continue
                    
                    # Skip system windows with no meaningful title
                    if len(title.strip()) < 3:
                        continue
                    
                    apps_to_close.append(w)
                
                if not apps_to_close:
                    print("[Jarvis] Koi close karne layak app nahi mila.")
                    return
                
                # Show what we're closing
                app_names = [w['title'] for w in apps_to_close]
                print(f"[Jarvis] {len(app_names)} apps band kar raha hoon: {app_names}")
                
                # Close each app
                for w in apps_to_close:
                    title = w.get('title', '')
                    hwnd = w.get('hwnd')
                    try:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                    except:
                        pass
                    try:
                        w['window'].close()
                        print(f"[Jarvis] Closed: {title}")
                    except:
                        try:
                            proc = self.window_manager._get_process_info(hwnd)
                            if proc:
                                proc.kill()
                                print(f"[Jarvis] Closed: {title}")
                        except:
                            print(f"[Jarvis] Could not close: {title}")
                    time.sleep(0.3)
                return
            
            if target and target.strip().lower() in ('dono', 'dono ko', 'both', '__dono__'):
                # First check chain apps (from current command like "open chrome then open notepad then close dono")
                apps_to_close = []
                if self._chain_opened_apps:
                    # Reverse order - last opened closes first (github.com first, then youtube.com)
                    apps_to_close = list(reversed(self._chain_opened_apps))
                else:
                    # Fall back to memory's app history
                    app_history = self.memory.get_app_history(2)
                    if len(app_history) >= 2:
                        app_history = list(reversed(app_history))
                
                if not apps_to_close:
                    print("[Jarvis] Koi app track nahi hai. Pehle koi app kholo.")
                    return
                
                print(f"[Jarvis] Closing: {', '.join(apps_to_close)}")
                
                # For browser tabs, we need special handling - close without cycling tabs
                for app in apps_to_close:
                    if self.browser_manager.is_url(app):
                        # Directly attempt to close the tab - it will auto-focus first
                        self.browser_manager.close_tab(app)
                    else:
                        self.window_manager.focus_window(app)
                        time.sleep(0.3)
                        self.window_manager.close_window(app, original_name=app)
                    time.sleep(0.5)  # Wait between closes
                # Clear chain after closing
                self._chain_opened_apps.clear()
                return
            if not target or target == '__last_app__' or (target.lower() in HINDI_PARTICLES):
                target = self._last_opened_app or self.memory.get_last_app()
                if not target:
                    self._hinglish_print(
                        "[Jarvis] Which app to close?",
                        "[Jarvis] Kaunsa app band karein?"
                    )
                    return
            if self.browser_manager.is_url(target):
                self.browser_manager.close_tab(target)
            else:
                self.window_manager.close_window(target)
                self._last_opened_app = target
                self.memory.set_last_app(target)
                
        elif cmd == "minimize":
            target = arg
            if not target or target == '__last_app__' or (target.lower() in HINDI_PARTICLES):
                target = self._last_opened_app or self.memory.get_last_app()
                if not target:
                    self._hinglish_print(
                        "[Jarvis] Which app to minimize?",
                        "[Jarvis] Kaunsa app chhota karein?"
                    )
                    return
            self.window_manager.minimize_window(target)
            self._last_opened_app = target
            self.memory.set_last_app(target)
                
        elif cmd == "maximize":
            target = arg
            if not target or target == '__last_app__' or (target.lower() in HINDI_PARTICLES):
                target = self._last_opened_app or self.memory.get_last_app()
                if not target:
                    self._hinglish_print(
                        "[Jarvis] Which app to maximize?",
                        "[Jarvis] Kaunsa app bada karein?"
                    )
                    return
            self.window_manager.maximize_window(target)
            self._last_opened_app = target
            self.memory.set_last_app(target)
                
        elif cmd == "restore":
            target = arg
            if not target or target == '__last_app__' or (target.lower() in HINDI_PARTICLES):
                target = self._last_opened_app or self.memory.get_last_app()
                if not target:
                    self._hinglish_print(
                        "[Jarvis] Which app to restore?",
                        "[Jarvis] Kaunsa app wapas laein?"
                    )
                    return
            self.window_manager.restore_window(target)
            self._last_opened_app = target
            self.memory.set_last_app(target)
                
        elif cmd == "focus":
            target = arg
            if not target or (target.lower() in HINDI_PARTICLES):
                target = self._last_opened_app or self.memory.get_last_app()
                if not target:
                    self._hinglish_print(
                        "[Jarvis] Which app to focus?",
                        "[Jarvis] Kaunsa app focus karein?"
                    )
                    return
            self.window_manager.focus_window(target)
            self._last_opened_app = target
            self.memory.set_last_app(target)
                
        elif cmd == "list":
            apps = self.app_manager.get_installed_apps(force_refresh=(arg is not None))
            if arg:
                arg_lower = arg.lower()
                apps = [a for a in apps if arg_lower in a["name"].lower()]
            
            if apps:
                print(f"\nInstalled Applications ({len(apps)}):")
                print("-" * 50)
                for app in apps[:50]:
                    print(f"  {app['name']}")
                if len(apps) > 50:
                    print(f"  ... and {len(apps) - 50} more")
            else:
                print("No apps found")

        elif cmd == "volume":
            if not arg:
                vol = self.media_manager.get_system_volume()
                print(f"[Jarvis] Current volume: {vol}%")
            elif arg.lower() == "up":
                self.media_manager.volume_up()
            elif arg.lower() == "down":
                self.media_manager.volume_down()
            elif arg.lower() == "mute":
                self.media_manager.mute_volume()
            elif arg.lower() == "unmute":
                self.media_manager.unmute_volume()
            elif arg and arg.isdigit():
                self.media_manager.set_volume(int(arg))
            elif arg.lower().startswith("set "):
                try:
                    level = int(arg.lower().replace("set ", "").strip())
                    self.media_manager.set_volume(level)
                except ValueError:
                    print("[Jarvis] Usage: volume set <0-100>")
            else:
                try:
                    level = int(arg.strip())
                    self.media_manager.set_volume(level)
                except ValueError:
                    print("[Jarvis] Usage: volume <up/down/mute/unmute/set 0-100>")

        elif cmd == "increase":
            if arg and arg.lower() == "volume":
                self.media_manager.volume_up()
            elif not arg:
                self.media_manager.volume_up()

        elif cmd == "decrease":
            if arg and arg.lower() == "volume":
                self.media_manager.volume_down()
            elif not arg:
                self.media_manager.volume_down()

        elif cmd == "mute":
            self.media_manager.mute_volume()

        elif cmd == "unmute":
            self.media_manager.unmute_volume()

        elif cmd == "media":
            if not arg:
                print("[Jarvis] Usage: media list")
            elif arg.lower() in ("list", "list media"):
                list_media_sessions()
            else:
                print("[Jarvis] Usage: media list")

        elif cmd in ("play", "pause", "next", "previous", "prev", "skip", "resume"):
            self.handle_media(cmd, arg)
            
        elif cmd == "set":
            self.handle_set_command(arg)
            
        elif cmd == "play_song":
            if not arg:
                print("[Jarvis] Kaunsa gaana bajana hai?")
                return
            song = arg.replace(" on spotify", "").replace(
                   "spotify pe ", "").replace("spotify mein ", "").strip()
            print(f"[Jarvis] Spotify pe '{song}' search kar raha hoon...")
            self._play_song_on_spotify(song)
            self.memory.log_activity('spotify_play', {'song': song})
            
        elif cmd == "search_youtube":
            auto = getattr(self, '_yt_auto_play', False)
            auto_pick = getattr(self, '_yt_auto_pick', None)
            self._yt_auto_play = False
            self._yt_auto_pick = None
            if not arg:
                print("[Jarvis] Kya search karna hai YouTube pe?")
                return

            pick_flag = '--pick' in arg

            if pick_flag:
                parts = arg.split('--pick')
                query = parts[0].strip()
                pick_num = parts[1].strip() if len(parts) > 1 else '1'
                match = re.search(
                    r'search[_\s]+(.+?)\s+on\s+(?:youtube|yt)',
                    query,
                    re.IGNORECASE
                )
                if match:
                    query = match.group(1).strip()
                else:
                    query = query.replace(" on youtube", "").replace(
                            "youtube pe ", "").strip()
                self._last_yt_search = query
                self.browser_manager.search_youtube_with_pick(query, pick_num)
                return

            query = arg.replace('--autoplay', '').strip()
            match = re.search(
                r'search[_\s]+(.+?)\s+on\s+(?:youtube|yt)',
                query,
                re.IGNORECASE
            )
            if match:
                query = match.group(1).strip()
            else:
                query = query.replace(" on youtube", "").replace(
                        "youtube pe ", "").strip()

            self._last_yt_search = query
            self.memory.log_activity('youtube_search', {'query': query})

            if auto_pick:
                self.browser_manager.search_youtube_autopick(query, auto_pick)
            elif auto:
                self.browser_manager.search_youtube(query, True)
            else:
                self.browser_manager.search_youtube(query, False)

        elif cmd == "web_search" or cmd == "websearch":
            if not arg:
                print("[Jarvis] Kya search karna hai?")
            else:
                print(f"[Jarvis] Web pe '{arg}' search kar raha hoon...")
                results = web_search(arg)
                print(results[:500])
                self.memory.log_activity('web_search', {'query': arg})
            
        elif cmd == "whatsapp_message":
            print(f"[Jarvis] WhatsApp message coming soon: {arg}")
            
        elif cmd == "type_text":
            print(f"[Jarvis] Type text coming soon: {arg}")

        elif cmd == "memory":
            if not arg or arg == 'status':
                self.memory.show_status()

            elif arg in ('clear', 'delete'):
                self.memory.delete_with_confirmation(days=30)

            elif arg.startswith('clear ') or arg.startswith('delete '):
                parts = arg.split()
                if len(parts) >= 2:
                    if parts[1] == 'all':
                        print("[Memory] Session aur daily log delete karein? (long term memory RAHEGI)")
                        confirm = input("Confirm (haan/nahi): ").strip().lower()
                        if confirm in ('haan', 'ha', 'yes', 'y', 'haa'):
                            self.memory.clear_all()
                            print("[Memory] Done.")
                        else:
                            print("[Memory] Cancel.")
                    elif parts[1] == 'history':
                        print("[Memory] Sab long term memories delete karein?")
                        confirm = input("Confirm (haan/nahi): ").strip().lower()
                        if confirm in ('haan', 'ha', 'yes', 'y', 'haa'):
                            self.memory.clear_history()
                            print("[Memory] Done.")
                        else:
                            print("[Memory] Cancel.")
                    else:
                        try:
                            days = int(parts[1])
                            self.memory.delete_with_confirmation(days=days)
                        except:
                            print("[Jarvis] Usage: memory clear <days/all/history>")
                else:
                    self.memory.delete_with_confirmation(days=30)

            elif arg == 'clear all':
                print("[Memory] Session aur daily log delete karein? (long term memory RAHEGI)")
                print("[Memory] Type 'HAAN' to confirm delete, anything else to cancel:")
                confirm = input(">>> ").strip().lower()
                if confirm in ('haan', 'ha', 'yes', 'y', 'haa'):
                    self.memory.clear_all()
                    print("[Memory] Done.")
                else:
                    print("[Memory] Cancel.")

            elif arg == 'clear history':
                print("[Memory] Sab long term memories delete karein?")
                print("[Memory] Type 'HAAN' to confirm delete, anything else to cancel:")
                confirm = input(">>> ").strip().lower()
                if confirm in ('haan', 'ha', 'yes', 'y', 'haa'):
                    self.memory.clear_history()
                    print("[Memory] Done.")
                else:
                    print("[Memory] Cancel.")

            elif arg == 'limit':
                limit_mb = self.memory.get_storage_limit_mb()
                print(f"[Memory] Current limit: {limit_mb}MB")

            elif arg.startswith('limit '):
                try:
                    mb = int(arg.replace('limit ', '').strip())
                    self.memory.set_storage_limit(mb)
                except:
                    print("[Jarvis] Usage: memory limit <MB>")

            elif arg.startswith('remember '):
                parts = arg[9:].strip().split()
                if len(parts) < 2:
                    print("[Memory] Usage: memory remember <key> <value>")
                    return
                value = parts[-1]
                key = ' '.join(parts[:-1])
                self.memory.remember(key, value)

            elif arg.startswith('forget '):
                key = arg[7:].strip()
                if key:
                    self.memory.forget(key)
                else:
                    print("[Jarvis] Usage: memory forget <key>")

            elif arg.startswith('recall '):
                key = arg[7:]
                if key:
                    val = self.memory.recall(key)
                    if val:
                        print(f"[Memory] {key}: {val}")
                    else:
                        print(f"[Memory] '{key}' nahi mila.")
                else:
                    print("[Jarvis] Usage: memory recall <key>")

            else:
                print("[Jarvis] Memory commands:")
                print("  memory status                    - Show full status")
                print("  memory remember <key> <value>   - Save permanently")
                print("  memory recall <key>              - Recall saved value")
                print("  memory forget <key>              - Delete saved value")
                print("  memory clear                      - Delete 30+ days old")
                print("  memory clear 7                   - Delete 7+ days old")
                print("  memory clear all                 - Delete session + daily log")
                print("  memory clear history             - Delete long term memories")
                print("  memory limit 500                 - Set storage limit to 500MB")
                print("  memory limit                      - Show current limit")
            
        elif cmd in ("create_file", "create"):
            if not arg:
                print("[Jarvis] Usage: create file <filename>")
                print("[Jarvis] Example: create file notes.txt")
                return
            
            arg_clean = re.sub(r'^file\s+', '', arg, flags=re.IGNORECASE).strip()
            
            content = ""
            filename = arg_clean
            
            # Single unified pattern that catches all variations with explicit file extension
            write_match = re.search(
                r'^(.+?\.[\w]+)\s+(?:and\s+)?(?:write|type|mein\s+likho|likho|likhna|with\s+content)\s+(.+)$',
                arg_clean,
                re.IGNORECASE | re.DOTALL
            )
            
            if write_match:
                filename = write_match.group(1).strip()
                raw_content = write_match.group(2).strip()
                
                # Decide: needs brain or direct text?
                code_keywords = [
                    'code', 'program', 'script', 'function', 'class',
                    'write a', 'make a', 'generate', 'create a',
                    'c++', 'python', 'java', 'html', 'css', 'javascript',
                    'sql', 'cpp', 'algorithm', 'sort', 'search',
                ]
                needs_brain = any(kw in raw_content.lower() for kw in code_keywords)
                
                if needs_brain:
                    # Generate via Cerebras API directly
                    print(f"[Jarvis] Generating content...")
                    try:
                        import requests
                        from dotenv import load_dotenv
                        load_dotenv()
                        CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
                        url = "https://api.cerebras.ai/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        body = {
                            "model": "llama3.1-8b",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Generate ONLY the requested content. No explanation. No markdown backticks. Just raw clean content ready to save in a file."
                                },
                                {"role": "user", "content": raw_content}
                            ],
                            "temperature": 0.3,
                            "max_tokens": 2000
                        }
                        r = requests.post(url, json=body, headers=headers, timeout=30)
                        if r.status_code == 200:
                            content = r.json()["choices"][0]["message"]["content"].strip()
                            # Strip markdown code fences
                            content = re.sub(r'^```\w*\n?', '', content)
                            content = re.sub(r'\n?```$', '', content)
                            content = content.strip()
                        else:
                            content = raw_content
                    except Exception as e:
                        print(f"[Jarvis] Content generation error: {e}")
                        content = raw_content
                else:
                    # Direct text — write as-is
                    content = raw_content
            else:
                filename = arg_clean
                topic = filename.rsplit('.', 1)[0] if '.' in filename else filename
                print(f"[Jarvis] Generating content for {filename}...")
                self._create_file_with_content(filename, topic)
                self.memory.log_activity('file_created', {
                    'filename': filename,
                    'has_content': True
                })
                return
            
            if '.' not in filename:
                print(f"[Jarvis] Extension missing. Example: notes.txt, code.py")
                return
            
            self.file_manager.create_file(filename, content)
            self.memory.log_activity('file_created', {
                'filename': filename,
                'has_content': bool(content)
            })
        
        elif cmd == "delete_file":
            if not arg:
                print("[Jarvis] Konsi file delete karni hai?")
                return
            filename = re.sub(r'^file\s+', '', arg, 
                             flags=re.IGNORECASE).strip()
            self.file_manager.show_in_explorer(filename)

        else:
            print(f"Unknown command: {cmd}")

    def handle_media(self, verb, args):
        action = verb
        app_hint = None
        
        full_input = ""
        if args:
            full_input = f"{verb} {args}".lower()
        else:
            full_input = verb.lower()
        
        compound_phrases = {
            "next": ["next track", "next song", "skip track", "skip song", "play next", "play next track", "play next song"],
            "previous": ["previous track", "previous song", "prev track", "prev song", "play previous", "play prev", "play previous track"],
            "play": ["play music", "play song", "play video", "play media", "resume"],
            "pause": ["pause media", "pause video", "pause music", "pause song"],
        }
        
        for key, phrases in compound_phrases.items():
            for phrase in phrases:
                if phrase in full_input:
                    action = key
                    break
            if action != verb:
                break
        
        if args:
            args_lower = args.lower().strip()

            if ' on ' in args_lower:
                parts = args_lower.split(' on ', 1)
                left = parts[0].strip()
                right = parts[1].strip()
                if left in ("play", "pause", "next", "previous", "prev", "skip", "resume"):
                    action = left
                app_hint = right
            elif args_lower.startswith('on '):
                app_hint = args_lower[3:].strip()
            else:
                words = args_lower.split()
                possible_actions = ["play", "pause", "next", "previous", "prev", "skip", "resume"]
                for i, word in enumerate(words):
                    if word in possible_actions:
                        app_hint = " ".join(words[:i]) if i > 0 else None
                        action = word
                        break
                if app_hint is None and action == verb:
                    app_hint = args_lower

            if app_hint:
                app_hint = app_hint.replace('on ', '').strip()
                if app_hint in ('spotify', 'spotify.com', 'open.spotify.com'):
                    app_hint = 'spotify'
                elif app_hint in ('youtube', 'yt', 'youtube.com'):
                    app_hint = 'youtube'
                elif app_hint in ('chrome', 'google chrome', 'browser'):
                    app_hint = 'chrome'
        
        if action in ("play", "pause", "next", "previous", "prev", "skip", "resume"):
            if action == "resume":
                action = "play"

            if app_hint == 'spotify':
                result = self._control_spotify_tab(action)
                if not result:
                    print("[Jarvis] Spotify tab not found")
                return

            elif app_hint == 'youtube':
                result = self._control_youtube_tab(action)
                if not result:
                    print("[Jarvis] YouTube tab not found")
                return

            elif app_hint == 'chrome':
                did_something = False
                if action in ('pause', 'play'):
                    sp = self._control_spotify_tab(action)
                    yt = self._control_youtube_tab(action)
                    did_something = sp or yt
                else:
                    did_something = self._control_youtube_tab(action)
                    if not did_something:
                        did_something = self._control_spotify_tab(action)
                if not did_something:
                    handle_media(action, None, jarvis_instance=self)
                return

            else:
                handle_media(action, app_hint, jarvis_instance=self)
    def _is_spotify_tab(self, title):
        if not title: return False
        t = title.lower()
        return ('spotify' in t or 
                'open.spotify' in t or
                '•' in title or
                t.startswith('spotify') or 
                t.endswith('- spotify') or 
                'spotify web' in t or
                'spotify player' in t)

    def _focus_chrome_tab(self, keyword):
        """Focus a Chrome tab containing the keyword."""
        import win32gui
        import win32con
        import win32com.client
        import pyautogui
        import time
        
        chrome_hwnds = []
        
        def find_chrome(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if title and 'google chrome' in title.lower():
                        results.append(hwnd)
                except:
                    pass
        
        win32gui.EnumWindows(find_chrome, chrome_hwnds)
        
        if not chrome_hwnds:
            def find_chrome_fallback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        if title and 'chrome' in title.lower():
                            results.append(hwnd)
                    except:
                        pass
            win32gui.EnumWindows(find_chrome_fallback, chrome_hwnds)
        
        if not chrome_hwnds:
            return False
        
        hwnd = chrome_hwnds[0]
        
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.4)
        except Exception:
            pass
        
        # Check current tab first!
        try:
            current_title = win32gui.GetWindowText(hwnd)
            if current_title and (self._is_spotify_tab(current_title) if keyword == 'spotify' else keyword.lower() in current_title.lower()):
                rect = win32gui.GetWindowRect(hwnd)
                cx = rect[0] + (rect[2] - rect[0]) // 2
                cy = rect[1] + int((rect[3] - rect[1]) * 0.6)
                pyautogui.click(cx, cy)
                time.sleep(0.3)
                return True
        except Exception:
            pass

        # First try Ctrl+1 through Ctrl+8 for speed
        for n in range(1, 9):
            pyautogui.hotkey('ctrl', str(n))
            time.sleep(0.3)
            try:
                title = win32gui.GetWindowText(hwnd)
                if title and (self._is_spotify_tab(title) if keyword == 'spotify' else keyword.lower() in title.lower()):
                    rect = win32gui.GetWindowRect(hwnd)
                    cx = rect[0] + (rect[2] - rect[0]) // 2
                    cy = rect[1] + int((rect[3] - rect[1]) * 0.6)
                    pyautogui.click(cx, cy)
                    time.sleep(0.3)
                    return True
            except Exception:
                pass

        # Fallback: Ctrl+Tab to cycle through everything else
        for _ in range(20):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.3)
            try:
                title = win32gui.GetWindowText(hwnd)
                if title and (self._is_spotify_tab(title) if keyword == 'spotify' else keyword.lower() in title.lower()):
                    rect = win32gui.GetWindowRect(hwnd)
                    cx = rect[0] + (rect[2] - rect[0]) // 2
                    cy = rect[1] + int((rect[3] - rect[1]) * 0.6)
                    pyautogui.click(cx, cy)
                    time.sleep(0.3)
                    return True
            except Exception:
                pass

        print(f"[Jarvis] Tab not found: {keyword}")
        return False
    
    def _get_chrome_hwnd(self):
        import win32gui
        results = []
        def callback(hwnd, data):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                if 'google chrome' in title or title.endswith('- google chrome'):
                    data.append(hwnd)
        win32gui.EnumWindows(callback, results)
        return results[0] if results else None

    def _control_spotify_tab(self, action):
        import pyautogui, time, win32gui, win32con, win32com.client

        hwnd = self._get_chrome_hwnd()
        if not hwnd:
            print("[Jarvis] Chrome not found")
            return False

        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
        except Exception:
            pass

        found = False
        # Check current tab first!
        try:
            current_title = win32gui.GetWindowText(hwnd)
            if self._is_spotify_tab(current_title):
                found = True
        except Exception:
            pass

        if not found:
            # First try Ctrl+1 through Ctrl+8 for speed
            for n in range(1, 9):
                pyautogui.hotkey('ctrl', str(n))
                time.sleep(0.3)
                title = win32gui.GetWindowText(hwnd)
                if self._is_spotify_tab(title):
                    found = True
                    break

        if not found:
            # Fallback: Ctrl+Tab to cycle through all tabs
            for _ in range(20):
                pyautogui.hotkey('ctrl', 'tab')
                time.sleep(0.3)
                title = win32gui.GetWindowText(hwnd)
                if self._is_spotify_tab(title):
                    found = True
                    break

        if not found:
            return False

        rect = win32gui.GetWindowRect(hwnd)
        cx = rect[0] + (rect[2] - rect[0]) // 2
        cy = rect[1] + int((rect[3] - rect[1]) * 0.6)
        pyautogui.click(cx, cy)
        time.sleep(0.4)

        if action in ('pause', 'play'):
            pyautogui.press('space')
        elif action == 'next':
            pyautogui.hotkey('ctrl', 'right')
        elif action == 'previous':
            pyautogui.hotkey('ctrl', 'left')
        else:
            return False

        time.sleep(0.2)
        print(f"[Jarvis] Spotify {action} ✓")
        return True

    def _control_youtube_tab(self, action):
        import pyautogui, time, win32gui, win32con, win32com.client

        hwnd = self._get_chrome_hwnd()
        if not hwnd:
            print("[Jarvis] Chrome not found")
            return False

        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
        except Exception:
            pass

        found = False
        # Check current tab first!
        try:
            current_title = win32gui.GetWindowText(hwnd).lower()
            if 'youtube' in current_title:
                found = True
        except Exception:
            pass

        if not found:
            # First try Ctrl+1 through Ctrl+8 for speed
            for n in range(1, 9):
                pyautogui.hotkey('ctrl', str(n))
                time.sleep(0.3)
                title = win32gui.GetWindowText(hwnd).lower()
                if 'youtube' in title:
                    found = True
                    break

        if not found:
            # Fallback: Ctrl+Tab to cycle through all tabs
            for _ in range(20):
                pyautogui.hotkey('ctrl', 'tab')
                time.sleep(0.3)
                title = win32gui.GetWindowText(hwnd).lower()
                if 'youtube' in title:
                    found = True
                    break

        if not found:
            return False

        rect = win32gui.GetWindowRect(hwnd)
        cx = rect[0] + (rect[2] - rect[0]) // 2
        cy = rect[1] + int((rect[3] - rect[1]) * 0.6)
        pyautogui.click(cx, cy)
        time.sleep(0.4)

        if action in ('pause', 'play'):
            pyautogui.press('space')
        elif action == 'next':
            pyautogui.hotkey('shift', 'n')
        elif action == 'previous':
            pyautogui.hotkey('shift', 'p')
        else:
            return False

        time.sleep(0.2)
        print(f"[Jarvis] YouTube {action} ✓")
        return True

    def handle_set_command(self, args):
        if not args:
            print("Unknown set command")
            return
        
        if args.lower().startswith("volume"):
            vol_part = args[6:].strip()
            if vol_part.startswith("to "):
                vol_part = vol_part[3:].strip()
            
            if not vol_part:
                vol = self.media_manager.get_system_volume()
                print(f"[Jarvis] Current volume: {vol}%")
                return
            
            try:
                level = int(vol_part)
                self.media_manager.set_volume(level)
            except ValueError:
                print("[Jarvis] Usage: set volume <0-100>")
        else:
            print(f"Unknown set command: {args}")

    def _play_song_on_spotify(self, song: str):
        """
        Play song using spotify.com in Chrome.
        User is already signed in to spotify.com.
        Flow: Open spotify.com/search/song/tracks → click first result → play
        """
        import urllib.parse
        CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(CHROME_EXE):
            CHROME_EXE = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        encoded_song = urllib.parse.quote(song)
        spotify_search_url = f"https://open.spotify.com/search/{encoded_song}/tracks"

        subprocess.Popen([CHROME_EXE, '--new-tab', spotify_search_url])
        print(f"[Jarvis] Spotify pe '{song}' search kar raha hoon...")
        time.sleep(4.5)

        sp_win = None
        for attempt in range(12):
            wins = [w for w in gw.getAllWindows()
                    if 'spotify' in w.title.lower()
                    and w.visible]
            if wins:
                sp_win = wins[0]
                break
            time.sleep(0.5)

        if not sp_win:
            for attempt in range(5):
                wins = [w for w in gw.getAllWindows()
                        if ('chrome' in w.title.lower()
                            or 'google chrome' in w.title.lower())
                        and 'edge' not in w.title.lower()
                        and w.visible]
                if wins:
                    sp_win = wins[0]
                    break
                time.sleep(0.5)

        if not sp_win:
            print("[Jarvis] Chrome window nahi mila.")
            return

        hwnd = sp_win._hWnd
        orig_rect = win32gui.GetWindowRect(hwnd)
        was_maximized = (win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMAXIMIZED)

        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            time.sleep(0.15)
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1.5)
        except:
            pass

        rect = win32gui.GetWindowRect(hwnd)
        win_x = rect[0]
        win_y = rect[1]
        win_w = rect[2] - rect[0]
        win_h = rect[3] - rect[1]

        first_track_x = win_x + int(win_w * 0.35)
        first_track_y = win_y + int(win_h * 0.35)

        pyautogui.moveTo(first_track_x, first_track_y, duration=0.4)
        time.sleep(0.8)

        pyautogui.doubleClick(first_track_x, first_track_y)
        time.sleep(0.3)

        pyautogui.moveTo(first_track_x, first_track_y + 10, duration=0.2)
        time.sleep(0.3)
        pyautogui.doubleClick(first_track_x, first_track_y + 10)

        print(f"[Jarvis] '{song}' play ho raha hai Spotify pe!")

        if not was_maximized:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                left, top, right, bottom = orig_rect
                win32gui.MoveWindow(hwnd, left, top, right-left, bottom-top, True)
            except:
                pass

    def parse_and_run(self, command_str):
        cmd, arg = self.parse_command(command_str)
        if cmd:
            self.handle_command(cmd, arg)

    def preprocess_youtube_compound(self, text: str) -> str:
        """Detect YouTube commands and rewrite to search_youtube format."""
        t = text.lower().strip()

        ordinal_map = {
            'first': '1', '1st': '1', 'pehla': '1', 'pehli': '1',
            'second': '2', '2nd': '2', 'doosra': '2', 'doosri': '2',
            'third': '3', '3rd': '3', 'teesra': '3', 'teesri': '3',
            'fourth': '4', '4th': '4', 'chautha': '4',
            'fifth': '5', '5th': '5', 'paanchwa': '5',
            'sixth': '6', '6th': '6', 'seventh': '7', '7th': '7',
            'eighth': '8', '8th': '8', 'ninth': '9', '9th': '9',
            'tenth': '10', '10th': '10',
        }

        # Pattern 1: "search X on youtube and play Nth video"
        play_nth = re.search(
            r'^search\s+(.+?)\s+on\s+(?:youtube|yt)\s+'
            r'(?:and\s+)?play\s+(?:the\s+)?(\w+)\s*(?:video)?$',
            t, re.IGNORECASE
        )
        if play_nth:
            query = play_nth.group(1).strip()
            pick_raw = play_nth.group(2).strip().lower()
            pick_num = ordinal_map.get(pick_raw, pick_raw)
            if pick_num.isdigit():
                self._yt_auto_pick = pick_num
                return f"search_youtube {query}"

        # Pattern 2: "search X on youtube" plain — no autoplay
        plain_search = re.search(
            r'^search\s+(.+?)\s+on\s+(?:youtube|yt)$',
            t, re.IGNORECASE
        )
        if plain_search:
            query = plain_search.group(1).strip()
            return f"search_youtube {query}"

        # Pattern 3: "search X on youtube then play N"
        then_play = re.search(
            r'^search\s+(.+?)\s+on\s+(?:youtube|yt)\s+then\s+play\s+(\w+)$',
            t, re.IGNORECASE
        )
        if then_play:
            query = then_play.group(1).strip()
            pick_raw = then_play.group(2).strip().lower()
            pick_num = ordinal_map.get(pick_raw, pick_raw)
            if pick_num.isdigit():
                self._yt_auto_pick = pick_num
            else:
                self._yt_auto_play = True
            return f"search_youtube {query}"

        # Pattern 4: "search X on youtube and play first" → autoplay
        autoplay_first = re.search(
            r'^search\s+(.+?)\s+on\s+(?:youtube|yt)\s+'
            r'(?:and\s+)?(?:play\s+)?(?:first|pehla|pehli|1st)(?:\s+video)?$',
            t, re.IGNORECASE
        )
        if autoplay_first:
            query = autoplay_first.group(1).strip()
            self._yt_auto_play = True
            return f"search_youtube {query}"

        # Pattern 5: "youtube pe X search karo"
        yt_pe = re.search(
            r'(?:youtube\s+pe|yt\s+pe)\s+(.+?)\s+'
            r'(?:search\s+karo|dhundo|search\s+kar)',
            t, re.IGNORECASE
        )
        if yt_pe:
            query = yt_pe.group(1).strip()
            return f"search_youtube {query}"

        return text

    def run(self):
        self.print_banner()
        
        while self.running:
            try:
                user_input = input("\033[92mjarvis>\033[0m ").strip()
                user_input = re.sub(r'^\d+[\.\)]\s*', '', user_input)
                if not user_input:
                    continue
                
                if self._processing_input:
                    self.parse_and_run(user_input)
                    continue
                
                self._processing_input = True
                
                # Clear chain apps from previous command
                self._chain_opened_apps.clear()
                
                user_input = user_input.rstrip('\\').strip()
                
                # In run(), add this BEFORE chain splitting:
                user_input = self.preprocess_youtube_compound(user_input)
                
                # BUG 6+7 fix: memory clear/limit should NOT be chained - execute alone
                lowered = user_input.lower().strip()
                if lowered.startswith('memory clear') or lowered.startswith('memory limit'):
                    actual_cmd = user_input
                    self.parse_and_run(actual_cmd)
                    self.memory.add_command(user_input)
                    self._processing_input = False
                    continue
                
                # Add direct parse for delete file pattern - skip brain entirely
                delete_match = re.match(
                    r'^delete\s+(?:file\s+)?(\S+\.\w+)$', 
                    user_input.strip(), re.IGNORECASE)
                if delete_match:
                    filename = delete_match.group(1)
                    self.file_manager.show_in_explorer(filename)
                    self.memory.add_command(user_input)
                    self._processing_input = False
                    continue
                
                flattened = split_into_parts(user_input)

                typo_separators = [' the ', ' an ']
                for segment in list(flattened):
                    for typo in typo_separators:
                        if typo in f' {segment.lower()} ':
                            parts = re.split(typo, segment, flags=re.IGNORECASE)
                            verbs = ["open", "close", "minimize", "maximize",
                                    "restore", "focus", "play", "pause", "search",
                                    "set", "mute", "unmute", "volume"]
                            if (len(parts) == 2 and
                                any(parts[1].strip().lower().startswith(v)
                                    for v in verbs)):
                                flattened.remove(segment)
                                flattened.extend([p.strip() for p in parts if p.strip()])
                                break

                processed_parts = []
                for part in flattened:
                    part = part.strip()
                    if not part:
                        continue
                    
                    # BUG 3 fix: URL detection in chain - add "open " prefix if URL without verb
                    url_patterns = [".com", ".org", ".net", ".io", ".dev", ".app", ".co"]
                    is_url = any(ext in part.lower() for ext in url_patterns)
                    has_verb = any(part.lower().startswith(v) for v in ['open ', 'close ', 'play ', 'search ', 'minimize ', 'maximize '])
                    if is_url and not has_verb:
                        part = "open " + part
                    
                    # Fast command check FIRST — before any translation
                    # This prevents hinglish_to_english from corrupting
                    # search_youtube/play_song commands
                    if is_fast_command(part):
                        processed_parts.append(part)
                        continue
                    
                    if part.lower().startswith('memory'):
                        processed_parts.append("__brain_processed__" + part)
                        continue
                    
                    translated = hinglish_to_english(part)
                    
                    fast_volume_commands = [
                        'increase volume', 'decrease volume', 'mute', 'unmute',
                        'volume up', 'volume down', 'close',
                    ]
                    ACTION_VERBS = ['open ', 'close ', 'minimize ', 'maximize ',
                                    'restore ', 'focus ']
                    if translated != part and (
                        translated.lower() in fast_volume_commands or
                        translated.lower().startswith('set volume') or
                        any(translated.lower().startswith(v) for v in ACTION_VERBS)
                    ):
                        processed_parts.append(translated)
                        continue
                    
                    if part.lower().startswith('memory'):
                        processed_parts.append("__brain_processed__" + part)
                        continue
                    
                    if is_fast_command(part):
                        processed_parts.append(part)
                        continue
                    
                    self._brain_call_count += 1
                    if self._brain_call_count > 1:
                        # This is a duplicate — skip brain, use input as raw command
                        processed_parts.append(part)
                        continue

                    try:
                        brain_result = think(part)
                    except Exception as e:
                        print(f"[Jarvis] Brain error: {e}")
                        processed_parts.append(part)
                        continue
                    
                    if brain_result.get("type") == "conversation":
                        reply = brain_result.get('reply', '').strip()
                        provider = brain_result.get('provider', 'Unknown')
                        source = brain_result.get('source', 'conversation')
                        if reply:
                            if source == 'web_search':
                                print(f"[{provider} via Web Search] {reply}")
                            else:
                                print(f"[{provider}] {reply}")
                        else:
                            # Retry with next provider if empty reply
                            print(f"[Jarvis] Ek second...")
                            from brain import call_openrouter_conversation
                            try:
                                retry = call_openrouter_conversation(user_input)
                                print(f"[Jarvis] {retry.get('reply', 'Kuch hua. Dobara try karo.')}")
                            except:
                                print(f"[Jarvis] Hmm, try again!")
                        continue
                    
                    action = brain_result.get("action", "raw")
                    target = brain_result.get("target", "") or ""
                    app    = brain_result.get("app", "") or ""
                    extra  = brain_result.get("extra", {}) or {}
                    arg    = brain_result.get("arg", "") or ""
                    song   = extra.get("text","") or extra.get("query","") or arg or ""
                    
                    if action == "raw":
                        cmd_string = part
                    
                    elif action == "open":
                        cmd_string = f"open {target}" if target else f"open {app}"
                    
                    elif action == "close":
                        cmd_string = f"close {target}" if target else f"close {app}"
                    
                    elif action in ("minimize","maximize","restore","focus"):
                        t = target or app
                        cmd_string = f"{action} {t}" if t else action
                    
                    elif action == "play":
                        if song and app in ("spotify","music",""):
                            cmd_string = f"play_song {song} on spotify" if song else "play"
                        elif song and app in ("youtube","chrome","browser"):
                            cmd_string = f"search_youtube {song}"
                        elif app:
                            cmd_string = f"play on {app}"
                        else:
                            cmd_string = "play"
                    
                    elif action == "pause":
                        cmd_string = f"pause on {app}" if app else "pause"
                    
                    elif action == "next":
                        cmd_string = f"next on {app}" if app else "next"
                    
                    elif action == "previous":
                        cmd_string = f"previous on {app}" if app else "previous"
                    
                    elif action == "play_song":
                        cmd_string = f"play_song {song or target} on {app or 'spotify'}"
                    
                    elif action == "search_youtube":
                        cmd_string = f"search_youtube {song or target}"
                    
                    elif action == "whatsapp_message":
                        text = extra.get("text", arg) or ""
                        cmd_string = f"whatsapp_message {target} {text}"
                    
                    elif action == "type_text":
                        text = extra.get("text", arg) or ""
                        cmd_string = f"type_text {text} in {target}"
                    
                    elif action in ("increase volume","decrease volume","mute","unmute"):
                        cmd_string = action
                    
                    elif action == "set_volume":
                        level = extra.get("level", target) or target
                        cmd_string = f"set volume {level}"
                    
                    else:
                        cmd_string = f"{action} {target}".strip()
                    
                    if cmd_string and len(cmd_string.split()) >= 2:
                        processed_parts.append("__brain_processed__" + cmd_string)
                    elif cmd_string in SINGLE_WORD_COMMANDS:
                        processed_parts.append("__brain_processed__" + cmd_string)
                
                valid_parts = [p for p in processed_parts if p is not None and p != '__brain_processed__']
                if len(valid_parts) > 1:
                    executed = 0
                    for cmd_str in processed_parts:
                        if cmd_str is None or cmd_str == '__brain_processed__':
                            continue
                        try:
                            actual_cmd = cmd_str.replace("__brain_processed__", "")
                            self.parse_and_run(actual_cmd)
                            self.memory.add_command(actual_cmd)
                            executed += 1
                            if executed < len(valid_parts):
                                time.sleep(1.0)
                        except Exception as e:
                            print(f"[Jarvis] Command failed: ({actual_cmd})")
                    print("[Jarvis] All done.")
                    # Focus terminal back after running chain commands
                    self.window_manager.focus_terminal()
                    time.sleep(0.2)
                else:
                    for cmd_str in processed_parts:
                        if cmd_str is not None and cmd_str != '__brain_processed__':
                            actual_cmd = cmd_str.replace("__brain_processed__", "")
                            self.parse_and_run(actual_cmd)
                            self.memory.add_command(actual_cmd)
                    
                    # Focus terminal back after command execution
                    self.window_manager.focus_terminal()
                    time.sleep(0.2)
                
                # Reset after processing all parts:
                self._brain_call_count = 0
                self._processing_input = False
                            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")
                self._processing_input = False
                self._brain_call_count = 0


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
