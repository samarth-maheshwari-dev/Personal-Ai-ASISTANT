import speech_recognition as sr
import subprocess
import winsound
import time
import os
import sys
import threading
import keyboard
import psutil
from datetime import datetime

# CONFIGURATION
JARVIS_DIR = r"C:\Users\ASUS\OneDrive\Desktop\JARVIS"
VENV_PYTHON = os.path.join(JARVIS_DIR, ".venv", "Scripts", "python.exe")
JARVIS_SCRIPT = os.path.join(JARVIS_DIR, "jarvis.py")
LOG_FILE = os.path.join(JARVIS_DIR, "wake_log.txt")

WAKE_PHRASES = ["wake up jarvis", "jarvis wake up", "hey jarvis", "ok jarvis", "open jarvis"]
HOTKEY = "ctrl+alt+j"

# STATE
last_triggered_time = 0
cooldown_seconds = 3

def log_message(message):
    """Writes a message with a timestamp to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def is_jarvis_running():
    """Checks if jarvis.py is already running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                joined = " ".join(cmdline)
                if "jarvis.py" in joined and "wake_jarvis.py" not in joined:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def open_terminal():
    """Triggers the launch of the JARVIS terminal with duplicate detection."""
    global last_triggered_time
    
    current_time = time.time()
    if current_time - last_triggered_time < cooldown_seconds:
        return

    last_triggered_time = current_time

    if is_jarvis_running():
        log_message("[Wake] JARVIS already running! Skipping launch.")
        print("[Wake] JARVIS already running!")
        winsound.Beep(1000, 100) # One short beep as requested
        return

    # Success beeps
    # Play two beeps: 1000Hz then 1200Hz as per request
    winsound.Beep(1000, 200)
    winsound.Beep(1200, 200)

    # Launch logic
    # Try wt.exe first
    try:
        # Check if wt.exe is available in the path or typical location
        # A simple check is to try running it with --version or just try-except Popen
        # The user provided an exact command string for wt.exe
        subprocess.Popen([
            'wt.exe', 
            '-d', JARVIS_DIR, 
            VENV_PYTHON, JARVIS_SCRIPT
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        log_message("[Wake] Launched JARVIS via Windows Terminal.")
    except (FileNotFoundError, Exception):
        # Fallback to cmd.exe
        try:
            full_cmd = f'"{VENV_PYTHON}" "{JARVIS_SCRIPT}"'
            subprocess.Popen([
                'cmd.exe', '/k', full_cmd
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            log_message("[Wake] Launched JARVIS via CMD fallback.")
        except Exception as e:
            log_message(f"[Wake] ERROR launching terminal: {e}")

def hotkey_thread():
    """Listens for the global hotkey."""
    log_message(f"[Hotkey] Listening for {HOTKEY}...")
    try:
        keyboard.add_hotkey(HOTKEY, lambda: open_terminal())
        keyboard.wait()
    except Exception as e:
        log_message(f"[Hotkey] ERROR: {e}")

def voice_thread():
    """Listens for the voice wake word."""
    recognizer = sr.Recognizer()
    
    try:
        mic = sr.Microphone()
    except Exception as e:
        log_message("[Wake] No microphone found, voice disabled")
        print("[Wake] No microphone found, voice disabled")
        return

    log_message("[Wake] Voice listener started.")
    
    with mic as source:
        # Initial adjustment for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                try:
                    text = recognizer.recognize_google(audio).lower()
                    
                    found = False
                    for phrase in WAKE_PHRASES:
                        if phrase in text:
                            log_message(f"[Wake] Voice detected: '{text}'")
                            open_terminal()
                            found = True
                            break
                    
                except sr.UnknownValueError:
                    continue # Silent recognition failure
                except sr.RequestError as e:
                    # Google API error
                    time.sleep(1)
                    continue
            except Exception:
                # Catch-all for mic errors/system interrupts
                time.sleep(1)
                continue

if __name__ == "__main__":
    # Create log file if not exists and log startup
    with open(LOG_FILE, "a") as f:
        f.write(f"\n--- JARVIS Wake System Started at {datetime.now()} ---\n")

    # Start threads
    t1 = threading.Thread(target=hotkey_thread, daemon=True)
    t2 = threading.Thread(target=voice_thread, daemon=True)

    t1.start()
    t2.start()

    # Keep the main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("[System] Shutting down.")
        sys.exit(0)
