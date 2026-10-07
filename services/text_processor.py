"""
TextProcessor — splits long text into TTS-safe chunks.

Strategy:
  1. Split by paragraph (double newline).
  2. If a paragraph exceeds MAX_CHUNK_SIZE, split by sentence.
  3. If a sentence still exceeds the limit, hard-split by characters.
"""
import re
import logging
from typing import List

from config import MAX_CHUNK_SIZE

logger = logging.getLogger(__name__)


class TextProcessor:
    """Prepares raw text for the TTS engine."""

    def __init__(self, max_chunk_size: int = MAX_CHUNK_SIZE) -> None:
        self.max_chunk_size = max_chunk_size

    # ── Public ────────────────────────────────────────────────────────

    def prepare(self, text: str) -> List[str]:
        """
        Clean and split text into a list of chunks safe for the TTS engine.
        Each chunk is at most `max_chunk_size` characters.
        """
        text = self._clean(text)
        paragraphs = self._split_paragraphs(text)
        chunks: List[str] = []
        for para in paragraphs:
            chunks.extend(self._chunk_paragraph(para))
        logger.debug("TextProcessor produced %d chunk(s)", len(chunks))
        return [c for c in chunks if c.strip()]

    # ── Internal ──────────────────────────────────────────────────────

    @staticmethod
    def _clean(text: str) -> str:
        """Normalise whitespace while preserving paragraph breaks."""
        # Collapse 3+ blank lines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse runs of spaces/tabs on a single line
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    @staticmethod
    def _split_paragraphs(text: str) -> List[str]:
        """Split by blank lines."""
        return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    def _chunk_paragraph(self, paragraph: str) -> List[str]:
        """Split a single paragraph into ≤ max_chunk_size chunks."""
        if len(paragraph) <= self.max_chunk_size:
            return [paragraph]

        sentences = self._split_sentences(paragraph)
        chunks: List[str] = []
        current = ""

        for sentence in sentences:
            if not sentence.strip():
                continue
            candidate = (current + " " + sentence).strip() if current else sentence
            if len(candidate) <= self.max_chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # Sentence itself might be too long
                if len(sentence) > self.max_chunk_size:
                    chunks.extend(self._hard_split(sentence))
                    current = ""
                else:
                    current = sentence

        if current:
            chunks.append(current)

        return chunks

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences using punctuation boundaries."""
        # Keep delimiter attached to the preceding word
        parts = re.split(r"(?<=[.!?…])\s+", text)
        return parts

    def _hard_split(self, text: str) -> List[str]:
        """Last-resort split by character count at word boundaries."""
        chunks: List[str] = []
        words = text.split()
        current = ""
        for word in words:
            candidate = (current + " " + word).strip() if current else word
            if len(candidate) <= self.max_chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = word
        if current:
            chunks.append(current)
        return chunks
