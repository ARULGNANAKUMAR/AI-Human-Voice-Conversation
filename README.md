# 🎙 AI Human Voice Conversation

> A Python desktop application that converts written content into **realistic, human-like neural speech** — with playback, export, and history management — all inside a clean, dark-themed Tkinter GUI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Licence](https://img.shields.io/badge/Licence-MIT-green)
![TTS](https://img.shields.io/badge/TTS-edge--tts-purple)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Interface Preview](#-interface-preview)
- [Screenshots / Layout](#-screenshots--layout)
- [Requirements](#-requirements)
- [Installation](#-installation)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Create a virtual environment](#2-create-a-virtual-environment)
  - [3. Install Python dependencies](#3-install-python-dependencies)
  - [4. Install FFmpeg](#4-install-ffmpeg-required-for-multi-chunk-audio-merging)
  - [5. Configure environment (optional)](#5-configure-environment-optional)
  - [6. Run the application](#6-run-the-application)
- [How to Use](#-how-to-use)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Configuration Reference](#-configuration-reference)
- [Supported Voices](#-supported-voices)
- [Extending the Application](#-extending-the-application)
  - [Swapping the TTS Provider](#swapping-the-tts-provider)
  - [Adding a New Language](#adding-a-new-language)
  - [Adding a New Voice](#adding-a-new-voice)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Roadmap / Future-Ready](#-roadmap--future-ready)
- [Performance Notes](#-performance-notes)
- [Contributing](#-contributing)
- [Licence](#-licence)
- [Acknowledgements](#-acknowledgements)

---

## 🧭 Overview

**AI Human Voice Conversation** is a cross-platform desktop tool that turns text into natural-sounding speech using **Microsoft Edge's neural TTS engine** (via the free `edge-tts` Python package). It's designed for anyone who needs quick, high-quality voice generation without paying for cloud APIs — writers, students, content creators, developers building voice demos, or accessibility users.

The application is **modular by design**: the TTS backend is abstracted behind a provider interface, so swapping to ElevenLabs, OpenAI TTS, Coqui, or Piper later requires zero changes to the GUI.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🗣 **Neural TTS** | Microsoft Edge voices — natural intonation, not robotic |
| 🌍 **Multiple voices** | 400+ available; 14 curated in the GUI (English US/UK/India + Tamil) |
| 🖥 **Desktop GUI** | Modern dark-themed Tkinter interface (Catppuccin-inspired palette) |
| 📜 **Long-text support** | Automatic chunking + seamless audio joining (with 300 ms pauses) |
| ▶️ **Playback controls** | Play / Pause / Resume / Stop via `pygame.mixer` |
| 💾 **Export** | Save as MP3 or WAV |
| 🕓 **Audio history** | SQLite-backed history with re-play, re-save, and delete |
| ⚡ **Speed control** | 0.5× to 2.0× speaking rate (maps to edge-tts `rate` percentages) |
| 🎭 **Style selection** | Conversational, Newscast, Cheerful, Calm, Empathetic, Excited |
| 🔌 **Modular TTS** | Swap the TTS provider without touching the GUI |
| 🧵 **Thread-safe UI** | Generation runs in a daemon thread; UI stays responsive |
| 🧪 **Tested** | Pytest unit tests for text processing, validators, and file utils |
| 🔐 **No API keys needed** | edge-tts is free and keyless (optional keys supported for future providers) |

---

## 🖼 Interface Preview

```
┌─────────────────────────────────────────────────┬──────────────────┐
│  🎙 AI Human Voice Conversation                 │  Audio History   │
├─────────────────────────────────────────────────│                  │
│  CONTENT                                        │  🔊 voice_001.mp3│
│  ┌───────────────────────────────────────────┐  │  22 Sep 2026     │
│  │ Paste or type your text here…             │  │  [▶ Play][🗑]    │
│  │                                           │  │──────────────────│
│  └───────────────────────────────────────────┘  │  🔊 voice_002.mp3│
│  Characters: 0                        [Clear]   │  …               │
├─────────────────────────────────────────────────│                  │
│  VOICE SETTINGS                                 │                  │
│  Language: [English ▼]  Voice: [Jenny ▼]        │                  │
│  Speed: 0.5× ────●──────────── 2.0×   1.0×     │                  │
│  Style: [Conversational ▼]                      │                  │
├─────────────────────────────────────────────────│                  │
│  [⚡ Generate] [▶ Play] [⏸ Pause] [⏹ Stop] [💾]│                  │
│  ████████████████░░░░  Generating voice… 80%    │                  │
└─────────────────────────────────────────────────┴──────────────────┘
```

### Colour Palette

| Role | Colour | Hex |
|---|---|---|
| Main background | Deep navy | `#1e1e2e` |
| Card / panel | Muted purple | `#2a2a3e` |
| Text input area | Near black | `#13131f` |
| Accent (buttons) | Purple-blue | `#7c6af7` |
| Success | Green | `#50fa7b` |
| Warning | Yellow | `#f1fa8c` |
| Error | Red | `#ff5555` |
| Foreground | Off-white | `#cdd6f4` |
| Dim text | Grey | `#6c7086` |
| Heading | Pink | `#f5c2e7` |

---

## 🧰 Requirements

### System

- **Python 3.10 or newer**
- **Internet connection** (required for edge-tts synthesis — it streams from Microsoft servers)
- **FFmpeg** (required only for merging multi-chunk audio — see [Installation step 4](#4-install-ffmpeg-required-for-multi-chunk-audio-merging))
- **Audio output device** (speakers/headphones) for playback

### Python packages (installed via `requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| `edge-tts` | ≥6.1.9 | Microsoft Edge neural TTS engine |
| `pydub` | ≥0.25.1 | Audio segment manipulation + MP3/WAV export |
| `pygame` | ≥2.5.0 | Audio playback (mixer) |
| `mutagen` | ≥1.47.0 | Read audio file duration and metadata |
| `python-dotenv` | ≥1.0.0 | Load `.env` files |
| `pytest` | ≥7.4.0 | Testing framework |

### Operating System

- **Windows 10/11** (primary target — logs show Windows paths)
- **macOS 11+** (works; install FFmpeg via Homebrew)
- **Linux** (works; install FFmpeg via apt/dnf)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourname/ai-human-voice.git
cd ai-human-voice
```

Or download and extract the ZIP, then `cd` into the folder.

---

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

Or upgrade pip first if you hit issues:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Install FFmpeg (required for multi-chunk audio merging)

FFmpeg is used by `pydub` to **decode and merge multiple MP3 chunks** into one file. Without it, any text long enough to be split into more than one chunk will fail with:

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

| Platform | Command |
|---|---|
| **Windows** | Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) → extract → add the `bin/` folder to your `PATH` environment variable. Verify with `ffmpeg -version` in a new terminal. |
| **macOS** | `brew install ffmpeg` |
| **Ubuntu / Debian** | `sudo apt update && sudo apt install ffmpeg` |
| **Fedora** | `sudo dnf install ffmpeg` |
| **Arch** | `sudo pacman -S ffmpeg` |

> **Note:** FFmpeg is only needed when generating audio from **long texts that require multiple chunks**. Short text (single chunk) works without FFmpeg.

**Alternative:** you can point pydub directly at the binary without modifying `PATH`:

```python
from pydub import AudioSegment
AudioSegment.converter = r"C:\path\to\ffmpeg.exe"
```

Or set the environment variable `FFMPEG_BINARY` before importing pydub.

---

### 5. Configure environment (optional)

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` if you plan to use a cloud TTS provider later. The default `edge-tts` engine **does not need any API key**.

```env
# ElevenLabs (optional — for future voice cloning)
ELEVENLABS_API_KEY=

# OpenAI TTS (optional — for gpt-4o-audio or tts-1)
OPENAI_API_KEY=
```

---

### 6. Run the application

```bash
python main.py
```

You should see the app window open, and log output like:

```
2026-09-24 10:08:59,452 [INFO] __main__: Starting AI Human Voice Conversation v1.0.0
2026-09-24 10:08:59,780 [INFO] database.database: Database initialised at ...\data\app.db
2026-09-24 10:09:02,526 [INFO] services.audio_service: pygame mixer initialised
```

---

## 🎧 How to Use

1. **Paste or type** your content into the large text area.
2. *(Optional)* Click **Clear** to reset the text box.
3. **Select a language** from the dropdown (English or Tamil).
4. **Choose a voice** from the voice dropdown — display names include gender and character.
5. **Adjust the speed** slider between `0.5×` and `2.0×`.
6. *(Optional)* Pick a **style** (Conversational, Newscast, etc.).
7. Click **⚡ Generate Voice** — a progress bar tracks synthesis and merging.
8. Once complete, click **▶ Play** to listen.
9. Use **⏸ Pause** / **⏹ Stop** as needed.
10. Click **💾 Save Audio** to export as MP3 or WAV.
11. View past generations in **Audio History** — click **▶ Play** to replay or **🗑 Delete** to remove both the DB entry and the file on disk.

> **Tip:** Generation runs in a background thread, so you can keep interacting with the UI (e.g. scroll history) while audio is being synthesised.

---

## 📁 Project Structure

```
ai_human_voice/
├── main.py                     ← Entry point: logging, service init, GUI launch
├── config.py                   ← All app-wide settings (paths, defaults, API keys)
├── requirements.txt            ← Python dependencies
├── README.md                   ← This file
├── .env.example                ← Template for optional API keys
├── app.log                     ← Runtime log (auto-generated)
│
├── app/
│   ├── __init__.py             ← Exports VoiceApp
│   ├── gui.py                  ← Main Tkinter window (largest module)
│   ├── theme.py                ← Dark theme colours + ttk.Style config
│   └── dialogs.py              ← Save / error / confirm dialog helpers
│
├── services/
│   ├── __init__.py
│   ├── tts_service.py          ← TTS abstraction + EdgeTTSProvider
│   ├── audio_service.py        ← pygame playback + pydub chunk merging
│   ├── text_processor.py       ← Long-text chunking logic
│   └── history_service.py      ← Business logic over the DB
│
├── database/
│   ├── __init__.py
│   └── database.py             ← SQLite CRUD layer
│
├── models/
│   ├── __init__.py
│   └── audio_record.py         ← AudioRecord dataclass
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py           ← Path helpers, duration reading, filename generation
│   └── validators.py           ← Input validation + filename sanitisation
│
├── audio/
│   ├── generated/              ← Saved audio files (voice_YYYYMMDD_HHMMSS.mp3)
│   └── temp/                   ← Chunk intermediates (auto-cleaned)
│
├── data/
│   └── app.db                  ← SQLite history database
│
└── tests/
    ├── __init__.py
    ├── test_audio_service.py   ← Filename / temp-path generation tests
    ├── test_text_processor.py  ← Chunking tests
    └── test_validators.py      ← Input validation tests
```

---

## 🏛 Architecture

The app follows a **layered architecture** with a strict one-way dependency flow:

```
┌───────────────────────────────────────────────┐
│  main.py  →  logging + service init + GUI     │
└───────────────────────────────────────────────┘
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼
  services/       database/         app/
  (business)      (persistence)     (view)
     │
     ├── tts_service.py     → edge-tts wrapper (swappable)
     ├── audio_service.py   → pygame playback + pydub merging
     ├── text_processor.py  → chunking long text
     └── history_service.py → CRUD over the DB
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Worker thread + `queue.Queue`** | Tkinter is single-threaded; the queue decouples background work from UI updates. Polled every 100 ms via `self.after()`. |
| **`BaseTTSProvider` abstraction** | Swap edge-tts → ElevenLabs/OpenAI/Coqui without touching GUI code. |
| **Chunked synthesis** | Bypasses per-request character limits and allows granular progress reporting. |
| **`temp_path()` with microseconds** | Avoids filename collisions when many chunks are created rapidly. |
| **Dependency injection** | Services are constructed in `main.py` and passed into `VoiceApp` — easier to test and swap. |
| **SQLite** | Zero-config persistence — no server to run. |
| **Optional API keys** | edge-tts needs none; cloud providers are strictly opt-in. |

### Generation Flow

```
User clicks "Generate"
        │
        ▼
_on_generate()  → validate text → disable buttons → start daemon thread
        │
        ▼
_worker_generate()
        ├── TextProcessor.prepare()         → List[str] chunks
        ├── TTSService.synthesise_chunks()  → List[Path] temp MP3s
        ├── AudioService.combine_chunks()   → single MP3
        ├── HistoryService.add()            → DB row + duration
        └── put (DONE, (path, record)) on queue
        │
        ▼
_poll_queue()  → re-enable buttons, add history card, show "✔ Complete"
```

---

## ⚙ Configuration Reference

All defaults live in `config.py`. Edit them directly to change behaviour.

| Setting | Default | Description |
|---|---|---|
| `BASE_DIR` | *(auto)* | Project root |
| `AUDIO_DIR` | `audio/generated` | Where saved MP3s go |
| `TEMP_DIR` | `audio/temp` | Where chunk intermediates go |
| `DATA_DIR` | `data` | Where the SQLite DB lives |
| `DB_PATH` | `data/app.db` | Full path to the SQLite file |
| `APP_NAME` | `AI Human Voice Conversation` | Window title |
| `APP_VERSION` | `1.0.0` | Version string |
| `WINDOW_SIZE` | `1100x780` | Default window dimensions |
| `SUPPORTED_FORMATS` | `["mp3", "wav"]` | Export formats |
| `DEFAULT_FORMAT` | `mp3` | Default export format |
| `MAX_CHUNK_SIZE` | `1800` | Max characters per TTS request |
| `DEFAULT_SPEED` | `1.0` | Default speaking rate (0.5–2.0) |
| `DEFAULT_PITCH` | `+0Hz` | Reserved for future pitch control |
| `TTS_PROVIDER` | `edge_tts` | Active provider (`elevenlabs`/`openai`/`coqui` reserved) |
| `DEFAULT_LANGUAGE` | `English` | Default dropdown selection |
| `DEFAULT_VOICE` | `en-US-JennyNeural` | Default voice ID |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `LOG_FORMAT` | `%(asctime)s ...` | Log line format |
| `ELEVENLABS_API_KEY` | `""` | Optional — loaded from `.env` |
| `OPENAI_API_KEY` | `""` | Optional — loaded from `.env` |

---

## 🗣 Supported Voices

The GUI exposes a **curated subset** (14 voices) so the dropdown stays manageable. All voices below come from `VOICE_CATALOGUE` in `services/tts_service.py`.

### English

| Display name | Voice ID | Character |
|---|---|---|
| Jenny | `en-US-JennyNeural` | Female, Conversational (US) |
| Aria | `en-US-AriaNeural` | Female, Natural (US) |
| Guy | `en-US-GuyNeural` | Male, Natural (US) |
| Davis | `en-US-DavisNeural` | Male, Conversational (US) |
| Jane | `en-US-JaneNeural` | Female, Cheerful (US) |
| Tony | `en-US-TonyNeural` | Male, Confident (US) |
| Sonia | `en-GB-SoniaNeural` | Female, Natural (UK) |
| Ryan | `en-GB-RyanNeural` | Male, Natural (UK) |
| Neerja | `en-IN-NeerjaNeural` | Female, Natural (India) |
| Prabhat | `en-IN-PrabhatNeural` | Male, Natural (India) |

### Tamil

| Display name | Voice ID | Character |
|---|---|---|
| Pallavi | `ta-IN-PallaviNeural` | Female, Natural (India) |
| Valluvar | `ta-IN-ValluvarNeural` | Male, Natural (India) |
| Saranya | `ta-LK-SaranyaNeural` | Female, Natural (Sri Lanka) |
| Kumar | `ta-LK-KumarNeural` | Male, Natural (Sri Lanka) |

> **Want more voices?** edge-tts exposes 400+ voices. Run `edge-tts --list-voices` from the command line to see them all, then add entries to `VOICE_CATALOGUE`.

---

## 🔧 Extending the Application

### Swapping the TTS Provider

Subclass `BaseTTSProvider` and pass an instance to `TTSService`:

```python
from pathlib import Path
from services.tts_service import BaseTTSProvider, TTSService

class MyProvider(BaseTTSProvider):
    def synthesise(
        self,
        text: str,
        voice: str,
        speed: float,
        output_path: Path,
    ) -> None:
        # Call your API here and write audio bytes to output_path
        ...

    def available_voices(self) -> list[str]:
        return ["my-voice-1", "my-voice-2"]

# Usage
tts_service = TTSService(provider=MyProvider())
```

Or hot-swap at runtime:

```python
tts_service.swap_provider(MyProvider())
```

**Example: OpenAI TTS provider**

```python
from openai import OpenAI
from pathlib import Path
from services.tts_service import BaseTTSProvider

class OpenAITTSProvider(BaseTTSProvider):
    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key)

    def synthesise(self, text, voice, speed, output_path):
        response = self._client.audio.speech.create(
            model="tts-1",
            voice=voice or "alloy",
            input=text,
            speed=speed,
        )
        response.stream_to_file(output_path)

    def available_voices(self):
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
```

**Example: ElevenLabs provider**

```python
from elevenlabs.client import ElevenLabs
from services.tts_service import BaseTTSProvider

class ElevenLabsProvider(BaseTTSProvider):
    def __init__(self, api_key: str):
        self._client = ElevenLabs(api_key=api_key)

    def synthesise(self, text, voice, speed, output_path):
        audio = self._client.generate(
            text=text,
            voice=voice or "Rachel",
            model="eleven_multilingual_v2",
        )
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

    def available_voices(self):
        return [v.name for v in self._client.voices.get_all().voices]
```

---

### Adding a New Language

Edit `VOICE_CATALOGUE` in `services/tts_service.py`:

```python
VOICE_CATALOGUE = {
    "English": [ ... ],
    "Tamil":   [ ... ],
    "Hindi": [
        ("Swara  — Female, Natural", "hi-IN-SwaraNeural"),
        ("Madhur — Male, Natural",   "hi-IN-MadhurNeural"),
    ],
}
```

No other changes are needed — the GUI reads this dict dynamically.

---

### Adding a New Voice

Append a tuple to the appropriate language list:

```python
("Emily  — Female, Calm", "en-US-EmilyNeural"),
```

The first element is the display name shown in the dropdown; the second is the edge-tts voice ID.

---

## 🧪 Testing

Run the full test suite:

```bash
python -m pytest tests/ -v
```

Run a specific test file:

```bash
python -m pytest tests/test_text_processor.py -v
```

Run with coverage (requires `pytest-cov`):

```bash
pip install pytest-cov
python -m pytest tests/ --cov=services --cov=utils --cov-report=html
```

### What's tested

| Test file | Coverage |
|---|---|
| `test_text_processor.py` | Empty input, whitespace-only, paragraph splitting, chunk size limits, content preservation, newline normalisation |
| `test_validators.py` | Empty/whitespace text, length limits, filename sanitisation (slashes, colons, empty fallback) |
| `test_audio_service.py` | Timestamped filename generation, temp path location, uniqueness |

### What's not tested (yet)

- GUI rendering (would need `pytest-tk` or manual testing)
- Actual TTS synthesis (requires network)
- Audio merging (requires FFmpeg + real MP3s)
- Database CRUD (planned)

---

## 🛠 Troubleshooting

### ❌ `FileNotFoundError: [WinError 2] The system cannot find the file specified`

**Cause:** pydub cannot find FFmpeg. This happens during the **combine chunks** step when the text is long enough to be split into multiple chunks.

**Fix:** Install FFmpeg and ensure it's on your `PATH`.

```bash
# Verify
ffmpeg -version
```

If `ffmpeg` isn't recognised, add its `bin/` folder to your system `PATH` and **restart your terminal** (and IDE). On Windows, you may need to log out and back in.

**Workaround without FFmpeg:** Keep your text short (< 1800 characters) so only one chunk is generated. Single-chunk audio is copied directly without pydub.

**Alternative fix:** Set the binary path explicitly in `services/audio_service.py`:

```python
from pydub import AudioSegment
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe   = r"C:\ffmpeg\bin\ffprobe.exe"
```

---

### ❌ `pygame.error: mixer not initialized` or no sound on playback

**Cause:** No audio output device, or pygame's mixer failed to initialise.

**Fixes:**
- Check that speakers/headphones are connected and not muted.
- On Linux, ensure ALSA/PulseAudio is running.
- Look for `pygame init failed` in `app.log` — the app degrades gracefully (generation still works, playback doesn't).

---

### ❌ `edge-tts` fails with a connection error

**Cause:** No internet, firewall blocking, or Microsoft's servers are temporarily unavailable.

**Fixes:**
- Verify internet connectivity.
- Try a different network (some corporate firewalls block `speech.platform.bing.com`).
- Retry after a few minutes — edge-tts depends on a live Microsoft endpoint.

---

### ❌ `ModuleNotFoundError: No module named 'edge_tts'`

**Cause:** Dependencies not installed or the wrong virtual environment is active.

**Fix:**

```bash
pip install -r requirements.txt
```

Confirm you're in the venv: `(venv)` should appear in your prompt. On Windows: `venv\Scripts\activate`.

---

### ❌ WAV export fails

**Cause:** pydub requires FFmpeg for MP3→WAV conversion.

**Fix:** Install FFmpeg (see above).

---

### ❌ Generation stuck at 0% or 85%

**Cause:** Network stall during synthesis, or FFmpeg hanging during merge.

**Fixes:**
- Check `app.log` for the last logged line.
- Kill and restart the app.
- Verify FFmpeg works standalone: `ffmpeg -i input.mp3 output.wav`.

---

### ❌ History entries point to missing files

**Cause:** Files were manually deleted from `audio/generated/`.

**Fix:** Delete the stale entry from the GUI (🗑 Delete). The app filters missing files when loading history on startup, but stale entries created *during* a session may still appear.

---

### 📄 Where are the logs?

`app.log` in the project root. Increase verbosity by setting `LOG_LEVEL = "DEBUG"` in `config.py`.

---

## ❓ FAQ

**Q: Do I need an API key?**
A: No. The default `edge-tts` engine is free and keyless. API keys are only used if you later swap to ElevenLabs or OpenAI.

**Q: Does it work offline?**
A: No. edge-tts streams from Microsoft's servers, so an internet connection is required for synthesis. Playback of already-generated audio works offline.

**Q: How long can my text be?**
A: Up to 50,000 characters (validated). Long text is automatically split into ~1800-character chunks and merged.

**Q: Why is there a delay between chunks?**
A: A 300 ms silence is inserted between chunks during merging for natural pacing. You can change this in `audio_service.py` (`silence = AudioSegment.silent(duration=300)`).

**Q: Where are generated files stored?**
A: `audio/generated/` — filenames follow `voice_YYYYMMDD_HHMMSS.mp3`.

**Q: Can I clone a voice?**
A: Not yet. The architecture supports adding a cloning provider (e.g. ElevenLabs or Coqui) later, but voice cloning requires the speaker's explicit authorisation.

**Q: Can I run this on a server / headless machine?**
A: The GUI needs a display. For headless use, you'd need to call `TTSService` and `AudioService.combine_chunks()` directly via a script.

**Q: How do I change the theme?**
A: Edit `app/theme.py` — all colours and fonts are defined at the top. The `apply()` function wires them into ttk styles.

**Q: Is the audio history synced anywhere?**
A: No — it's local SQLite (`data/app.db`). Back it up if you care about the history.

**Q: Can I delete the audio history?**
A: Yes. Delete individual entries in the GUI, or delete `data/app.db` (this removes all history but leaves files on disk).

---

## 🔮 Roadmap / Future-Ready

The architecture is designed for these additions:

- [ ] **Local offline TTS** — Coqui TTS / Piper integration
- [ ] **ElevenLabs backend** — voice cloning (with user authorisation)
- [ ] **OpenAI TTS backend** — `gpt-4o-audio` / `tts-1`
- [ ] **More languages** — Hindi, Telugu, Malayalam, Kannada, Bengali, etc.
- [ ] **Multi-speaker conversations** — assign different voices to different speakers
- [ ] **Emotion / style controls** — richer SSML-driven expressiveness
- [ ] **Document import** — TXT / PDF / DOCX
- [ ] **Audio waveform visualisation** — matplotlib or pygame-based
- [ ] **Search in history** — full-text search over stored text
- [ ] **Cloud storage sync** — Google Drive / S3 export
- [ ] **Batch processing** — queue multiple texts for overnight generation
- [ ] **Pitch control** — the `DEFAULT_PITCH` config value is already reserved
- [ ] **Subtitle / SRT export** — timestamps aligned with audio
- [ ] **Streaming playback** — start playing before full generation completes

---

## ⚡ Performance Notes

| Scenario | Approximate time |
|---|---|
| Short text (1 chunk, ~30 chars) | ~2–5 seconds |
| Medium text (5 chunks, ~500 chars) | ~10–15 seconds |
| Long text (14 chunks, ~1500 chars) | ~35–50 seconds |
| Merging 14 chunks with pydub | ~2–4 seconds (once FFmpeg is installed) |

Times depend heavily on network latency to Microsoft's edge-tts endpoint and CPU speed for merging.

**Memory usage:** ~60–100 MB idle; spikes briefly during pydub merging of many chunks.

**Thread safety:** All TTS and merging work runs on a daemon thread. UI updates happen only on the main thread via `queue.Queue`. Playback uses a lock around pygame calls.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`.
3. Make your changes.
4. Add tests for new functionality.
5. Run the test suite: `python -m pytest tests/ -v`.
6. Commit: `git commit -m "Add amazing feature"`.
7. Push: `git push origin feature/amazing-feature`.
8. Open a Pull Request.

### Coding style

- Follow **PEP 8**.
- Use **type hints** for all public functions.
- Keep services free of GUI imports (layered architecture).
- Log meaningful events at `INFO` or `DEBUG`.
- Add docstrings to public classes and methods.

### Reporting bugs

Open an issue with:
- Your OS and Python version.
- The relevant `app.log` excerpt (especially the traceback).
- Steps to reproduce.
- Whether FFmpeg is installed (`ffmpeg -version`).

---

## 📄 Licence

**MIT Licence** — free to use, modify, and distribute. See `LICENSE` for details.

```
Copyright (c) 2026 AI Human Voice Conversation contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgements

- **[edge-tts](https://github.com/rany2/edge-tts)** — Python wrapper around Microsoft Edge's neural TTS engine. This project wouldn't exist without it.
- **[pydub](https://github.com/jiaaro/pydub)** — Elegant audio segment manipulation.
- **[pygame](https://www.pygame.org/)** — Reliable cross-platform audio playback.
- **[mutagen](https://mutagen.readthedocs.io/)** — Audio metadata reading.
- **[FFmpeg](https://ffmpeg.org/)** — The Swiss Army knife of audio/video processing.
- **Catppuccin** — Colour palette inspiration for the dark theme.

---

<div align="center">

If this project helped you, consider giving it a ⭐ on GitHub!

</div>
