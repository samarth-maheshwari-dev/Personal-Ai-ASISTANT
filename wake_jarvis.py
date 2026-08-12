import ctypes
from ctypes import wintypes
import speech_recognition as sr
import subprocess
import winsound
import time
import os
import sys
import threading
import psutil
from datetime import datetime

# CONFIGURATION
JARVIS_DIR = r"C:\Users\ASUS\OneDrive\Desktop\JARVIS"
VENV_PYTHON = os.path.join(JARVIS_DIR, ".venv", "Scripts", "python.exe")
JARVIS_SCRIPT = os.path.join(JARVIS_DIR, "jarvis.py")
LOG_FILE = os.path.join(JARVIS_DIR, "wake_log.txt")

WAKE_PHRASES = ["wake up jarvis", "jarvis wake up", "hey jarvis", "ok jarvis", "open jarvis"]
HOTKEY = "ctrl+alt+j"

# ── Native Windows API constants ──
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000
VK_J = 0x4A                      # 'J' virtual key code
WM_HOTKEY = 0x0312
HOTKEY_ID = 1
ERROR_ALREADY_EXISTS = 183
ERROR_HOTKEY_ALREADY_REGISTERED = 1409

# Single-instance mutex (prevents duplicate wake processes)
MUTEX_NAME = "Global\\JARVIS_WakeHotkey_Mutex"

# WinDLL with use_last_error=True so we can inspect GetLastError()
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# STATE
last_triggered_time = 0
cooldown_seconds = 3


def log_message(message):
    """Writes a message with a timestamp to the log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception:
        pass


def acquire_single_instance():
    """Creates a named mutex. Returns False if another instance is already running."""
    kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = ctypes.get_last_error()
    if last_error == ERROR_ALREADY_EXISTS:
        return False
    return True


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
    """Triggers the launch/focus of the JARVIS GUI Application."""
    global last_triggered_time

    current_time = time.time()
    if current_time - last_triggered_time < cooldown_seconds:
        return

    last_triggered_time = current_time

    # Success beeps
    winsound.Beep(1000, 200)
    winsound.Beep(1200, 200)

    # Launch GUI logic via start_jarvis_gui.vbs or npx electron .
    try:
        vbs_script = os.path.join(JARVIS_DIR, "start_jarvis_gui.vbs")
        if os.path.exists(vbs_script):
            subprocess.Popen(['wscript.exe', vbs_script], cwd=JARVIS_DIR)
        else:
            frontend_dir = os.path.join(JARVIS_DIR, "frontend jarvis")
            subprocess.Popen(['npx.cmd', 'electron', '.'], cwd=frontend_dir)
        log_message("[Wake] Focused/Launched JARVIS GUI Application.")
    except Exception as e:
        log_message(f"[Wake] ERROR launching GUI: {e}")


def hotkey_thread():
    """Registers the global hotkey via native Windows API and pumps messages.

    RegisterHotKey works at the OS level — unlike keyboard library hooks,
    it reliably receives the hotkey even when elevated/admin windows have focus.
    """
    log_message(f"[Hotkey] Registering {HOTKEY} via native RegisterHotKey...")

    # RegisterHotKey(NULL, id, MOD_CONTROL|MOD_ALT|MOD_NOREPEAT, 'J')
    try:
        mods = MOD_CONTROL | MOD_ALT | MOD_NOREPEAT
        ok = user32.RegisterHotKey(None, HOTKEY_ID, mods, VK_J)
        if not ok:
            last_error = ctypes.get_last_error()
            log_message(f"[Hotkey] RegisterHotKey failed with error {last_error}")

            if last_error == ERROR_HOTKEY_ALREADY_REGISTERED:
                log_message("[Hotkey] Hotkey already registered by another app. Trying keyboard fallback...")
                _hotkey_fallback()
            return

        log_message("[Hotkey] Listening for ctrl+alt+j... (native RegisterHotKey active)")

        # Message pump — WM_HOTKEY arrives on THIS thread's queue.
        msg = wintypes.MSG()
        while True:
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0:      # WM_QUIT received
                break
            if result == -1:     # Error
                log_message(f"[Hotkey] GetMessage error: {ctypes.get_last_error()}")
                break

            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                open_terminal()

            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    except Exception as e:
        log_message(f"[Hotkey] ERROR in hotkey thread: {e}")
        # Last resort: try the keyboard library
        _hotkey_fallback()


def _hotkey_fallback():
    """Fallback hotkey listener using the keyboard library (if installed)."""
    try:
        import keyboard
        keyboard.add_hotkey("ctrl+alt+j", lambda: open_terminal())
        log_message("[Hotkey] Fallback listener active via keyboard library.")
        keyboard.wait()
    except Exception as e:
        log_message(f"[Hotkey] Fallback failed too: {e}")


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

                    for phrase in WAKE_PHRASES:
                        if phrase in text:
                            log_message(f"[Wake] Voice detected: '{text}'")
                            open_terminal()
                            break

                except sr.UnknownValueError:
                    continue  # Silent recognition failure
                except sr.RequestError as e:
                    # Google API error
                    time.sleep(1)
                    continue
            except Exception:
                # Catch-all for mic errors/system interrupts
                time.sleep(1)
                continue


if __name__ == "__main__":
    # Single-instance guard — exit silently if another wake process is running
    if not acquire_single_instance():
        sys.exit(0)

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

