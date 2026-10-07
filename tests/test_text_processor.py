"""Tests for TextProcessor."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.text_processor import TextProcessor


@pytest.fixture
def proc():
    return TextProcessor(max_chunk_size=200)


def test_empty_returns_empty(proc):
    assert proc.prepare("") == []


def test_whitespace_only_returns_empty(proc):
    assert proc.prepare("   \n  ") == []


def test_short_text_single_chunk(proc):
    result = proc.prepare("Hello world.")
    assert result == ["Hello world."]


def test_long_text_splits_into_chunks(proc):
    long = ("This is a sentence. " * 20).strip()
    chunks = proc.prepare(long)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 200


def test_paragraph_splitting(proc):
    text = "Paragraph one.\n\nParagraph two."
    chunks = proc.prepare(text)
    assert len(chunks) == 2


def test_preserves_content(proc):
    text = "Hello everyone. Welcome to the demo."
    chunks = proc.prepare(text)
    combined = " ".join(chunks)
    assert "Hello everyone" in combined
    assert "Welcome to the demo" in combined


def test_triple_newline_normalised(proc):
    text = "Line one.\n\n\n\nLine two."
    chunks = proc.prepare(text)
    assert len(chunks) == 2


def test_no_empty_chunks(proc):
    text = "First.\n\n\n\nSecond.\n\n\n"
    chunks = proc.prepare(text)
    assert all(c.strip() for c in chunks)
