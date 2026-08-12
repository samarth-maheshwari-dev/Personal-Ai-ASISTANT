# JARVIS — Open-Source Full-Stack Desktop AI Assistant 🤖⚡

[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org)
[![Electron](https://img.shields.io/badge/Electron-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://electronjs.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Ollama](https://img.shields.io/badge/Ollama-AI_Brain-black?style=for-the-badge)](https://ollama.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> An agency-grade, open-source **Full-Stack Desktop AI Assistant** built for Windows. Integrates a sleek React/Electron frontend, a high-performance Python FastAPI backend, a multi-model Ollama AI Thinking Layer, Microsoft Neural Speech Synthesis, and native OS automation.

---

## 💡 What is JARVIS?

**JARVIS** is not a simple chatbot skin or API wrapper. It is a complete, production-grade **Full-Stack AI Engineering System** designed to give you a personal Iron-Man-style assistant running locally on your machine.

It unifies:
1. **Modern Desktop UI**: Electron shell + React 18 dashboard with real-time WebSocket log streaming.
2. **High-Speed Microservice Backend**: FastAPI Python server handling asynchronous command parsing and system automation.
3. **Local & Cloud AI Brain**: Ollama multi-model priority fallback chain that thinks, reasons, and handles Hinglish naturally.
4. **Neural Speech Synthesis**: Native Microsoft Edge Neural TTS delivering crystal-clear Indian female voice responses (`hi-IN-SwaraNeural` and `en-IN-NeerjaNeural`).
5. **Windows OS Automation**: Native desktop window control, volume management, Spotify/YouTube web automation, and file generation.

---

## 🛠️ Full-Stack Technology Stack

```
 🖥️ FRONTEND LAYER         ⚡ BACKEND & API LAYER        🧠 AI & SPEECH ENGINE        💻 OS AUTOMATION
┌─────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│  Electron 30 Shell  │   │   FastAPI (Python)   │   │  Ollama Router (5M)  │   │  Win32 & UWP API     │
│  React 18 + Vite    │ ◄─┼─► Uvicorn Web Server ┼─► │  Microsoft Edge TTS  │ ◄─┼─► Pycaw / Nircmd     │
│  TailwindCSS        │   │   WebSocket (/ws)    │   │  Web Search Engine   │   │  yt-dlp & Chrome API │
│  Framer Motion      │   │   CORS & Subprocess  │   │  Hinglish Classifier │   │  FileSystem Engine   │
└─────────────────────┘   └──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

| Stack Layer | Technologies Used | Purpose & Responsibilities |
|---|---|---|
| **Frontend UI** | React 18, Vite, TailwindCSS, Framer Motion, Lucide Icons | Responsive Iron-Man dashboard, animated mic visualizers, command bar, dynamic message threads. |
| **Desktop Shell** | Electron 30, Global Hotkeys (`Ctrl+Alt+J`), Node IPC | System tray integration, global overlay hotkey, background process management. |
| **Backend API** | Python 3.13, FastAPI, Uvicorn, WebSockets | REST API (`POST /api/command`), real-time WebSocket stdout streaming (`/ws`), async execution. |
| **AI Brain Layer** | Ollama Router, DuckDuckGo Search API | 5-model priority fallback, intent routing, web search summarization, custom system prompts. |
| **Speech Engine** | `edge-tts`, `gTTS`, Web Speech API | Neural Indian Female TTS (`en-IN-NeerjaNeural` & `hi-IN-SwaraNeural`), `hi-IN` speech recognition. |
| **OS Automation** | `pywin32`, `pycaw`, `nircmd`, `yt-dlp` | Window state control (open/close/minimize), CoreAudio volume, Spotify/YouTube Chrome automation. |

---

## ⚡ What JARVIS Can Do (Capability Matrix)

| Category | Features & Commands | Tech & Architecture Under the Hood | Status |
|---|---|---|---|
| **Window Management** | `chrome kholo`, `notepad band karo`, `maximize`, `minimize`, `focus` | `pywin32` + Windows EnumWindows API + UWP app launcher. Remembers last active window context. | ✅ Production |
| **Hinglish Parser** | `awaaz badhaao`, `gaana bajao`, `bnd karo`, `pehle wala chalao` | Custom rule-based Hinglish-to-English dictionary + Ollama intent classifier. Zero translation latency. | ✅ Production |
| **Volume Control** | `volume 50% karo`, `mute karo`, `awaaz badhaao / ghatao` | CoreAudio Windows API via `pycaw` with automatic fallback to `nircmd.exe`. | ✅ Production |
| **Neural Female Voice** | Natural Indian Female accent voice output (zero British/American tone) | `edge-tts` streaming base64 MP3 (`en-IN-NeerjaNeural` for Latin script & `hi-IN-SwaraNeural` for Devanagari). | ✅ Production |
| **Speech Input (STT)** | Real-time speech recognition for Hindi, Hinglish, & English | Web Speech API localized to `hi-IN` with visual soundwave animation. | ✅ Production |
| **YouTube Automation** | `search lofi music on youtube`, `play 2nd video` | `yt-dlp` metadata extraction + Chrome automation. Shows top video results directly. | ✅ Production |
| **Spotify Control** | `play shape of you on spotify`, `next on spotify`, `pause` | Spotify Web player automation running seamlessly inside a dedicated Chrome tab. | ✅ Production |
| **AI Thinking Layer** | Conversational queries, code writing, math, flirty/nerdy banter | 5-model Ollama fallback priority chain (Cloud Proxy -> Local Gemma -> Qwen -> Phi). | ✅ Production |
| **Real-Time Web Search** | `weather in Indore today`, `latest news`, `cricket score` | Dual-attempt web search via DuckDuckGo API + LLM factual summarizer. | ✅ Production |
| **File Generation** | `create file sort.py and write bubble sort code` | Direct file system IO with automated code snippet cleanup and Desktop path resolution. | ✅ Production |
| **Context Memory** | `memory remember my name Samarth`, `memory recall` | Persistent JSON key-value store, daily logs, and session history management. | ✅ Production |
| **Compound Commands** | `open chrome then search lo-fi music then volume 40` | Multi-command regex splitter (`then`, `phir`, `aur`, `and`) executed sequentially. | ✅ Production |

---

## 🧠 How It Works with AI

JARVIS uses a hybrid AI orchestration architecture:

```
[ User Query (GUI / Voice) ]
             │
             ▼
   FastAPI POST /api/command
             │
             ▼
   Intent Classification (brain.py)
             │
 ┌───────────┴─────────────────────────────┐
 │                                         │
 ▼                                         ▼
[ PC Action Command ]            [ AI Thinking Layer ]
(Open/Close/Volume/File)        (Query / Chat / Code / Web Search)
 │                                         │
 │                                         ▼
 │                            Ollama Priority Fallback Chain
 │                            ┌──────────────────────────────┐
 │                            │ 1. minimax-m3:cloud (30s)    │
 │                            │ 2. nemotron-3-super (30s)    │
 │                            │ 3. gemma4:e2b (Local 120s)   │
 │                            │ 4. qwen2.5:3b (Local 60s)    │
 │                            │ 5. phi3:mini (Local 60s)     │
 │                            └──────────────┬───────────────┘
 │                                           │
 └───────────────────┬───────────────────────┘
                     │
                     ▼
       Neural TTS Engine (edge-tts)
   ├── Devanagari Hindi → hi-IN-SwaraNeural
   └── Hinglish/Latin   → en-IN-NeerjaNeural (Indian Accent)
                     │
                     ▼
       [ Base64 Audio + Structured JSON ]
                     │
                     ▼
       [ React GUI + HTML5 Audio + Live WebSocket Logs ]
```

---

## 📥 How to Download and Run JARVIS (Easy Setup)

### Prerequisites
- **Windows 11 / 10**
- **Python 3.13+** installed
- **Node.js 18+** installed
- **Ollama** installed from [ollama.ai](https://ollama.ai)

---

### Step 1 — Clone the Repository
```bash
git clone https://github.com/samarth-maheshwari-dev/Personal-Ai-ASISTANT.git
cd Personal-Ai-ASISTANT
```

### Step 2 — Set Up Python Backend Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Pull AI Models (Ollama)
```bash
ollama pull qwen2.5:3b
ollama pull phi3:mini
```

### Step 4 — Launch the Backend Server
```bash
python server.py
# → FastAPI Server active at http://localhost:8000
```

### Step 5 — Launch the Desktop App / Frontend UI
In a new terminal tab:
```bash
cd "frontend jarvis"
npm install

# Run as Electron Desktop Application:
npm run electron .

# Or run in Web Browser:
npm run dev
# → Open http://localhost:5173
```

---

## 🚀 What's Coming Next (Roadmap)

- [ ] **Phase 2 — Remote Control via Mobile Web 📱**: Mobile PWA dashboard connecting over WebSockets to control your PC remotely from anywhere.
- [ ] **Phase 3 — WhatsApp & Instagram Automation 💬**: Automated DM responses and message dispatch via Playwright browser sessions.
- [ ] **Phase 4 — PDF Document RAG & Speech Analysis 📖**: Local vector embeddings for instant document Q&A and PDF summarization.
- [ ] **Phase 5 — Autonomous Multi-Step Agentic Workflows 🤖**: Multi-tool agent execution (e.g. `book a cab`, `summarize top 5 emails and reply`).

---

## 🤝 Open Source & Contributing

JARVIS is 100% open-source under the **MIT License**. Contributions, bug reports, and pull requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AwesomeFeature`)
3. Commit your Changes (`git commit -m 'Add AwesomeFeature'`)
4. Push to the Branch (`git push origin feature/AwesomeFeature`)
5. Open a Pull Request

---

*Built with ❤️ by **Samarth Maheshwari** — Indore, India 🇮🇳*  
*Python 3.13 | FastAPI | Electron | React | Ollama | MIT License*
