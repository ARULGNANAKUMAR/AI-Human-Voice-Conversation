"""
AudioService — merges audio chunks and controls playback via pygame.
"""
import logging
import shutil
import threading
from pathlib import Path
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


class AudioService:
    """Handles audio combining and playback."""

    def __init__(self) -> None:
        self._pygame_ready = False
        self._current_path: Optional[Path] = None
        self._lock = threading.Lock()
        self._init_pygame()

    # ── Init ──────────────────────────────────────────────────────────

    def _init_pygame(self) -> None:
        try:
            import pygame  # type: ignore
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            self._pygame_ready = True
            logger.info("pygame mixer initialised")
        except Exception as exc:
            logger.warning("pygame init failed (%s) — playback unavailable", exc)
            self._pygame_ready = False

    # ── Chunk combining ───────────────────────────────────────────────

    def combine_chunks(
        self,
        chunk_paths: List[Path],
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Path:
        """
        Concatenate MP3 chunk files into a single output file.
        Uses pydub if available for clean concat; falls back to raw byte copy.
        """
        if len(chunk_paths) == 1:
            shutil.copy2(str(chunk_paths[0]), str(output_path))
            return output_path

        try:
            from pydub import AudioSegment  # type: ignore
            return self._combine_with_pydub(chunk_paths, output_path, progress_callback)
        except ImportError:
            logger.warning("pydub not available — using raw byte concatenation")
            return self._combine_raw(chunk_paths, output_path)

    def _combine_with_pydub(
        self,
        chunk_paths: List[Path],
        output_path: Path,
        progress_callback,
    ) -> Path:
        from pydub import AudioSegment  # type: ignore

        combined = AudioSegment.empty()
        total = len(chunk_paths)
        silence = AudioSegment.silent(duration=300)   # 300 ms between chunks

        for i, path in enumerate(chunk_paths):
            seg = AudioSegment.from_mp3(str(path))
            combined += seg
            if i < total - 1:
                combined += silence
            if progress_callback:
                progress_callback(int((i + 1) / total * 100))

        fmt = output_path.suffix.lstrip(".")
        combined.export(str(output_path), format=fmt)
        logger.info("Combined %d chunks → %s", total, output_path)
        return output_path

    @staticmethod
    def _combine_raw(chunk_paths: List[Path], output_path: Path) -> Path:
        """Byte-level MP3 concatenation (works but no silence between chunks)."""
        with open(output_path, "wb") as out_f:
            for path in chunk_paths:
                with open(path, "rb") as in_f:
                    out_f.write(in_f.read())
        logger.info("Raw-combined %d chunks → %s", len(chunk_paths), output_path)
        return output_path

    def convert_to_wav(self, src: Path, dest: Path) -> Path:
        """Convert an MP3 file to WAV."""
        try:
            from pydub import AudioSegment  # type: ignore
            seg = AudioSegment.from_mp3(str(src))
            seg.export(str(dest), format="wav")
            logger.info("Converted to WAV → %s", dest)
            return dest
        except ImportError:
            raise RuntimeError(
                "pydub is required for WAV conversion. Run: pip install pydub"
            )

    # ── Playback ──────────────────────────────────────────────────────

    def play(self, path: Path) -> bool:
        """Start playing an audio file. Returns True on success."""
        if not self._pygame_ready:
            logger.error("pygame not initialised — cannot play audio")
            return False
        try:
            import pygame  # type: ignore
            with self._lock:
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.play()
                self._current_path = path
            logger.info("Playback started: %s", path)
            return True
        except Exception as exc:
            logger.error("Playback failed: %s", exc)
            return False

    def pause(self) -> None:
        if not self._pygame_ready:
            return
        import pygame  # type: ignore
        pygame.mixer.music.pause()
        logger.debug("Playback paused")

    def resume(self) -> None:
        if not self._pygame_ready:
            return
        import pygame  # type: ignore
        pygame.mixer.music.unpause()
        logger.debug("Playback resumed")

    def stop(self) -> None:
        if not self._pygame_ready:
            return
        import pygame  # type: ignore
        pygame.mixer.music.stop()
        logger.debug("Playback stopped")

    def is_playing(self) -> bool:
        if not self._pygame_ready:
            return False
        import pygame  # type: ignore
        return bool(pygame.mixer.music.get_busy())

    def get_position_ms(self) -> int:
        """Return playback position in milliseconds."""
        if not self._pygame_ready:
            return 0
        import pygame  # type: ignore
        return pygame.mixer.music.get_pos()

    def set_volume(self, volume: float) -> None:
        """Set volume 0.0–1.0."""
        if not self._pygame_ready:
            return
        import pygame  # type: ignore
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    def cleanup(self) -> None:
        """Release pygame resources."""
        if self._pygame_ready:
            import pygame  # type: ignore
            pygame.mixer.quit()
            logger.info("pygame mixer released")
