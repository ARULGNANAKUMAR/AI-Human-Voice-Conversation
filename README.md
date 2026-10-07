# 🎙 AI Human Voice Conversation

A Python desktop application that converts written content into **realistic, human-like neural speech** and lets you listen to, manage, and save the generated audio — all from a clean Tkinter GUI.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Neural TTS** | Microsoft Edge voices — natural intonation, not robotic |
| **400+ voices** | English, Tamil, and more |
| **Desktop GUI** | Modern dark-themed Tkinter interface |
| **Long-text support** | Automatic chunking + seamless audio joining |
| **Playback controls** | Play / Pause / Resume / Stop |
| **Export** | Save as MP3 or WAV |
| **Audio history** | SQLite-backed history with re-play and delete |
| **Speed control** | 0.5× to 2.0× speaking rate |
| **Modular TTS** | Swap the TTS provider without touching the GUI |
| **Thread-safe UI** | Generation never freezes the interface |

---

## 🖼 Interface Overview

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

---

## 🚀 Installation

### 1. Clone / download

```bash
git clone https://github.com/yourname/ai-human-voice.git
cd ai-human-voice
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg (required by pydub for multi-chunk audio merging)

| Platform | Command |
|---|---|
| Windows | Download from https://ffmpeg.org/download.html and add to PATH |
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |

> **Note:** FFmpeg is only needed when generating audio from long texts that require multiple chunks. Single-chunk audio (short texts) works without it.

### 5. Configure environment (optional)

```bash
cp .env.example .env
```

The default TTS engine (`edge-tts`) **does not need any API key**. The `.env` file is only needed if you later switch to ElevenLabs or OpenAI TTS.

### 6. Run

```bash
python main.py
```

---

## 🔊 How to Use

1. **Paste or type** your content into the text area.
2. **Select a language** (English or Tamil).
3. **Choose a voice** from the dropdown.
4. **Adjust the speed** slider if needed.
5. Click **⚡ Generate Voice** — progress is shown.
6. Click **▶ Play** to listen.
7. Click **💾 Save Audio** to export as MP3 or WAV.
8. View past files in **Audio History** — play or delete any entry.

---

## 🏗 Architecture

```
ai_human_voice/
├── main.py                   ← Entry point
├── config.py                 ← All app-wide settings
├── app/
│   ├── gui.py                ← Main Tkinter window
│   ├── theme.py              ← Dark theme / colours
│   └── dialogs.py            ← Save / error / confirm dialogs
├── services/
│   ├── tts_service.py        ← TTS abstraction + edge-tts backend
│   ├── audio_service.py      ← pygame playback + pydub combining
│   ├── text_processor.py     ← Long-text chunking
│   └── history_service.py    ← Business logic over the DB
├── database/
│   └── database.py           ← SQLite CRUD layer
├── models/
│   └── audio_record.py       ← AudioRecord dataclass
├── utils/
│   ├── file_utils.py         ← Path helpers, duration reading
│   └── validators.py         ← Input validation
├── audio/
│   ├── generated/            ← Saved audio files
│   └── temp/                 ← Chunk intermediates (auto-cleaned)
├── data/
│   └── app.db                ← SQLite history database
└── tests/                    ← pytest unit tests
```

### Swapping the TTS provider

Subclass `BaseTTSProvider` in `services/tts_service.py` and pass an instance to `TTSService`:

```python
class MyProvider(BaseTTSProvider):
    def synthesise(self, text, voice, speed, output_path): ...
    def available_voices(self): ...

tts_service = TTSService(provider=MyProvider())
```

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

---

## 🔮 Future-Ready

The architecture is designed for these additions:
- Local offline TTS (Coqui / Piper)
- ElevenLabs / OpenAI TTS backends
- Voice cloning (with user authorisation)
- More languages
- Multi-speaker conversations
- Emotion / style controls
- TXT / PDF / DOCX import
- Audio waveform visualisation
- Cloud storage
- Search in history

---

## 📋 Requirements

- Python 3.10+
- Internet connection (for edge-tts synthesis)
- FFmpeg (for multi-chunk long-text audio)
- See `requirements.txt` for Python packages

---

## 📄 Licence

MIT — free to use and modify.
