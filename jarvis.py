import os
import subprocess
import sys
import time
import re
from pathlib import Path

NIRCMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nircmd.exe')
NIRCMD_AVAILABLE = os.path.isfile(NIRCMD)

if not NIRCMD_AVAILABLE:
    print("[Jarvis] WARNING: nircmd.exe not found in JARVIS folder. Volume control is disabled.")


def install_packages(packages):
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])


install_packages(["pyautogui", "pygetwindow", "pywin32", "rapidfuzz", "psutil", "winrt-runtime", "winrt-Windows.Media.Control", "winrt-Windows.Foundation", "winrt-Windows.Foundation.Collections", "python-dotenv", "requests", "yt-dlp", "ddgs"])


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

    # ── STEP 1: Extract target from ORIGINAL text FIRST (before any stripping) ──
    known_targets = [
        'spotify', 'chrome', 'youtube', 'whatsapp', 'notepad',
        'vlc', 'settings', 'calculator', 'camera', 'edge',
        'word', 'excel', 'powerpoint', 'teams', 'discord',
        'telegram', 'instagram', 'twitter', 'photos', 'paint',
        'file explorer', 'explorer', 'task manager', 'antigravity',
        'claude', 'music', 'video', 'song', 'gaana', 'gana',
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
    "play on ", "pause on ", "next on ", "previous on "
]

SINGLE_WORD_COMMANDS = ['play', 'pause', 'next', 'previous', 
                        'mute', 'unmute', 'exit', 'list']


def is_fast_command(text):
    t = text.lower().strip()
    if t in FAST_COMMANDS:
        return True
    return any(t.startswith(v) for v in FAST_VERBS)


def split_into_parts(user_input):
    parts = user_input.split("then")
    flattened = []
    for segment in parts:
        subparts = [p.strip() for p in segment.split("and")]
        for p in subparts:
            if p:
                flattened.append(p)
    return flattened


class DependencyManager:
    @staticmethod
    def check():
        pass


