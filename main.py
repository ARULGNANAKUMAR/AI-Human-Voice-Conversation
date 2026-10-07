"""
main.py — Entry point for AI Human Voice Conversation.

Responsibilities:
  1. Configure logging.
  2. Ensure required directories exist.
  3. Initialise services.
  4. Launch the Tkinter GUI.
"""
import logging
import sys
from pathlib import Path

# ── Ensure project root is on sys.path ────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from config import APP_NAME, APP_VERSION, LOG_FORMAT, LOG_LEVEL
from utils.file_utils import ensure_dirs


def _setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    _setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    ensure_dirs()

    # ── Initialise services ───────────────────────────────────────────
    from database.database     import Database
    from services.tts_service  import TTSService
    from services.audio_service import AudioService
    from services.history_service import HistoryService

    db              = Database()
    tts_service     = TTSService()
    audio_service   = AudioService()
    history_service = HistoryService(db)

    # ── Launch GUI ────────────────────────────────────────────────────
    from app.gui import VoiceApp

    app = VoiceApp(
        tts_service     = tts_service,
        audio_service   = audio_service,
        history_service = history_service,
    )
    app.mainloop()

    logger.info("Application exited cleanly.")


if __name__ == "__main__":
    main()
