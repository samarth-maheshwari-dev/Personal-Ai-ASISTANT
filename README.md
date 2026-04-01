## JARVIS — Personal AI Assistant | Discussion & Roadmap 🤖

---

### What is JARVIS? 🧠

JARVIS is a **Windows 11 terminal-based AI assistant** built from scratch in Python 3.13 — with zero budget, zero paid APIs, and zero shortcuts.

It is not a chatbot wrapper. It is not a voice assistant skin. It is a full system that **thinks, decides, and acts** — controlling your PC like a human would, powered by multiple free AI providers working as one brain.

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

**AI Brain — Multi-Provider 🧩**
- Cerebras → fast responses, file generation
- SambaNova → code, math, complex logic
- Mistral → education, explanations
- NVIDIA Nemotron → heavy reasoning
- OpenRouter → fallback conversation
- Ollama → fully offline fallback
- Auto-routes your query to the best model for that type

**Web Search (Real-Time) 🌐**
- Detects queries needing live data (weather, news, prices, scores)
- Multi-attempt search with result filtering
- Summarized by Cerebras — clean 2-3 line answer, no hallucination dump

**File Creation 📄**
- `create file notes.txt` → AI generates full content
- `create file sort.py and write bubble sort code` → writes working code
- Direct Cerebras API call — raw clean output, no markdown noise
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

**Step 1 — Clone the repo**
```bash
git clone https://github.com/samarth-maheshwari-dev/Personal-Ai-ASISTANT.git
cd Personal-Ai-ASISTANT
```

**Step 2 — Install dependencies**
```bash
pip install pyautogui pygetwindow pywin32 rapidfuzz psutil winrt-runtime winrt-Windows.Media.Control python-dotenv requests yt-dlp ddgs pycaw comtypes
```

**Step 3 — Create your `.env` file**

Create a file named `.env` in the JARVIS folder and add your free API keys:

```env
CEREBRAS_API_KEY=your_key_here
SAMBANOVA_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

All of these are **free tier** — no credit card needed:
- Cerebras → cerebras.ai
- SambaNova → sambanova.ai
- OpenRouter → openrouter.ai
- NVIDIA NIM → build.nvidia.com
- Mistral → console.mistral.ai

**Step 4 — Run**
```bash
python jarvis.py
```

**Optional — Offline Mode**

Install Ollama from ollama.ai and pull:
```bash
ollama pull qwen2.5:3b
```
JARVIS will use this as fallback when internet is unavailable.

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
Control JARVIS from anywhere using your phone. Running a command from another city and watching your PC execute it. This will likely use a lightweight WebSocket server with a simple phone UI — no app install needed, just a browser.

---

**Phase 3 — WhatsApp & Instagram Messaging 💬**
JARVIS will be able to send messages on your behalf.
`send whatsapp message to Mom: coming home at 8`
`reply to instagram DM from john: okay sounds good`
This requires browser automation with logged-in sessions — planned using Playwright.

---

**Phase 4 — PDF Reading + Voice (TTS) 📖🔊**
Drop a PDF and ask JARVIS to read it, summarize it, or answer questions from it.
Text-to-speech so JARVIS actually speaks the answer back — no more reading the terminal. Voice input is also on the roadmap so you can speak commands naturally.

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

JARVIS is built different — entirely from free tools, runs on your own machine, understands the way Indians actually talk (Hinglish), and is designed to feel less like a product and more like your own assistant that you shaped yourself.

Every feature in here was built, broken, debugged, and rebuilt through real testing. There are no shortcuts in this codebase.

---

### Contribute or Suggest 🤝

This repo is public for a reason — feedback, bug reports, and feature suggestions are welcome.

If you find a command that breaks, a case that isn't handled, or have an idea for the roadmap — open an issue or drop a comment here.

The goal is to keep building until `open my laptop, do my work, and tell me when it's done` is a real command JARVIS can handle.

---

*Built by Samarth Maheshwari — Indore, India 🇮🇳*
*Python 3.13 | Windows 11 | Zero Budget | Built from scratch*# Personal-Ai-ASISTANT
