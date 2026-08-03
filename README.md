## JARVIS — Personal AI Assistant | Discussion & Roadmap 🤖

---

### What is JARVIS? 🧠

JARVIS is a **Windows 11 terminal-based AI assistant** built from scratch in Python 3.13 — with zero budget, zero paid APIs, and zero shortcuts.

It is not a chatbot wrapper. It is not a voice assistant skin. It is a full system that **thinks, decides, and acts** — controlling your PC like a human would, powered by a 5-model priority chain running entirely through Ollama — two cloud proxies for speed when online, three local models for full offline operation when not.

The goal was simple but ambitious: build something that feels less like a tool and more like an actual assistant that understands what you want.

---

### What JARVIS Can Do Right Now ⚡

**App Control — Full Window Management**
- Open, close, minimize, maximize, restore, focus any app
- Works on regular apps AND UWP apps (Calculator, Settings, Store)
- Remembers the last opened app — say `band karo` without repeating the name
- Chain commands: `open chrome then open notepad then close dono`

**Hinglish Support 🇮🇳**
- Fully understands mixed Hindi-English commands
- `chrome kholo`, `awaaz badhaao`, `notepad band karo`, `maximize karo`
- No translation API needed — built-in Hinglish-to-English parser

**Volume Control**
- `awaaz badhaao / ghatao`, `volume up / down`
- `awaaz band karo` (mute), `awaaz wapas lao` (unmute)
- `volume 40 karo` — set exact level
- Powered by nircmd.exe with Windows API fallback

**Browser Automation — Chrome Forced**
- Always opens in Chrome, never Edge
- Open URLs, close tabs by name
- Navigate existing Chrome window without opening new ones

**YouTube Search 🎬**
- `search lofi music on youtube` → shows 10 results with title, channel, duration
- `search python tutorial on youtube and play 3rd video` → auto-picks
- Powered by yt-dlp for reliable result fetching

**Spotify Web Player 🎵**
- `play shape of you on spotify` → opens Spotify web, plays first result
- `next on spotify`, `pause on spotify`, `previous on spotify`
- No desktop app needed — runs fully in Chrome tab

**AI Brain — 5-Model Priority Chain 🧩**

> JARVIS runs a single unified priority chain through Ollama. No juggling multiple API dashboards. No separate keys for each provider. One interface — five fallbacks — defined in `ai/ollama_router.py`.

**Priority Chain (tried in order, pehle se last tak)**

| Priority | Model | Type | Timeout | Role |
|---|---|---|---|---|
| 1 | `minimax-m3:cloud` | ☁️ Cloud Proxy | 30s | Fastest — primary response |
| 2 | `nemotron-3-super:cloud` | ☁️ Cloud Proxy | 30s | Second cloud, strong reasoning |
| 3 | `gemma4:e2b` | 💻 Offline Local | 120s | Best offline model, heavy tasks |
| 4 | `qwen2.5:3b` | 💻 Offline Local | 60s | Lightweight, fast offline |
| 5 | `phi3:mini` | 💻 Offline Local | 60s | Last resort, minimum RAM usage |

Cloud proxies (1–2) route through Ollama's cloud model interface. If you're offline or they timeout — JARVIS drops to local models (3–5) automatically. No config change, no manual switching.

**How the Brain Routes Queries**

```
User Input → ai/ollama_router.py
    ↓
1. minimax-m3:cloud        [30s timeout]
   ↓ fail / timeout
2. nemotron-3-super:cloud  [30s timeout]
   ↓ fail / timeout
3. gemma4:e2b              [120s timeout]  ← offline fallback starts here
   ↓ fail
4. qwen2.5:3b              [60s timeout]
   ↓ fail
5. phi3:mini               [60s timeout]
   ↓ all 5 fail
   → retry loop + recovery attempt
```

Every model in the chain is managed through Ollama. **No external API keys required** — everything goes through a single Ollama interface.

**Web Search (Real-Time) 🌐**
- Detects queries needing live data (weather, news, prices, scores)
- Multi-attempt search with result filtering
- Summarized by the active cloud model — clean 2-3 line answer, no hallucination dump

**File Creation 📄**
- `create file notes.txt` → AI generates full content
- `create file sort.py and write bubble sort code` → writes working code
- Direct API call — raw clean output, no markdown noise
- Saves to Desktop by default

**Memory System 💾**
- Session memory, daily log, permanent long-term storage
- `memory remember name Samarth` → `memory recall name` → `Samarth`
- 1GB limit with auto-cleanup oldest-first
- `memory status` → full dashboard

**Compound Command Chaining**
- Supports `then`, `phir`, `aur`, `and` as separators
- `open notepad then minimize notepad then close notepad` — all execute in order
- Terminal refocuses automatically after chain execution

---

### How to Download and Run JARVIS 📥

**Requirements**
- Windows 11 (Windows 10 may work)
- Python 3.13+
- Google Chrome installed
- nircmd.exe (place in JARVIS folder — for volume control)
- Ollama installed — **required** (manages all AI models, cloud + local)

**Step 1 — Clone the repo**
```bash
git clone https://github.com/samarth-maheshwari-dev/Personal-Ai-ASISTANT.git
cd Personal-Ai-ASISTANT
```

**Step 2 — Install dependencies**
```bash
pip install pyautogui pygetwindow pywin32 rapidfuzz psutil winrt-runtime winrt-Windows.Media.Control python-dotenv requests yt-dlp ddgs pycaw comtypes
```

**Step 3 — Install Ollama and pull all models**

