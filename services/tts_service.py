"""
TTSService — modular TTS abstraction.

Current backend: edge-tts (Microsoft neural voices, free, no API key).
To swap providers, subclass BaseTTSProvider and register it below.
"""
import asyncio
import logging
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Voice catalogue helpers
# ─────────────────────────────────────────────────────────────────────────────

# Curated subset — shown in the GUI dropdown.
# Keys: language label   Values: list of (display_name, edge_voice_name)
VOICE_CATALOGUE = {
    "English": [
        ("Jenny  — Female, Conversational",     "en-US-JennyNeural"),
        ("Aria   — Female, Natural",             "en-US-AriaNeural"),
        ("Guy    — Male, Natural",               "en-US-GuyNeural"),
        ("Davis  — Male, Conversational",        "en-US-DavisNeural"),
        ("Jane   — Female, Cheerful",            "en-US-JaneNeural"),
        ("Tony   — Male, Confident",             "en-US-TonyNeural"),
        ("Sonia  — Female, UK, Natural",         "en-GB-SoniaNeural"),
        ("Ryan   — Male, UK, Natural",           "en-GB-RyanNeural"),
        ("Neerja — Female, India, Natural",      "en-IN-NeerjaNeural"),
        ("Prabhat— Male, India, Natural",        "en-IN-PrabhatNeural"),
    ],
    "Tamil": [
        ("Pallavi— Female, Natural",             "ta-IN-PallaviNeural"),
        ("Valluvar—Male, Natural",               "ta-IN-ValluvarNeural"),
        ("Saranya— Female, LK, Natural",         "ta-LK-SaranyaNeural"),
        ("Kumar  — Male, LK, Natural",           "ta-LK-KumarNeural"),
    ],
}

# Reverse lookup: voice_name → display_name
_VOICE_DISPLAY: dict[str, str] = {}
for _voices in VOICE_CATALOGUE.values():
    for _display, _name in _voices:
        _VOICE_DISPLAY[_name] = _display


def get_voices_for_language(language: str) -> List[tuple[str, str]]:
    """Return [(display_name, voice_id), …] for the given language."""
    return VOICE_CATALOGUE.get(language, [])


def voice_display_name(voice_id: str) -> str:
    return _VOICE_DISPLAY.get(voice_id, voice_id)


# ─────────────────────────────────────────────────────────────────────────────
# Abstract provider
# ─────────────────────────────────────────────────────────────────────────────

class BaseTTSProvider(ABC):
    """Interface that every TTS backend must satisfy."""

    @abstractmethod
    def synthesise(
        self,
        text: str,
        voice: str,
        speed: float,
        output_path: Path,
    ) -> None:
        """Generate speech for *text* and write it to *output_path*."""

    @abstractmethod
    def available_voices(self) -> List[str]:
        """Return a list of voice IDs this provider supports."""


# ─────────────────────────────────────────────────────────────────────────────
# edge-tts provider
# ─────────────────────────────────────────────────────────────────────────────

class EdgeTTSProvider(BaseTTSProvider):
    """
    Microsoft Edge neural TTS via the `edge-tts` package.
    Free — no API key required. Requires an internet connection.
    """

    # edge-tts expresses rate as a percentage delta string, e.g. "+10%" or "-20%"
    @staticmethod
    def _rate_string(speed: float) -> str:
        # speed=1.0 → "+0%", speed=1.5 → "+50%", speed=0.75 → "-25%"
        pct = round((speed - 1.0) * 100)
        return f"+{pct}%" if pct >= 0 else f"{pct}%"

    def synthesise(
        self,
        text: str,
        voice: str,
        speed: float,
        output_path: Path,
    ) -> None:
        """Run edge-tts synchronously (wraps the async API)."""
        asyncio.run(self._async_synthesise(text, voice, speed, output_path))

    async def _async_synthesise(
        self,
        text: str,
        voice: str,
        speed: float,
        output_path: Path,
    ) -> None:
        try:
            import edge_tts  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "edge-tts is not installed. Run: pip install edge-tts"
            ) from exc

        rate = self._rate_string(speed)
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(str(output_path))
        logger.debug("edge-tts saved → %s", output_path)

    def available_voices(self) -> List[str]:
        all_voices = []
        for voices in VOICE_CATALOGUE.values():
            all_voices.extend(v for _, v in voices)
        return all_voices


# ─────────────────────────────────────────────────────────────────────────────
# Main TTSService
# ─────────────────────────────────────────────────────────────────────────────

class TTSService:
    """
    High-level TTS service used by the GUI.

    Delegates to a concrete provider; handles chunk stitching.
    """

    def __init__(self, provider: Optional[BaseTTSProvider] = None) -> None:
        self._provider: BaseTTSProvider = provider or EdgeTTSProvider()

    # ── Public ────────────────────────────────────────────────────────

    def synthesise_chunks(
        self,
        chunks: List[str],
        voice: str,
        speed: float,
        progress_callback=None,   # callable(int percent)
    ) -> List[Path]:
        """
        Generate one MP3 file per chunk.
        Returns a list of temporary file paths.
        """
        from utils.file_utils import temp_path

        paths: List[Path] = []
        total = len(chunks)

        for i, chunk in enumerate(chunks):
            out = temp_path(suffix=".mp3")
            logger.info("Synthesising chunk %d/%d (%d chars)", i + 1, total, len(chunk))
            self._provider.synthesise(chunk, voice, speed, out)
            paths.append(out)
            if progress_callback:
                pct = int((i + 1) / total * 100)
                progress_callback(pct)

        return paths

    def available_voices(self) -> List[str]:
        return self._provider.available_voices()

    def swap_provider(self, provider: BaseTTSProvider) -> None:
        """Hot-swap the TTS backend without restarting."""
        self._provider = provider
        logger.info("TTS provider swapped to %s", type(provider).__name__)
