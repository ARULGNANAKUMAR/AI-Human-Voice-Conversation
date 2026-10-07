"""Tests for input validators."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from utils.validators import validate_text, sanitise_filename


def test_empty_text_invalid():
    ok, msg = validate_text("")
    assert not ok
    assert msg


def test_whitespace_only_invalid():
    ok, msg = validate_text("   ")
    assert not ok


def test_valid_text():
    ok, msg = validate_text("Hello world.")
    assert ok
    assert msg == ""


def test_too_long_text():
    ok, msg = validate_text("x" * 50_001)
    assert not ok
    assert "too long" in msg.lower()


def test_sanitise_filename_removes_slashes():
    assert "/" not in sanitise_filename("my/file")
    assert "\\" not in sanitise_filename("my\\file")


def test_sanitise_filename_removes_colons():
    result = sanitise_filename("time:12:00")
    assert ":" not in result


def test_sanitise_filename_empty_fallback():
    assert sanitise_filename("") == "audio"
    assert sanitise_filename("...") == "audio"