class FileManager:
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
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            subprocess.Popen([chrome_path, url_str])
            print(f"[Jarvis] Launched Chrome with: {url_str}")
            return True
        except Exception as e:
            print(f"[Jarvis] Failed to open URL: {e}")
            return False
    
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

    def search_youtube(self, query: str, auto_play_first: bool = False):
        import yt_dlp
        
        if not query:
            print("[Jarvis] Kya search karna hai YouTube pe?")
            return False
        
        print(f"[Jarvis] YouTube pe '{query}' search kar raha hoon...")
        
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': False
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                r = ydl.extract_info(
                    f'ytsearch10:{query}', download=False)
                videos = r.get('entries', [])
        except Exception as e:
            print(f"[Jarvis] YouTube search failed: {e}")
            return False
        
        if not videos:
            print(f"[Jarvis] '{query}' ke liye koi result nahi mila.")
            return False
        
        if auto_play_first:
            video = videos[0]
            url = f"https://www.youtube.com/watch?v={video['id']}"
            title = video.get('title') or video.get('fulltitle') or 'Unknown'
            channel = video.get('channel') or video.get('uploader') or ''
            print(f"[Jarvis] Playing: {title} - {channel}")
            self.open_url(url)
            return True
        
        print(f"\n[Jarvis] '{query}' ke results:\n")
        for i, v in enumerate(videos, 1):
            title = v.get('title') or v.get('fulltitle') or 'Unknown Title'
            channel = (v.get('channel') or 
                       v.get('uploader') or 
                       v.get('channel_id') or 
                       'Unknown Channel')
            duration = v.get('duration') or v.get('duration_string') or 0
            if isinstance(duration, str):
                dur_str = duration
            elif duration:
                mins = int(duration // 60)
                secs = int(duration % 60)
                dur_str = f"{mins}:{secs:02d}"
            else:
                dur_str = "?"
            print(f"  {i:2}. {title}")
            print(f"      Channel: {channel} | Duration: {dur_str}")
        
        print("\n  0. Cancel")
        
        try:
            choice = input("\nKaunsa video play karein (0-10): ").strip()
            
            valid_aliases = {
                'first': '1', 'pehla': '1', 'pehli': '1', '1st': '1',
                'second': '2', 'doosra': '2', 'doosri': '2', '2nd': '2',
                'third': '3', 'teesra': '3', 'teesri': '3', '3rd': '3',
            }
            
            if choice in valid_aliases:
                choice = valid_aliases[choice]
            
            if not choice.isdigit():
                print("[Jarvis] Valid number daalo (0 se cancel). Input ignore kiya.")
                choice = input("Number daalo (0 to cancel): ").strip()
                if not choice.isdigit():
                    print("[Jarvis] Cancel kar diya.")
                    return False
            
            if choice == '0':
                print("[Jarvis] Cancel kiya.")
                return False
            
            idx = int(choice) - 1
            if idx < 0 or idx >= len(videos):
                print(f"[Jarvis] 1 se {len(videos)} ke beech number daalo.")
                return False
            
            video = videos[idx]
            url = f"https://www.youtube.com/watch?v={video['id']}"
            title = video.get('title', 'Unknown')
            channel = video.get('channel', video.get('uploader', ''))
            
            print(f"[Jarvis] Playing: {title} by {channel}")
            self.open_url(url)
            return True
            
        except Exception as e:
            print(f"[Jarvis] Error: {e}")
            return False


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

    def _read_system_volume(self):
        if not NIRCMD_AVAILABLE:
            return 50
        try:
            result = subprocess.run([NIRCMD, 'getvolume', '0'], capture_output=True, text=True)
            output = result.stdout.strip()
            parts = output.split()
            if len(parts) >= 1:
                vol_value = int(parts[0], 16)
                return int(vol_value / 655.35)
        except:
            pass
        return self._current_volume

    def get_system_volume(self):
        return self._read_system_volume()

    def set_volume(self, level):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return self._current_volume
        level = max(0, min(100, level))
        nircmd_value = int(65535 * level / 100)
        subprocess.run([NIRCMD, 'setsysvolume', str(nircmd_value)], capture_output=True)
        time.sleep(0.1)
        self._current_volume = level
        if self._is_muted:
            subprocess.run([NIRCMD, 'mutesysvolume', '0'], capture_output=True)
            time.sleep(0.1)
            subprocess.run([NIRCMD, 'setsysvolume', str(nircmd_value)], capture_output=True)
            self._is_muted = False
        self._print(f"[Jarvis] Volume set to {self._current_volume}%", f"[Jarvis] Awaaz {self._current_volume}% ho gayi ✓")
        return self._current_volume

    def volume_up(self):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return
        current = self._read_system_volume()
        new_vol = min(100, current + 10)
        self.set_volume(new_vol)
        self._print(f"[Jarvis] Volume up: {self._current_volume}%", f"[Jarvis] Awaaz {self._current_volume}% ho gayi ✓")

    def volume_down(self):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return
        current = self._read_system_volume()
        new_vol = max(0, current - 10)
        self.set_volume(new_vol)
        self._print(f"[Jarvis] Volume down: {self._current_volume}%", f"[Jarvis] Awaaz {self._current_volume}% ho gayi ✓")

    def mute_volume(self):
        if not NIRCMD_AVAILABLE:
            self._print("[Jarvis] Volume control unavailable - nircmd.exe not found")
            return False
        if self._is_muted:
            self._print("[Jarvis] Already muted", "[Jarvis] Pehle se hi mute hai")
            return True
        subprocess.run([NIRCMD, 'mutesysvolume', '1'], capture_output=True)
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
        subprocess.run([NIRCMD, 'mutesysvolume', '0'], capture_output=True)
        time.sleep(0.15)
        nircmd_value = int(65535 * self._current_volume / 100)
        subprocess.run([NIRCMD, 'setsysvolume', str(nircmd_value)], capture_output=True)
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


def _youtube_keyboard_next():
    """Press Shift+N on YouTube tab — skips to next video."""
    import pygetwindow as gw
    import win32gui, win32con
    import win32com.client
    import pyautogui, time

    wins = [w for w in gw.getAllWindows()
            if 'youtube' in w.title.lower()
            and ('chrome' in w.title.lower() or 'google' in w.title.lower())
            and w.visible]

    if not wins:
        wins = [w for w in gw.getAllWindows()
                if ('chrome' in w.title.lower() or 'google' in w.title.lower())
                and w.visible]

    if not wins:
        print("[Jarvis] YouTube Chrome window not found")
        return

    win = wins[0]
    hwnd = win._hWnd

    orig_rect = win32gui.GetWindowRect(hwnd)
    was_maximized = win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMAXIMIZED

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        time.sleep(0.1)
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.8)
    except Exception:
        pass

    rect = win32gui.GetWindowRect(hwnd)
    cx = rect[0] + int((rect[2] - rect[0]) * 0.50)
    cy = rect[1] + int((rect[3] - rect[1]) * 0.45)

    pyautogui.moveTo(cx, cy, duration=0.15)
    time.sleep(0.1)
    pyautogui.click(cx, cy)
    time.sleep(0.4)

    pyautogui.hotkey('shift', 'n')
    time.sleep(0.2)

    if not was_maximized:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            left, top, right, bottom = orig_rect
            win32gui.MoveWindow(hwnd, left, top,
                                right - left, bottom - top, True)
        except Exception:
            pass


