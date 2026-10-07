"""
Input / output validators.
"""
import re
from pathlib import Path


def validate_text(text: str) -> tuple[bool, str]:
    """
    Validate that text is non-empty and within reasonable length.

    Returns (is_valid, error_message).
    """
    stripped = text.strip()
    if not stripped:
        return False, "Please enter some content first."
    if len(stripped) < 2:
        return False, "Text is too short to generate audio."
    if len(stripped) > 50_000:
        return False, "Text is too long (max 50,000 characters)."
    return True, ""


def validate_filepath(path: str) -> tuple[bool, str]:
    """Check that a given file path is non-empty and on a writable volume."""
    if not path:
        return False, "File path is empty."
    p = Path(path)
    if not p.parent.exists():
        return False, f"Directory does not exist: {p.parent}"
    return True, ""


def sanitise_filename(name: str) -> str:
    """Remove characters that are unsafe in filenames."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")
    return name or "audio"
