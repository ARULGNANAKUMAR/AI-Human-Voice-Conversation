"""
Data model for an audio record stored in history.
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class AudioRecord:
    """Represents one generated audio file entry."""
    id:         int      = 0
    filename:   str      = ""
    filepath:   str      = ""
    text:       str      = ""
    voice:      str      = ""
    language:   str      = ""
    speed:      float    = 1.0
    duration:   float    = 0.0      # seconds
    format:     str      = "mp3"
    created_at: str      = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    @property
    def duration_str(self) -> str:
        """Return duration as MM:SS string."""
        m, s = divmod(int(self.duration), 60)
        return f"{m:02d}:{s:02d}"

    @property
    def created_at_display(self) -> str:
        """Return a human-friendly date string."""
        try:
            dt = datetime.strptime(self.created_at, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d %b %Y  %H:%M")
        except ValueError:
            return self.created_at

    @property
    def exists(self) -> bool:
        return Path(self.filepath).exists()