def _youtube_keyboard_previous():
    """Press Shift+P on YouTube tab — goes to previous video."""
    import pygetwindow as gw
    import win32gui, win32con
    import win32com.client
    import pyautogui, time

    wins = [w for w in gw.getAllWindows()
            if 'youtube' in w.title.lower()
            and ('chrome' in w.title.lower() or 'google' in w.title.lower())
            and w.visible]

    if not wins:
        wins = [w for w in gw.getAllWindows()
                if ('chrome' in w.title.lower() or 'google' in w.title.lower())
                and w.visible]

    if not wins:
        print("[Jarvis] YouTube Chrome window not found")
        return

    win = wins[0]
    hwnd = win._hWnd

    orig_rect = win32gui.GetWindowRect(hwnd)
    was_maximized = win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMAXIMIZED

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        time.sleep(0.1)
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.8)
    except Exception:
        pass

    rect = win32gui.GetWindowRect(hwnd)
    cx = rect[0] + int((rect[2] - rect[0]) * 0.50)
    cy = rect[1] + int((rect[3] - rect[1]) * 0.45)

    pyautogui.moveTo(cx, cy, duration=0.15)
    time.sleep(0.1)
    pyautogui.click(cx, cy)
    time.sleep(0.4)

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


async def media_action_async(action, app_hint=None):
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
            if is_chrome:
                _youtube_keyboard_next()
            else:
                await session.try_skip_next_async()
            print(f"[Jarvis] Next: {display}")

        elif action in ("prev", "previous"):
            if is_chrome:
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


def handle_media(action, app_hint=None):
    return run_async(media_action_async(action, app_hint))


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
    EXCLUDED_TITLES = ['jarvis.py', 'antigravity', 'opencode', 'terminal', 'powershell', 'cmd', 'python', 'code']

    def get_windows(self):
        try:
            windows = gw.getAllWindows()
            return [{"title": w.title, "hwnd": w._hWnd, "window": w} for w in windows if w.title.strip()]
        except Exception as e:
            print(f"Error getting windows: {e}")
            return []

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
        
        for win in candidates:
            proc_name = self._get_process_name(win["hwnd"])
            if proc_name and query_lower in proc_name:
                return win
        
        for win in candidates:
            if query_lower in win["title"].lower():
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

    def close_window(self, query):
        win = self.find_window(query)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        try:
            win["window"].close()
            time.sleep(0.3)
            print(f"[Jarvis] Closed: {title}")
            return True
        except:
            pass
        
        try:
            proc = self._get_process_info(win["hwnd"])
            if proc:
                proc.kill()
                print(f"[Jarvis] Closed: {title}")
                return True
        except:
            pass
        
        return False

    def minimize_window(self, query):
        win = self.find_window(query)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        try:
            win["window"].minimize()
            print(f"[Jarvis] Minimized: {title}")
            return True
        except Exception as e:
            print(f"Failed to minimize: {e}")
            return False

    def maximize_window(self, query):
        win = self.find_window(query)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        try:
            win["window"].maximize()
            print(f"[Jarvis] Maximized: {title}")
            return True
        except Exception as e:
            print(f"Failed to maximize: {e}")
            return False

    def restore_window(self, query):
        win = self.find_window(query)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        try:
            win["window"].restore()
            print(f"[Jarvis] Restored: {title}")
            return True
        except Exception as e:
            print(f"Failed to restore: {e}")
            return False

    def focus_window(self, query):
        win = self.find_window(query)
        if not win:
            print(f"Window not found: {query}")
            return False
        
        title = win["title"]
        hwnd = win["hwnd"]
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys("")
            print(f"[Jarvis] Focused: {title}")
            return True
        except Exception as e:
            print(f"Focus failed: {e}")
            return False


