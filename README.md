# Jarvis-Mark-1
 the updated version of Jarvis-MK-1


**Jarvis-Mark-1** is the updated version of Jarvis-MK-1: a Windows desktop voice
assistant ("Friday") with a **PyQt5 animated GUI**, **wake-word + speech recognition**,
**streaming LLM chat** (8 swappable model backends), **offline neural TTS**,
and **PC-automation tools** (open apps, play media, alarms, screenshots, code
execution, web search, and more).

> ⚠️ **Windows-only** — paths, `.bat` launchers, `AppOpener`, `pyautogui`
> automation and the bundled ADB platform-tools all assume Windows.

---

## ✨ Features

- 🖥️ **Animated PyQt5 GUI** (`Frontend/GUI.py`) — Jarvis GIF avatar, live chat view,
  mic/assistant status indicators, window controls
- 🎙️ **Speech recognition, 3 engines** — `speechrecogwhisper.py` (faster-whisper
  `tiny`, mic input), `SpeechRecog.py` / `SpeechRecoggui.py` (headless-Chrome
  Web Speech API via Selenium, GUI variant streams text to screen)
- 🗣️ **Streaming offline TTS** (`CommonFunctions/kspeak.py`) — Kokoro `KPipeline`
  → persistent `sounddevice` stream; sentence-level queue, clap-to-interrupt
  (`clap_detection`), hot-word events, stop flags
- 🔊 **Alt cloud TTS** (`CommonFunctions/elevenlabs.py`) — ElevenLabs streaming voice
- 🧠 **8 swappable LLM backends** (`Models/`) — groq (default), openrouter,
  openrouterrq, deepseekr1, cablyai, llamauc, typegpt, zukijourney; groq backend
  keeps a persistent `Data/ChatLog.json` conversation log
- 🛠️ **25+ PC tools** (`CommonFunctions/tools.py`, wildcard-imported) — web search
  (Gemini-grounded + classic), open/close apps & tabs, YouTube/song playback +
  download, weather, currency/temperature conversion, jokes/quotes/definitions,
  screenshots, QR codes, passwords, IP lookup, system info, file search, OCR,
  web scraping, timers, code execution, self-modifying `create_new_tool` /
  `delete_tool`
- ⏰ **Alarms, calls, device control** (`Functions/`) — alarm setter, phone-call
  helper, Android ADB connection setup (bundled `platform-tools/`), browser-use
  stub, text-file reader, system-info reporter
- ⚡ **Fast startup** (`main.py`) — TTS, STT and chat backends import concurrently
  in threads; two entry points: `main.py` (CLI loop) and `Jarvis.py` (GUI loop)

## 🏗️ Architecture

```
Mic ──► SpeechRecog (whisper-tiny / chrome-web-speech) ──► text query
                                                              │
filter_queries() routes "open/close/play/system/…" ──► tools.py / Functions/
                                                              │ else

```
├── Jarvis.py                  # GUI entry point (mic thread + PyQt5 loop, Groq chat)
├── main.py                    # CLI entry point (voice loop + tool routing + chat)
├── API_keys.py                # 🔑 ALL keys + persona (AI name/gender, user profile)
├── Run_Jarvis.bat / Setup_Jarvis.bat   # Windows launch / setup shortcuts
├── Models/                    # LLM backends: groq*, openrouter*, deepseekr1,
│                              #   cablyai, llamauc, typegpt, zukijourney
├── CommonFunctions/
│   ├── kspeak.py              # Kokoro streaming TTS + clap interrupt + hot-word
│   ├── speechrecogwhisper.py  # faster-whisper mic STT
│   ├── SpeechRecog.py / SpeechRecoggui.py  # Chrome Web-Speech STT (CLI / GUI)
│   ├── elevenlabs.py          # ElevenLabs cloud TTS alt
│   ├── Player.py              # YouTube play + video/song download
│   ├── tools.py               # 25+ automation/utility tools (star-imported)
│   └── WebsiteInfo.py         # reads Brave history DB for context
├── Functions/                 # alarms, calls, ADB android setup, search, reader, sysinfo
├── Frontend/                  # PyQt5 GUI + graphics (Jarvis.gif) + status/data files
├── Resources/                 # notification sounds + audio assets
└── transparent-semaphore-1fv6h2/agent.py   # standalone agent experiment

