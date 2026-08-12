# JARVIS — Open-Source Full-Stack AI Desktop Assistant 🤖⚡

[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org)
[![Electron 30](https://img.shields.io/badge/Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://electronjs.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Ollama](https://img.shields.io/badge/Ollama-AI_Brain-black?style=for-the-badge)](https://ollama.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An open-source **Full-Stack AI Desktop Assistant** for Windows. JARVIS combines a React/Electron desktop shell, an asynchronous FastAPI backend microservice, real-time WebSocket log streaming, a multi-model Ollama AI router, Microsoft Neural TTS, and native Windows OS automation.

---

## 📌 Architectural Overview

JARVIS is engineered as a local-first, multi-tier full-stack application. Rather than sending raw text to an external API, it processes input through a multi-stage intent pipeline that decides whether to execute a deterministic OS automation action, perform a web search, or invoke a multi-model AI reasoning chain.

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                       DESKTOP / FRONTEND LAYER                          │
 │  Electron 30 Shell · React 18 · TailwindCSS · Framer Motion · Canvas    │
 └───────────────────────────────────┬─────────────────────────────────────┘
                                     │ HTTP REST (POST /api/command)
                                     │ WebSocket (/ws Live Logs)
                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                        BACKEND SERVICE LAYER                            │
 │            FastAPI Server (Python 3.13) · Uvicorn · LogStream           │
 └───────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                   INTENT & COMMAND ROUTER (brain.py)                    │
 └───────┬───────────────────────────┼───────────────────────────┬─────────┘
         │ Deterministic Action      │ AI Reasoning              │ Live Search
         ▼                           ▼                           ▼
 ┌───────────────┐           ┌───────────────┐           ┌───────────────┐
 │ OS AUTOMATION │           │ OLLAMA ROUTER │           │  WEB SEARCH   │
 │ Win32 / UWP   │           │ 5-Model Chain │           │ DuckDuckGo    │
 │ CoreAudio     │           │ Cloud / Local │           │ Summarizer    │
 │ Chrome/Spotify│           └───────┬───────┘           └───────────────┘
 └───────┬───────┘                   │                           │
         │                           └───────────┬───────────────┘
         │                                       │ Response Text
         ▼                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                      NEURAL TTS ENGINE (edge-tts)                       │
 │      Hinglish / English Latin Script  ➜ en-IN-NeerjaNeural (Indian Accent)│
 │      Devanagari Hindi Script          ➜ hi-IN-SwaraNeural               │
 └───────────────────────────────────┬─────────────────────────────────────┘
                                     │ Base64 Audio Stream + JSON Response
                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                 REACT FRONTEND & AUDIO PLAYER EXECUTION                 │
 └─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Technology Stack

| Layer | Component | Description |
|---|---|---|
| **Desktop Shell** | Electron 30, Node.js IPC, Windows API | Manages frameless desktop windowing, system tray integration, native media permissions, and global hotkeys (`Ctrl+Alt+J`). Spawns backend background processes quietly (`windowsHide: true`). |
| **Frontend UI** | React 18, Vite 5, TailwindCSS, Framer Motion | Modern dashboard featuring animated canvas visualizers, dynamic chat thread persistence, voice input controls, and custom title bars. |
| **Backend API** | Python 3.13, FastAPI, Uvicorn | Asynchronous web server exposing REST endpoints (`/api/command`, `/api/tts`, `/api/system-prompt`) and real-time WebSocket log streaming (`/ws`). |
| **AI Orchestration** | `ai/ollama_router.py`, `brain.py` | 5-model priority fallback pipeline (Cloud proxies to local Ollama models) with context-aware Hinglish intent classification. |
| **Speech Pipeline** | `edge-tts`, `gTTS`, Web Speech API | Dual-mode Microsoft Edge Neural Speech Synthesis (`en-IN-NeerjaNeural` & `hi-IN-SwaraNeural`) paired with `hi-IN` Web Speech STT recognition. |
| **OS Automation** | `pywin32`, `pycaw`, `nircmd`, `yt-dlp` | Win32 window state management, CoreAudio volume manipulation, Chrome tab control, Spotify web playback, and Desktop file operations. |
| **State & Storage** | LocalStorage, JSON File Store | Thread history stored in client LocalStorage; system configuration, memory context, and daily logs managed via structured JSON storage (`memory_manager.py`). |

---

## ⚡ Feature Implementation Matrix

| Category | Capability / Command | Technical Implementation | Status |
|---|---|---|---|
| **Window Control** | `chrome kholo`, `notepad band karo`, `minimize`, `maximize`, `focus` | Win32 API via `pywin32` + UWP App Launcher (`explorer.exe shell:AppsFolder\...`). Tracks active window handles. | ✅ Implemented |
| **Volume Control** | `volume 50% karo`, `mute karo`, `awaaz badhaao / ghatao` | CoreAudio Windows API via `pycaw` with fallback execution via `nircmd.exe`. | ✅ Implemented |
| **Hinglish Parser** | `awaaz badhaao`, `gaana bajao`, `bnd karo`, `kholo` | Rule-based Hinglish translation layer + Ollama fallback. No external translation API required. | ✅ Implemented |
| **Neural TTS** | Natural Indian Female accent voice output | `edge-tts` streaming base64 MP3 (`en-IN-NeerjaNeural` for Hinglish/English Latin script; `hi-IN-SwaraNeural` for Devanagari). | ✅ Implemented |
| **Speech Input (STT)** | Speech-to-Text input with animated waveform | Web Speech API configured to `hi-IN` with visual pulse status states in React. | ✅ Implemented |
| **YouTube Automation** | `search lofi music on youtube`, `play 2nd video` | Metadata extraction via `yt-dlp` paired with Chrome process automation. | ✅ Implemented |
| **Spotify Automation** | `play shape of you on spotify`, `next on spotify` | Spotify Web player automation running inside a dedicated Chrome browser instance. | ✅ Implemented |
| **AI Reasoning** | General chat, code generation, technical Q&A, math | 5-model priority chain handled via Ollama Gateway (`ai/ollama_router.py`). | ✅ Implemented |
| **Web Search** | `weather in Indore today`, `latest news update` | Real-time multi-attempt search using DuckDuckGo (`ddgs`) with LLM factual summarization. | ✅ Implemented |
| **File Generation** | `create file sort.py and write bubble sort code` | Direct disk IO with automated markdown code block cleaning, saving directly to user Desktop. | ✅ Implemented |
| **Memory System** | `memory remember my name Samarth`, `memory recall` | Persistent JSON storage (`memory_manager.py`) with 1GB automated log pruning. | ✅ Implemented |
| **Global Overlay** | `Ctrl+Alt+J` shortcut key | Electron `globalShortcut` API registering system-wide hotkeys to toggle/focus overlay. | ✅ Implemented |
| **Silent Backend** | Background execution without visible CMD windows | Node `child_process.spawn` detached with `windowsHide: true` for `server.py` & `ollama`. | ✅ Implemented |

---

## 🧩 AI Architecture & Multi-Model Routing

JARVIS unifies all AI operations under a single router interface (`ai/ollama_router.py`) connected to a local Ollama instance (`http://localhost:11434`). It executes requests against a prioritized fallback chain:

```
                      [ User Input Query ]
                                │
                                ▼
                   ┌──────────────────────────┐
                   │   ai/ollama_router.py    │
                   └────────────┬─────────────┘
                                │
       ┌────────────────────────┼────────────────────────┐
       │ Priority 1             │ Priority 2             │ Priority 3
       ▼ (30s)                  ▼ (30s)                  ▼ (120s)
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ minimax-m3   │ ──────► │ nemotron-3   │ ──────► │ gemma4:e2b   │
│ :cloud       │ Timeout │ :cloud       │ Timeout │ (Local)      │
└──────────────┘         └──────────────┘         └──────┬───────┘
                                                         │ Timeout
                                                         ▼
                                                  ┌──────────────┐
                                                  │ qwen2.5:3b   │ (Priority 4 - 60s)
                                                  └──────┬───────┘
                                                         │ Timeout
                                                         ▼
                                                  ┌──────────────┐
                                                  │ phi3:mini    │ (Priority 5 - 60s)
                                                  └──────────────┘
```

1. **Cloud Proxies (Priority 1–2)**: High-speed models accessed through Ollama's model gateway for fast responses when online.
2. **Local Models (Priority 3–5)**: Fully offline local models running on CPU/GPU hardware. If internet is disconnected or cloud models time out, execution automatically fails over to local models without throwing user-facing errors.

---

## 📂 Project Structure

```
JARVIS/
├── ai/
│   └── ollama_router.py       # Priority fallback chain & Ollama API adapter
├── memory/
│   ├── memory_manager.py      # JSON-backed memory & log manager
│   ├── history.json           # Conversation memory
│   └── daily_log.json         # Daily activity log
├── frontend jarvis/
│   ├── main.js                # Electron main process (IPC, hotkeys, process spawner)
│   ├── package.json           # Frontend dependencies & build config
│   ├── dist/                  # Production Vite build artifacts
│   └── src/
│       ├── App.jsx            # React root component
│       └── components/
│           ├── AppShell.jsx   # Layout wrapper & hotkey handlers
│           ├── TitleBar.jsx   # Custom window control bar
│           ├── CommandBar/    # Input bar, mic STT & Audio playback
│           ├── Main/          # Canvas visualizer & quick cards
│           └── Sidebar/       # Chat thread navigation & drawer
├── brain.py                    # Intent classifier & query router
├── jarvis.py                   # Core OS automation engine (Win32, Volume, Chrome, Media)
├── server.py                   # FastAPI server, WebSockets & Edge-TTS engine
├── wake_jarvis.py              # Hotkey daemon & background trigger listener
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation
```

---

## ⚙️ Installation & Setup Guide

### Prerequisites
- **Operating System**: Windows 10 / Windows 11 (64-bit)
- **Python**: Version 3.13 or higher
- **Node.js**: Version 18.0 or higher
- **Ollama**: Installed from [ollama.ai](https://ollama.ai)

---

### Step 1 — Clone Repository
```bash
git clone https://github.com/samarth-maheshwari-dev/Personal-Ai-ASISTANT.git
cd Personal-Ai-ASISTANT
```

### Step 2 — Set Up Python Backend
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3 — Install AI Models (Ollama)
Ensure Ollama is running, then pull at least one local model for offline fallback:
```bash
ollama pull qwen2.5:3b
ollama pull phi3:mini
```

### Step 4 — Run the Application

#### Option A: Run as Desktop App (Electron Shell)
```bash
# Terminal 1: Start Backend API
python server.py

# Terminal 2: Launch Electron Application
cd "frontend jarvis"
npm install
npm run electron .
```

#### Option B: Run in Development Mode (Vite + Web Browser)
```bash
# Terminal 1: Start Backend API
python server.py

# Terminal 2: Start Vite Dev Server
cd "frontend jarvis"
npm run dev
# Open http://localhost:5173 in Google Chrome
```

---

## 📡 API Reference

### 1. Execute Command or Chat
`POST /api/command`
```json
// Request Payload
{
  "input": "chrome kholo then set volume 40",
  "system_prompt": "Optional custom system prompt override"
}

// Response Payload
{
  "message": "Opening Chrome for you right now, sir!",
  "type": "command",
  "action": "open",
  "target": "chrome",
  "model_used": "Ollama",
  "success": true,
  "timestamp": "2026-08-12T14:30:00.000000",
  "audio": "data:audio/mp3;base64,SUQzBAAAAAAA..."
}
```

### 2. Standalone Text-to-Speech
`POST /api/tts`
```json
// Request Payload
{
  "text": "Arre, kya hua Samarth?"
}

// Response Payload
{
  "audio": "data:audio/mp3;base64,SUQzBAAAAAAA..."
}
```

### 3. WebSocket Real-Time Logs
`GET /ws`
- Connects to backend WebSocket stream. Receives live stdout text lines formatted for terminal displays.

---

## ⚠️ System Limitations & Caveats

- **OS Specificity**: Window management and volume control functions rely on native Windows Win32 APIs (`pywin32`) and CoreAudio (`pycaw`), making OS automation functional on Windows only.
- **Chrome Requirement**: Browser automation scripts expect Google Chrome to be installed in standard Windows executable paths.
- **Hardware Resources**: Local Ollama model execution speed depends on available system RAM/VRAM. Minimum 8GB system RAM recommended.

---

## 🚧 Development Roadmap

- [x] **Phase 1**: Core OS Automation Engine, Electron + React UI, Ollama Router, Indian Female Neural TTS.
- [ ] **Phase 2 — Mobile Web Remote**: Lightweight PWA interface connecting over WebSockets to control desktop tasks remotely from a smartphone.
- [ ] **Phase 3 — Messaging Automation**: Automated WhatsApp and Instagram message dispatching via Playwright browser contexts.
- [ ] **Phase 4 — Local Document RAG**: Local PDF and document parsing pipeline with vector embeddings for semantic document search.

---

## 📜 License & Acknowledgments

This project is open-source under the [MIT License](LICENSE).

**Author**: Samarth Maheshwari  
*Full-Stack Engineer & AI Automation Builder — Indore, India 🇮🇳*  
- GitHub: [@samarth-maheshwari-dev](https://github.com/samarth-maheshwari-dev)
