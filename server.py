"""
JARVIS Web Server — FastAPI backend that wraps the JARVIS engine.

Exposes:
    POST /api/command   →  Submit a command, get structured JSON response
    GET  /ws            →  WebSocket for live logs (green terminal output)

The frontend (Vite + React) calls /api/command and streams logs via /ws.

Run:
    python server.py
    (or: uvicorn server:app --host 0.0.0.0 --port 8000)
"""

import asyncio
import builtins
import io
import json
import threading
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── JARVIS engine ──
from jarvis import (
    Jarvis,
    split_into_parts,
    is_fast_command,
    hinglish_to_english,
)
from brain import think as brain_think

app = FastAPI(title="JARVIS Web API", version="1.0.0")

# Allow the Vite dev server (and any local frontend) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local personal use. Tighten for production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOG STREAMING — capture print() output and broadcast to WS
# ============================================================

class LogStream(io.TextIOBase):
    """A stream that captures written text and pushes it to all WS clients."""

    def __init__(self):
        self.subscribers: List[WebSocket] = []
        self._lock = threading.Lock()

    def write(self, text: str) -> int:
        if not text or text.strip() == "":
            return len(text)
        self.broadcast(text)
        return len(text)

    def flush(self):
        pass

    def broadcast(self, text: str):
        with self._lock:
            subs = list(self.subscribers)
        if not subs:
            return
        message = {
            "type": "log",
            "content": text,
            "timestamp": datetime.now().isoformat(),
        }
        for ws in subs:
            loop = getattr(ws, "_loop", None)
            if loop is None:
                continue
            try:
                asyncio.run_coroutine_threadsafe(ws.send_json(message), loop)
            except Exception:
                pass

    def register(self, ws: WebSocket):
        with self._lock:
            self.subscribers.append(ws)

    def unregister(self, ws: WebSocket):
        with self._lock:
            if ws in self.subscribers:
                self.subscribers.remove(ws)


log_stream = LogStream()

# ── Redirect stdout/stderr so JARVIS print() output reaches the frontend ──
sys_stdout = __import__("sys").stdout
sys_stderr = __import__("sys").stderr
__import__("sys").stdout = log_stream
__import__("sys").stderr = log_stream


# ============================================================
# INTERACTIVE INPUT HANDLING
# ============================================================

def _auto_input_call(prompt=""):
    """Thread-safe replacement for builtins.input.

    When JARVIS asks the user to pick a YouTube video / confirm a delete,
    we auto-select a sane default (first choice / cancel) and log it.
    """
    if prompt and any(k in prompt.lower() for k in ("confirm", "haan", "nahi")):
        log_stream.write(f"[Web] Auto-answer: {prompt.strip()} -> no (cancel)\n")
        return "no"
    if prompt and any(k in prompt.lower() for k in ("select", "kaunsa", "number")):
        log_stream.write("[Web] Auto-selecting first option (video 1).\n")
        return "1"
    log_stream.write(f"[Web] Auto-answer: {prompt.strip()} -> no\n")
    return "no"


# ============================================================
# REQUEST MODEL
# ============================================================

class CommandRequest(BaseModel):
    input: str


# ============================================================
# JARVIS SINGLETON
# ============================================================

_jarvis = None
_jarvis_lock = threading.Lock()


def get_jarvis() -> Jarvis:
    global _jarvis
    with _jarvis_lock:
        if _jarvis is None:
            # Replace builtins.input so interactive prompts don't block
            builtins.input = _auto_input_call
            _jarvis = Jarvis()
        return _jarvis


# ============================================================
# COMMAND ENGINE
# ============================================================

def run_command(raw_input: str) -> Dict[str, Any]:
    """Submit a raw command string through JARVIS's engine and return a result."""
    jarvis = get_jarvis()

    # Clear chain apps from previous command
    jarvis._chain_opened_apps.clear()

    # Preprocess YouTube compound commands
    processed = jarvis.preprocess_youtube_compound(raw_input)

    # Split compound commands (then / phir / and / aur)
    parts = split_into_parts(processed)

    result_parts: List[str] = []
    last_action = None
    last_target = None
    success = True

    for part in parts:
        part = part.strip()
        if not part:
            continue

        try:
            actual = None
            if is_fast_command(part):
                actual = part
            else:
                # Try Hinglish translation
                translated = hinglish_to_english(part)
                if translated != part:
                    actual = translated
                else:
                    # Route through brain.think()
                    brain_result = brain_think(part)
                    if brain_result and brain_result.get("type") == "conversation":
                        reply = brain_result.get("reply", "").strip()
                        result_parts.append(reply)
                        log_stream.write(f"[JARVIS] {reply}\n")
                        continue
                    actual = part

            # Execute the command
            jarvis.parse_and_run(actual)
            result_parts.append(actual)
            words = actual.split()
            last_action = words[0] if words else None
            last_target = " ".join(words[1:]) if len(words) > 1 else None
        except Exception as e:
            success = False
            log_stream.write(f"[Jarvis] Command failed: {e}\n")
            result_parts.append(f"Error: {e}")

    # Build response
    message = "\n".join(result_parts) if result_parts else "Command executed."
    return {
        "message": message,
        "type": "command",
        "action": last_action,
        "target": last_target,
        "model_used": "Ollama",
        "success": success,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================
# API ENDPOINTS
# ============================================================

@app.post("/api/command")
async def api_command(req: CommandRequest):
    """Handle a command from the frontend."""
    raw = (req.input or "").strip()
    if not raw:
        return {
            "message": "Empty command.",
            "type": "error",
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }

    # Run in a thread so blocking JARVIS calls don't block the event loop
    result = await asyncio.to_thread(run_command, raw)
    return result


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "JARVIS", "time": datetime.now().isoformat()}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket endpoint for live log streaming."""
    await ws.accept()
    ws._loop = asyncio.get_running_loop()
    log_stream.register(ws)
    # Send a welcome log
    await ws.send_json({
        "type": "log",
        "content": "[JARVIS] WebSocket connected. Ready for commands.\n",
        "timestamp": datetime.now().isoformat(),
    })
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    except WebSocketDisconnect:
        pass
    finally:
        log_stream.unregister(ws)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():
    # Warm up the JARVIS instance
    log_stream.write("[JARVIS] Initializing engine...\n")
    try:
        get_jarvis()
        log_stream.write("[JARVIS] Engine ready.\n")
    except Exception as e:
        log_stream.write(f"[JARVIS] Engine init error: {e}\n")


if __name__ == "__main__":
    import uvicorn

    print("""
    ╔══════════════════════════════════════════════════════╗
    ║  JARVIS WEB SERVER                                   ║
    ║  API:   http://localhost:8000/api/command            ║
    ║  Live:  ws://localhost:8000/ws                       ║
    ║  Health:http://localhost:8000/api/health             ║
    ╚══════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