---

## 🚀 Getting Started

### Prerequisites

- **Windows** 10/11, Python 3.10+ (3.11 recommended)
- Microphone + speakers
- API key(s) for whichever `Models/` backend you use (default: Groq)

### Installation

```bat
Setup_Jarvis.bat
```
which runs `pip install -r requirements.txt --upgrade`. (There is currently no
`requirements.txt` in the repo — install the key packages manually:)

```bat
pip install PyQt5 faster-whisper kokoro sounddevice pygame openai groq ^
  selenium webdriver-manager SpeechRecognition colorama pywhatkit ^
  pyautogui AppOpener pytube keyboard pyperclip google-genai ^
  beautifulsoup4 html2text qrcode pydub python-dotenv requests
```

plus `kokoro` model assets and Chrome (for the Selenium STT engines).

### Configuration

Fill in **`API_keys.py`** — keys + persona in one place:

```python
groq = 'gsk_...'            # default chat backend (Models/groq.py)
Gemini_api_key = '...'      # grounded web search (tools.py)
GoogleCustomSearch = '...'  # classic search fallback (Functions/GoogleSearch.py)
cx = '...'                  # custom-search engine id

## 📖 Usage

- Click the **mic button** (or enable the mic) and speak — status cycles
  `Listening … → Thinking … →` spoken + on-screen answer.
- **Clap to interrupt** long answers; say tool-style commands for instant actions:
  `open/close <app>`, `play <song> on youtube`, `google search <q>`,
  `set alarm/timer …`, `take screenshot`, `system info`, …
- Everything else streams from the LLM sentence-by-sentence through Kokoro TTS.
- Switch backends by changing the `Chat` import (`Models/groq.py` default).

## 🛠️ Tech Stack

- **UI:** PyQt5 · **STT:** faster-whisper, SpeechRecognition, Selenium + Chrome
- **TTS:** Kokoro (KPipeline), sounddevice, pygame (alt: ElevenLabs)
- **LLM:** Groq / OpenRouter / DeepSeek / Gemini-grounded search via OpenAI-compatible clients
- **Automation:** pywhatkit, pyautogui, AppOpener, pytube, ADB platform-tools

## ⚠️ Notes

- No `requirements.txt` / `.gitignore` yet — consider adding both (plus removing
  `API_keys.py` secrets, `Resources/The Box.wav` ~35 MB, and the committed
  `platform-tools/` binaries to slim the 52 MB repo).
- `Run_Jarvis.bat` has a hardcoded absolute path (`C:\Users\ASUS\…`) — edit it
  to your checkout or just run `python Jarvis.py`.
- The Groq system prompt asks for uncensored output — review before sharing/demoing.

## 📄 License

MIT — free to use and modify.


AI_Name = 'Friday'          # assistant name, gender, country…
User_Name = 'Suyash'        # …and your profile (used in prompts)
```

> 🔒 `API_keys.py` holds **live secrets** — keep it out of public commits
> (move to env vars / git-ignore it).

### Run

```bat
Run_Jarvis.bat
```
i.e. `python Jarvis.py` (GUI). Or headless CLI: `python main.py`, or type
instead of speaking with `run(chatmode=True)`.

```

                                                              ▼
Models/*.py (groq default, OpenAI-compatible) ──► streamed sentences ──► text_queue
                                                                               │
                                                    kspeak.py (Kokoro TTS) ◄───┘
                                                                               ▼
                                                    sounddevice stream + PyQt5 GUI updates
```

### Project structure

# 🤖 Jarvis-Mark-1 — Desktop AI Voice Assistant (Friday)