class Jarvis:
    def __init__(self):
        self.app_manager = AppManager()
        self.window_manager = WindowManager()
        self.file_manager = FileManager()
        self.browser_manager = BrowserManager()
        self.media_manager = MediaManager()
        self.running = True
        self.last_was_hinglish = False

    def _hinglish_print(self, english_msg, hinglish_msg):
        if self.last_was_hinglish and hinglish_msg:
            print(hinglish_msg)
        else:
            print(english_msg)

    def print_banner(self):
        banner = """
\033[96m     ██████╗ ██╗      ██████╗  ██████╗ ███████╗\033[0m
\033[96m    ██╔════╝ ██║     ██╔═══██╗██╔════╝ ██╔════╝\033[0m
\033[96m    ███████╗ ██║     ██║   ██║██║  ███╗███████╗\033[0m
\033[96m    ╚════██║ ██║     ██║   ██║██║   ██║╚════██║\033[0m
\033[96m    ███████║ ███████╗╚██████╔╝╚██████╔╝███████║\033[0m
\033[96m    ╚══════╝ ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝\033[0m
\033[93m              Your Terminal Assistant\033[0m
        """
        print(banner)
        print("\033[95mCommands: open, close, minimize, maximize, restore, focus, list, exit\033[0m\n")

    def parse_command(self, line):
        parts = line.strip().split(maxsplit=1)
        if not parts:
            return None, None
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        return cmd, arg

    def handle_command(self, cmd, arg):
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
            # App check third
            else:
                result = self.app_manager.open_app(arg)
                if result is False:
                    print("[Jarvis] Tip: If this is a file, try: open filename.ext")
                
        elif cmd == "close":
            if not arg:
                print("Usage: close <window title or URL>")
            elif self.browser_manager.is_url(arg):
                self.browser_manager.close_tab(arg)
            else:
                self.window_manager.close_window(arg)
                
        elif cmd == "minimize":
            if not arg:
                print("Usage: minimize <window title>")
            else:
                self.window_manager.minimize_window(arg)
                
        elif cmd == "maximize":
            if not arg:
                print("Usage: maximize <window title>")
            else:
                self.window_manager.maximize_window(arg)
                
        elif cmd == "restore":
            if not arg:
                print("Usage: restore <window title>")
            else:
                self.window_manager.restore_window(arg)
                
        elif cmd == "focus":
            if not arg:
                print("Usage: focus <window title>")
            else:
                self.window_manager.focus_window(arg)
                
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
            print(f"[Jarvis] Song search coming soon: {arg}")
            
        elif cmd == "search_youtube":
            if not arg:
                print("[Jarvis] Kya search karna hai YouTube pe?")
            else:
                query = arg.replace(" on youtube", "").replace(
                        "youtube pe ", "").replace(
                        " on yt", "").replace(
                        "yt pe ", "").strip()
                auto_first = any(word in query.lower() 
                               for word in ['first wali', 'pehli wali', 
                                           'pehla wala', 'top wali',
                                           'first one', 'auto'])
                if auto_first:
                    for word in ['first wali', 'pehli wali', 
                               'pehla wala', 'top wali', 
                               'first one', 'auto']:
                        query = query.replace(word, '').strip()
                self.browser_manager.search_youtube(query, auto_first)

        elif cmd == "web_search" or cmd == "websearch":
            if not arg:
                print("[Jarvis] Kya search karna hai?")
            else:
                print(f"[Jarvis] Web pe '{arg}' search kar raha hoon...")
                results = web_search(arg)
                print(results[:500])
            
        elif cmd == "whatsapp_message":
            print(f"[Jarvis] WhatsApp message coming soon: {arg}")
            
        elif cmd == "type_text":
            print(f"[Jarvis] Type text coming soon: {arg}")
            
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
        
        if args and " on " in args.lower():
            parts = args.lower().split(" on ")
            if parts[0].strip() in ("play", "pause", "next", "previous", "prev", "skip", "resume"):
                action = parts[0].strip()
            app_hint = parts[1].strip()
        elif args:
            words = args.lower().split()
            possible_actions = ["play", "pause", "next", "previous", "prev", "skip", "resume"]
            for i, word in enumerate(words):
                if word in possible_actions:
                    app_hint = " ".join(words[:i]) if i > 0 else None
                    action = word
                    break
            if app_hint is None and action == verb:
                app_hint = args.lower().strip()
        
        if action in ("play", "pause", "next", "previous", "prev", "skip", "resume"):
            if action == "resume":
                action = "play"
            handle_media(action, app_hint)

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

    def parse_and_run(self, command_str):
        cmd, arg = self.parse_command(command_str)
        if cmd:
            self.handle_command(cmd, arg)

    def run(self):
        self.print_banner()
        
        while self.running:
            try:
                user_input = input("\033[92mjarvis>\033[0m ").strip()
                if not user_input:
                    continue
                
                user_input = user_input.rstrip('\\').strip()
                
                flattened = split_into_parts(user_input)
                
                processed_parts = []
                for part in flattened:
                    part = part.strip()
                    if not part:
                        continue
                    
                    if is_fast_command(part):
                        processed_parts.append(part)
                        continue
                    
                    try:
                        brain_result = think(part)
                    except Exception as e:
                        print(f"[Jarvis] Brain error: {e}")
                        processed_parts.append(part)
                        continue
                    
                    if brain_result["type"] == "conversation":
                        print(f"[Jarvis] {brain_result.get('reply', '')}")
                        processed_parts.append(None)
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
                            executed += 1
                            if executed < len(valid_parts):
                                time.sleep(0.5)
                        except Exception as e:
                            print(f"[Jarvis] Command failed: ({actual_cmd})")
                    print("[Jarvis] All done.")
                else:
                    for cmd_str in processed_parts:
                        if cmd_str is not None and cmd_str != '__brain_processed__':
                            actual_cmd = cmd_str.replace("__brain_processed__", "")
                            self.parse_and_run(actual_cmd)
                            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
