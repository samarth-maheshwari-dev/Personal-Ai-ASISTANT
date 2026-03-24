import winreg
import os
import sys

# CONFIGURATION
JARVIS_DIR = r"C:\Users\ASUS\OneDrive\Desktop\JARVIS"
VENV_PYTHONW = os.path.join(JARVIS_DIR, ".venv", "Scripts", "pythonw.exe")
WAKE_SCRIPT = os.path.join(JARVIS_DIR, "wake_jarvis.py")

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_NAME = "JARVISWakeWord"
REG_VALUE = f'"{VENV_PYTHONW}" "{WAKE_SCRIPT}"'

def entry_exists():
    """Checks if the registry entry already exists."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, REG_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except FileNotFoundError:
        return False

def add_to_startup():
    """Adds the script to startup."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, REG_VALUE)
        winreg.CloseKey(key)
        
        print("✅ JARVIS wake word added to Windows startup!")
        print("✅ Hotkey: Ctrl+Alt+J")
        print("✅ Voice: say 'wake up jarvis'")
        print("✅ Will auto-start on next Windows boot")
        print("To remove: run this script again and choose remove")
    except Exception as e:
        print(f"❌ Failed to add to startup: {e}")

def remove_from_startup():
    """Removes the script from startup."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, REG_NAME)
        winreg.CloseKey(key)
        print("✅ Removed from startup")
    except Exception as e:
        print(f"❌ Failed to remove: {e}")

def main():
    if entry_exists():
        print("JARVIS already in startup.")
        choice = input("Remove it? (yes/no): ").lower().strip()
        if choice in ["yes", "y"]:
            remove_from_startup()
        else:
            print("No changes made.")
    else:
        # Check if pythonw.exe exists first
        if not os.path.exists(VENV_PYTHONW):
            print(f"❌ Error: {VENV_PYTHONW} not found. Please ensure venv is correctly set up.")
            return
        add_to_startup()

if __name__ == "__main__":
    main()
