"""Tests for AudioService (non-hardware paths)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from utils.file_utils import timestamped_filename, temp_path


def test_timestamped_filename_mp3():
    name = timestamped_filename("mp3")
    assert name.startswith("voice_")
    assert name.endswith(".mp3")


def test_timestamped_filename_wav():
    name = timestamped_filename("wav")
    assert name.endswith(".wav")


def test_temp_path_is_in_temp_dir():
    p = temp_path(".mp3")
    from config import TEMP_DIR
    assert str(TEMP_DIR) in str(p)


def test_timestamped_filename_unique():
    import time
    a = timestamped_filename()
    time.sleep(1.01)
    b = timestamped_filename()
    assert a != b