Install Ollama from [ollama.ai](https://ollama.ai), then pull the full model chain:

```bash
# Cloud proxy models (requires internet for first pull)
ollama pull minimax-m3:cloud
ollama pull nemotron-3-super:cloud

# Offline local models (stored on your machine)
ollama pull gemma4:e2b
ollama pull qwen2.5:3b
ollama pull phi3:mini
```

> Minimum setup: pull at least `qwen2.5:3b` and `phi3:mini` for offline support. Cloud models will auto-fallback to local if Ollama can't reach them.

> No API keys needed. No `.env` required for the AI brain. Ollama manages everything.

**Step 4 — Run**
```bash
python jarvis.py
```

JARVIS loads `ai/ollama_router.py` at startup and tries models in priority order automatically. No manual switching, no config changes needed.

**Step 5 — Run the Web UI (optional) 🖥️**

JARVIS now ships with a **Web Dashboard** — a sleek Iron-Man-style JARVIS interface with a command bar, live green terminal logs, and full control of your desktop assistant from the browser.

```bash
# Terminal 1 — Start the FastAPI backend server
python server.py
# → Backend at http://localhost:8000

# Terminal 2 — Start the frontend dev server
cd "frontend jarvis"
npm install
npm run dev
# → UI at http://localhost:5173
```

Open `http://localhost:5173` in Chrome, type `open chrome`, `notepad kholo`, `volume up`, or ask anything — and watch the live logs stream in green at the bottom of the screen.

**How the Web integration works 🔌**

| Layer | Tech | Role |
|---|---|---|
| Frontend UI | Vite + React + Tailwind | Iron-Man JARVIS dashboard, command input, live log panel |
| API | FastAPI (`server.py`) | Wraps the JARVIS engine → `POST /api/command` |
| Live Logs | WebSocket (`/ws`) | Streams real-time stdout to the browser in green |
| Brain | `ai/ollama_router.py` | 5-model priority chain for conversation & commands |

- `POST /api/command` `{ "input": "open chrome" }` → structured JSON `{ message, type, action, target, model_used, success, timestamp }`
- `GET /ws` → WebSocket that broadcasts every log line (`[Jarvis] ...`) live to connected clients
- CORS is enabled so the Vite dev server (5173) can talk to the backend (8000)
- Interactive prompts (e.g. YouTube video picker) auto-resolve to the first/default option so the API never blocks

---

### Why This Architecture Is Better 🔧

The old JARVIS used 5+ different API providers simultaneously, each requiring its own key, separate SDK, rate limit tracking, and independent failure handling.

The new version is cleaner:

| Old Setup | New Setup |
|---|---|
| 5+ API keys across different dashboards | Zero API keys — all through Ollama |
| Each provider = separate SDK | Single Ollama interface for everything |
| Online-only | Cloud proxy + 3 offline local fallbacks |
| Manual provider switching | Automatic priority chain via `ollama_router.py` |
| All fail = broken | All fail = retry loop + recovery attempt |

Same intelligence. Zero key management. Works without internet.


---

### Tested Command Suite ✅

JARVIS was validated against a **100-command test suite** covering:
- App control (20 tests)
- Hinglish commands (10 tests)
- Volume control (12 tests)
- Browser and URL control (10 tests)
- YouTube search and auto-play (8 tests)
- Spotify web control (7 tests)
- YouTube media control (5 tests)
- Memory system (10 tests)
- AI brain conversation, code, math, web search (12 tests)
- Stress and edge cases (6 tests)

Current score: **Production-ready for personal use** ✅

---

### What's Coming Next 🚀

This is where things get serious. JARVIS is designed to grow — and the next phases turn it from a terminal assistant into something that genuinely feels like a human handling tasks.

---

**Phase 2 — Remote Control via Phone 📱**

Control JARVIS from anywhere using your phone. Running a command from another city and watching your PC execute it. This will use a lightweight WebSocket server with a simple phone UI — no app install needed, just a browser.

---

**Phase 3 — WhatsApp & Instagram Messaging 💬**

JARVIS will be able to send messages on your behalf.
`send whatsapp message to Mom: coming home at 8`
`reply to instagram DM from john: okay sounds good`
Planned using Playwright with logged-in browser sessions.

---

**Phase 4 — PDF Reading + Voice (TTS) 📖🔊**

Drop a PDF and ask JARVIS to read it, summarize it, or answer questions from it.
Text-to-speech so JARVIS actually speaks the answer back — no more reading the terminal.
Voice input is also on the roadmap so you can speak commands naturally.

---

**Phase 5 — Human-Like Task Execution 🧠**

The end goal. JARVIS should handle multi-step real-world tasks the way a human assistant would:
- `book a cab` → opens Ola/Uber, fills details, confirms
- `check my last 5 emails and summarize` → reads Gmail, gives digest
- `download this research paper and give me key points` → downloads PDF, reads, summarizes

Not clicking buttons blindly — actually understanding context, recovering from errors, and asking when unclear.

---

### Why I Built This 💡

Most AI assistants either need expensive subscriptions, don't work offline, only do one thing, or feel robotic and generic.

JARVIS is built different:
- Entirely from **free tools**
- Runs **on your own machine**
- Works **offline** with local Ollama models
- Understands the way **Indians actually talk** (Hinglish)
- Designed to feel less like a product and more like **your own assistant** that you shaped yourself

Every feature in here was built, broken, debugged, and rebuilt through real testing. There are no shortcuts in this codebase.

---

### Contribute or Suggest 🤝

This repo is public for a reason — feedback, bug reports, and feature suggestions are welcome.

If you find a command that breaks, a case that isn't handled, or have an idea for the roadmap — open an issue or drop a comment here.

The goal is to keep building until `open my laptop, do my work, and tell me when it's done` is a real command JARVIS can handle.

---

*Built by Samarth Maheshwari — Indore, India 🇮🇳*
*Python 3.13 | Windows 11 | Zero Budget | Built from scratch*
