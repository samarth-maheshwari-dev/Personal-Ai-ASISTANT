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
from typing import Any, Dict, List, Optional

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

class TeeStream:
    def __init__(self, original, log_stream):
        self.original = original
        self.log_stream = log_stream
        self.encoding = getattr(original, 'encoding', 'utf-8')

    def write(self, text):
        if self.original:
            try:
                self.original.write(text)
            except Exception:
                pass
        if self.log_stream:
            try:
                self.log_stream.write(text)
            except Exception:
                pass

    def flush(self):
        if self.original:
            try:
                self.original.flush()
            except Exception:
                pass

    def isatty(self):
        return getattr(self.original, 'isatty', lambda: False)()

import sys
sys.stdout = TeeStream(sys.stdout, log_stream)
sys.stderr = TeeStream(sys.stderr, log_stream)


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
    system_prompt: Optional[str] = None

class SystemPromptRequest(BaseModel):
    system_prompt: str

class TTSRequest(BaseModel):
    text: str

import base64
import re

def is_devanagari(text: str) -> bool:
    return any('\u0900' <= c <= '\u097f' for c in text)

async def generate_tts_base64(text: str) -> Optional[str]:
    """Generates 100% Female Indian Audio (en-IN-NeerjaNeural for Hinglish/English, hi-IN-SwaraNeural for Devanagari)."""
    try:
        clean_text = re.sub(r'\*+', '', text)
        clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', clean_text).strip()
        if not clean_text:
            return None
        
        # Pick Indian Female Voice:
        # Devanagari -> hi-IN-SwaraNeural (Hindi Female Neural)
        # Hinglish/English Latin script -> en-IN-NeerjaNeural (Indian English Female Neural)
        voice = "hi-IN-SwaraNeural" if is_devanagari(clean_text) else "en-IN-NeerjaNeural"

        import edge_tts
        communicate = edge_tts.Communicate(clean_text, voice)
        mp3_fp = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_fp.write(chunk["data"])
        
        audio_bytes = mp3_fp.getvalue()
        if audio_bytes:
            b64_str = base64.b64encode(audio_bytes).decode('utf-8')
            return f"data:audio/mp3;base64,{b64_str}"
    except Exception as e:
        print(f"[TTS] Edge-TTS error: {e}")
        try:
            from gtts import gTTS
            clean_text = re.sub(r'\*+', '', text)
            clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', clean_text).strip()
            tts = gTTS(text=clean_text, lang='en', tld='co.in')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            b64_str = base64.b64encode(mp3_fp.getvalue()).decode('utf-8')
            return f"data:audio/mp3;base64,{b64_str}"
        except Exception as ge:
            print(f"[TTS] gTTS error: {ge}")
    return None


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
    # Preprocess YouTube compound commands
    processed = jarvis.preprocess_youtube_compound(raw_input)

    # Split compound commands (then / phir / and / aur)
    parts = split_into_parts(processed)

    result_parts: List[str] = []
    last_action = None
    last_target = None
    success = True

    # Global session history for context-aware command memory
    if not hasattr(run_command, "_last_target"):
        run_command._last_target = ""

    # Function for humanizing response phrasing instead of raw snake_case or mechanical execution text
    def humanize_action_message(parts_executed, last_act, last_tgt):
        if not parts_executed:
            return "Done for you, sir!"
        first = parts_executed[0]
        if first.startswith("Error"):
            return f"I ran into an issue while processing your request: {first}"
        
        # Clean text
        act = (last_act or "").lower()
        tgt = (last_tgt or "").lower()

        if act == "open":
            return f"Opening {tgt.title()} for you right now, sir!"
        elif act == "close":
            if tgt == "all":
                return "Closing all active application windows for you, sir."
            return f"Closing {tgt.title()} for you, sir."
        elif act in ("minimize", "maximize", "restore", "focus"):
            return f"I've {act}d {tgt.title()} for you, sir."
        elif act == "set" and "volume" in tgt:
            return f"Volume set to {tgt.replace('volume ', '')}%."
        elif act in ("mute", "unmute"):
            return f"System audio {act}d, sir."
        elif act == "search_youtube":
            return f"Searching YouTube for '{tgt}' for you, sir."
        elif act == "play_song":
            return f"Playing '{tgt}' on Spotify for you, sir."
        elif act in ("create", "delete", "rename"):
            return f"File operation '{act}' executed successfully, sir."
        
        # General clean response
        clean_text = " ".join([p.replace("_", " ").title() for p in parts_executed])
        return f"Executing {clean_text} for you, sir."

    # 3. Execution loop with auto-retry on failure
    MAX_RETRIES = 2
    last_is_conversational = False
    conversational_reply = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        words = part.lower().split()
        if run_command._last_target and any(w in words for w in ['it', 'that', 'this']):
            part = part.replace(' it', f' {run_command._last_target}').replace(' that', f' {run_command._last_target}').replace(' this', f' {run_command._last_target}')

        part_success = False
        attempt = 0
        last_exception = None

        while attempt <= MAX_RETRIES and not part_success:
            try:
                attempt += 1
                actual = None
                if is_fast_command(part):
                    actual = part
                else:
                    translated = hinglish_to_english(part)
                    if translated != part:
                        actual = translated
                    else:
                        brain_result = brain_think(part)
                        if brain_result and brain_result.get("type") == "conversation":
                            reply = brain_result.get("reply", "").strip()
                            conversational_reply = reply
                            last_is_conversational = True
                            log_stream.write(f"[JARVIS] {reply}\n")
                            part_success = True
                            break
                        actual = part

                # Track opened apps in chain before running parse_and_run
                if actual.startswith("open "):
                    target_name = actual[5:].strip()
                    if target_name and target_name not in jarvis._chain_opened_apps:
                        jarvis._chain_opened_apps.append(target_name)

                # Execute command
                jarvis.parse_and_run(actual)
                result_parts.append(actual)
                words = actual.split()
                last_action = words[0] if words else None
                last_target = " ".join(words[1:]) if len(words) > 1 else None
                if last_target and last_target.lower() not in ['it', 'that', 'this']:
                    run_command._last_target = last_target
                part_success = True
            except Exception as e:
                last_exception = e
                log_stream.write(f"[Jarvis] Attempt {attempt} failed for '{part}': {e}\n")
                time.sleep(0.5)  # Brief wait before retry

        if not part_success:
            success = False
            result_parts.append(f"Error: {last_exception}")

    # Build response
    if last_is_conversational and conversational_reply:
        return {
            "message": conversational_reply,
            "type": "conversation",
            "model_used": "Ollama",
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }

    if result_parts and any(p.startswith("Error") for p in result_parts):
        message = result_parts[-1]
    elif result_parts:
        message = humanize_action_message(result_parts, last_action, last_target)
    else:
        message = "Command completed successfully for you, sir."

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

    if req.system_prompt:
        try:
            from brain import set_custom_system_prompt
            set_custom_system_prompt(req.system_prompt)
        except Exception as e:
            print(f"[Server] Failed setting custom prompt: {e}")

    # Run in a thread so blocking JARVIS calls don't block the event loop
    result = await asyncio.to_thread(run_command, raw)
    msg_text = result.get("message", "")
    if msg_text:
        try:
            audio_data = await generate_tts_base64(msg_text)
            if audio_data:
                result["audio"] = audio_data
        except Exception as e:
            print(f"[Server] Failed to attach TTS audio: {e}")
    return result


@app.post("/api/tts")
async def api_tts(req: TTSRequest):
    audio_data = await generate_tts_base64(req.text or "")
    return {"audio": audio_data}


@app.get("/api/system-prompt")
async def get_system_prompt():
    try:
        from brain import get_current_system_prompt
        return {"system_prompt": get_current_system_prompt()}
    except Exception as e:
        return {"system_prompt": "", "error": str(e)}


@app.post("/api/system-prompt")
async def set_system_prompt(req: SystemPromptRequest):
    try:
        from brain import set_custom_system_prompt
        set_custom_system_prompt(req.system_prompt)
        return {"status": "ok", "system_prompt": req.system_prompt}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "JARVIS", "time": datetime.now().isoformat()}


@app.post("/api/restart")
async def restart_service():
    """Reset singleton instance & clear temporary backend state."""
    global _jarvis
    with _jarvis_lock:
        _jarvis = None
    return {"status": "restarted", "message": "JARVIS engine re-initialized successfully."}


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
