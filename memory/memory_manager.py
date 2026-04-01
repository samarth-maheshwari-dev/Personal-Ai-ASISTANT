import os
import json
import datetime
from pathlib import Path

MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(MEMORY_DIR, exist_ok=True)

SESSION_FILE = os.path.join(MEMORY_DIR, 'session.json')
DAILY_LOG_FILE = os.path.join(MEMORY_DIR, 'daily_log.json')
LONG_TERM_FILE = os.path.join(MEMORY_DIR, 'history.json')
LAST_APP_FILE = os.path.join(MEMORY_DIR, 'last_app.json')
APP_HISTORY_FILE = os.path.join(MEMORY_DIR, 'app_history.json')
CONFIG_FILE = os.path.join(MEMORY_DIR, 'config.json')


class MemoryManager:
    def __init__(self, storage_limit_mb=1024):
        self.storage_limit = storage_limit_mb * 1024 * 1024
        self._load_config()
        self._ensure_files()

    def _load_config(self):
        config = self._load_json(CONFIG_FILE, {})
        limit = config.get('storage_limit_mb', 1024)
        self.storage_limit = limit * 1024 * 1024

    def _ensure_files(self):
        files_to_create = {
            SESSION_FILE: [],
            DAILY_LOG_FILE: [],
            LONG_TERM_FILE: {},
            LAST_APP_FILE: {},
            CONFIG_FILE: {'storage_limit_mb': 1024}
        }
        for path, default_data in files_to_create.items():
            if not os.path.exists(path):
                self._save_json(path, default_data)

    def _load_json(self, path, default=None):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default if default is not None else (default if default is not None else {})

    def _save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_command(self, command):
        """Add command to session (last 10, auto-reset on new day)."""
        session = self._load_json(SESSION_FILE, [])
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Check if session is from today
        if session and session[0].get('date') != today:
            session = []  # Reset for new day
        
        now = datetime.datetime.now()
        entry = {
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'command': command
        }
        session.append(entry)
        
        # Keep only last 10
        if len(session) > 10:
            session = session[-10:]
        
        self._save_json(SESSION_FILE, session)

    def get_session_commands(self, n=10):
        """Get last n commands from session."""
        session = self._load_json(SESSION_FILE, [])
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if session and session[0].get('date') != today:
            return []
        return session[-n:] if session else []

    def get_last_app(self):
        """Get last opened/focused app."""
        last_app = self._load_json(LAST_APP_FILE, {})
        return last_app.get('app')

    def set_last_app(self, app_name):
        """Set last opened/focused app."""
        last_app = {'app': app_name, 'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        self._save_json(LAST_APP_FILE, last_app)
        # Also update app history for "close dono" feature
        self._add_to_app_history(app_name)
    
    def _add_to_app_history(self, app_name):
        """Track app in history (keeps last 5 apps for close dono feature)."""
        history = self._load_json(APP_HISTORY_FILE, [])
        # Remove if already exists (to move to front)
        history = [h for h in history if h.get('app', '').lower() != app_name.lower()]
        # Add to front
        history.insert(0, {
            'app': app_name,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        # Keep only last 5
        history = history[:5]
        self._save_json(APP_HISTORY_FILE, history)
    
    def get_app_history(self, n=2):
        """Get last n opened apps for 'close dono' feature."""
        history = self._load_json(APP_HISTORY_FILE, [])
        return [h['app'] for h in history[:n]] if history else []
    
    def get_prev_app(self):
        """Get the second-to-last opened app."""
        history = self.get_app_history(2)
        return history[1] if len(history) > 1 else None

    def get_memory_size(self):
        """Get total memory storage size in bytes."""
        total = 0
        for f in [SESSION_FILE, DAILY_LOG_FILE, LONG_TERM_FILE, LAST_APP_FILE, CONFIG_FILE]:
            if os.path.exists(f):
                total += os.path.getsize(f)
        return total

    def check_and_cleanup(self):
        """Check storage limit and offer cleanup."""
        current_size = self.get_memory_size()
        if current_size > self.storage_limit:
            size_mb = current_size / (1024*1024)
            limit_mb = self.storage_limit / (1024*1024)
            print(f"\n[Memory] Storage limit hit! ({size_mb:.1f}MB / {limit_mb:.0f}MB)")
            print("[Memory] Oldest 30 days ki entries delete karein? (haan/nahi)")
            confirm = input("Confirm: ").strip().lower()
            if confirm in ('haan', 'ha', 'yes', 'y', 'haa'):
                self._delete_oldest_days(30)
            else:
                print("[Memory] Delete cancel kiya. Agli baar phir poochunga.")

    def _delete_oldest_days(self, days):
        """Delete entries older than N days from daily log."""
        daily = self._load_json(DAILY_LOG_FILE, [])
        if not daily:
            print("[Memory] Daily log already empty.")
            return

        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_str = cutoff.strftime('%Y-%m-%d')

        before_count = len(daily)
        kept = [e for e in daily if e.get('date', '') > cutoff_str]
        deleted_count = before_count - len(kept)

        self._save_json(DAILY_LOG_FILE, kept)
        print(f"[Memory] {deleted_count} entries delete ho gayi (30+ days purani).")
        print(f"[Memory] {len(kept)} entries bachi hain.")

    def delete_with_confirmation(self, days=30):
        """Delete entries older than N days with confirmation."""
        daily = self._load_json(DAILY_LOG_FILE, [])

        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_str = cutoff.strftime('%Y-%m-%d')

        to_delete = [e for e in daily if e.get('date', '') <= cutoff_str]
        to_keep = [e for e in daily if e.get('date', '') > cutoff_str]

        if not to_delete:
            print(f"[Memory] {days} din se purani koi entry nahi hai.")
            return

        print(f"\n[Memory] {len(to_delete)} entries milti hain {days} din se purani.")
        oldest = to_delete[0].get('date', '')
        newest = to_delete[-1].get('date', '')
        print(f"[Memory] Date range: {oldest} -> {newest}")
        print("[Memory] Type 'HAAN' to confirm delete, anything else to cancel:")
        confirm = input(">>> ").strip().lower()

        if confirm in ('haan', 'ha', 'yes', 'y', 'haa'):
            self._save_json(DAILY_LOG_FILE, to_keep)
            print(f"[Memory] {len(to_delete)} entries delete ho gayi.")
            print(f"[Memory] {len(to_keep)} entries bachi hain.")
        else:
            print("[Memory] Delete cancel kiya.")

    def get_today_activity(self):
        """Get today's activities from daily log."""
        daily = self._load_json(DAILY_LOG_FILE, [])
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return [e for e in daily if e.get('date', '').startswith(today)]

    def log_activity(self, activity_type, data=None):
        """Log an activity to daily log."""
        now = datetime.datetime.now()
        entry = {
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'type': activity_type,
            'data': data or {}
        }
        daily = self._load_json(DAILY_LOG_FILE, [])
        daily.append(entry)
        self._save_json(DAILY_LOG_FILE, daily)
        self.check_and_cleanup()

    def remember(self, key, value):
        """Save permanent key-value to long term memory."""
        lt = self._load_json(LONG_TERM_FILE, {})
        lt[key] = {'value': value, 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        self._save_json(LONG_TERM_FILE, lt)
        print(f"[Memory] Yaad kiya: {key} = {value}")

    def recall(self, key):
        """Recall saved value from long term memory."""
        lt = self._load_json(LONG_TERM_FILE, {})
        if key in lt:
            return lt[key].get('value')
        return None

    def forget(self, key):
        """Delete a key from long term memory."""
        lt = self._load_json(LONG_TERM_FILE, {})
        if key in lt:
            del lt[key]
            self._save_json(LONG_TERM_FILE, lt)
            print(f"[Memory] Bhool gaya: {key}")
        else:
            print(f"[Memory] '{key}' nahi mila.")

    def get_long_term_count(self):
        """Get count of long term memories."""
        lt = self._load_json(LONG_TERM_FILE, {})
        return len(lt)

    def set_storage_limit(self, mb):
        """Set storage limit in MB and save to config."""
        self.storage_limit = mb * 1024 * 1024
        config = self._load_json(CONFIG_FILE, {})
        config['storage_limit_mb'] = mb
        self._save_json(CONFIG_FILE, config)
        print(f"[Memory] Limit set to {mb}MB")

    def get_storage_limit_mb(self):
        """Get storage limit in MB."""
        return self.storage_limit // (1024 * 1024)

    def clear_session(self):
        """Clear session commands only."""
        self._save_json(SESSION_FILE, [])
        print("[Memory] Session clear ho gaya.")

    def clear_daily_log(self):
        """Clear daily log completely."""
        self._save_json(DAILY_LOG_FILE, [])
        print("[Memory] Daily log clear ho gaya.")

    def clear_long_term(self):
        """Clear long term history."""
        self._save_json(LONG_TERM_FILE, {})
        print("[Memory] Long term history clear ho gaya.")

    def clear_all(self):
        """Clear session and daily log only (not long term)."""
        self.clear_session()
        self.clear_daily_log()
        print("[Memory] Session aur daily log clear ho gaye.")

    def clear_history(self):
        """Clear long term history (forget all)."""
        self.clear_long_term()
        print("[Memory] Sab long term memories bhool gaya.")

    def show_status(self):
        """Show complete memory status."""
        size = self.get_memory_size()
        size_mb = size / (1024 * 1024)
        limit_mb = self.storage_limit / (1024 * 1024)
        
        print("\n" + "="*40)
        print(" JARVIS Memory Status ".center(40))
        print("="*40)
        print(f"  Location: {MEMORY_DIR}")
        print(f"  Storage: {size_mb:.2f}MB / {limit_mb:.0f}MB")
        print(f"  Last app: {self.get_last_app() or 'None'}")
        
        today = self.get_today_activity()
        print(f"  Today's activities: {len(today)}")
        
        daily = self._load_json(DAILY_LOG_FILE, [])
        if daily:
            dates = [e.get('date', '') for e in daily if e.get('date')]
            if dates:
                print(f"  Log range: {min(dates)} -> {max(dates)}")
        
        session = self.get_session_commands(5)
        if session:
            print(f"\n  Last {len(session)} commands:")
            for cmd in session:
                print(f"    [{cmd['time']}] {cmd['command']}")
        
        lt_count = self.get_long_term_count()
        print(f"\n  Long term memories: {lt_count} items")
        
        print("="*40)