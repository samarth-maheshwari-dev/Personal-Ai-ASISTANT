@echo off
title JARVIS Web Server
echo ============================================
echo   JARVIS Web Server Launcher
echo   Uses project .venv Python explicitly
echo ============================================
echo.

cd /d "%~dp0"

REM Check if .venv exists, if not create it and install deps
if not exist ".venv\Scripts\python.exe" (
    echo [SETUP] Creating virtual environment...
    python -m venv .venv
    echo [SETUP] Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo [JARVIS] Starting server with .venv Python...
".venv\Scripts\python.exe" server.py

pause
