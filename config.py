"""
Application configuration for AI Human Voice Conversation.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "audio" / "generated"
TEMP_DIR  = BASE_DIR / "audio" / "temp"
DATA_DIR  = BASE_DIR / "data"
DB_PATH   = DATA_DIR / "app.db"

# Ensure directories exist
for _d in (AUDIO_DIR, TEMP_DIR, DATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── Application ────────────────────────────────────────────────────────
APP_NAME    = "AI Human Voice Conversation"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1100x780"

# ── Audio ──────────────────────────────────────────────────────────────
SUPPORTED_FORMATS  = ["mp3", "wav"]
DEFAULT_FORMAT     = "mp3"
MAX_CHUNK_SIZE     = 1800          # characters per TTS request
DEFAULT_SPEED      = 1.0           # 0.5 – 2.0 multiplier
DEFAULT_PITCH      = "+0Hz"

# ── TTS ────────────────────────────────────────────────────────────────
TTS_PROVIDER       = "edge_tts"    # swap to "elevenlabs" | "openai" | "coqui"
DEFAULT_LANGUAGE   = "English"
DEFAULT_VOICE      = "en-US-JennyNeural"

# ── Logging ────────────────────────────────────────────────────────────
LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# ── Optional API keys (loaded from .env) ──────────────────────────────
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")
