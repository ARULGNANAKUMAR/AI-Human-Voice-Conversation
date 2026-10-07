"""
File and path helpers.
"""
import shutil
import logging
from datetime import datetime
from pathlib import Path

from config import AUDIO_DIR, TEMP_DIR

logger = logging.getLogger(__name__)


def timestamped_filename(ext: str = "mp3") -> str:
    """Return a unique filename like voice_20260922_183000.mp3."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"voice_{ts}.{ext.lstrip('.')}"


def temp_path(suffix: str = ".mp3") -> Path:
    """Return a path for a temporary file inside TEMP_DIR."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return TEMP_DIR / f"tmp_{ts}{suffix}"


def move_to_generated(src: Path, filename: str) -> Path:
    """Move a temp file to the generated audio directory."""
    dest = AUDIO_DIR / filename
    shutil.move(str(src), str(dest))
    logger.debug("Moved %s → %s", src, dest)
    return dest


def delete_file(path: str | Path) -> bool:
    """Delete a file safely; return True on success."""
    p = Path(path)
    try:
        if p.exists():
            p.unlink()
            logger.info("Deleted file: %s", p)
            return True
        logger.warning("File not found for deletion: %s", p)
        return False
    except OSError as exc:
        logger.error("Failed to delete %s: %s", p, exc)
        return False


def get_audio_duration(path: str | Path) -> float:
    """
    Return audio duration in seconds.
    Uses mutagen if available, falls back to 0.0.
    """
    try:
        from mutagen import File as MutagenFile  # type: ignore
        f = MutagenFile(str(path))
        if f is not None and f.info is not None:
            return float(f.info.length)
    except Exception:
        pass
    # Fallback: estimate from file size (very rough)
    try:
        size = Path(path).stat().st_size
        return size / 16_000  # ~16 KB/s for 128kbps mp3
    except OSError:
        return 0.0


def ensure_dirs() -> None:
    """Make sure all required directories exist."""
    for d in (AUDIO_DIR, TEMP_DIR):
        d.mkdir(parents=True, exist_ok=True)
