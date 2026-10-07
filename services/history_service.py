"""
HistoryService — business-logic layer over the Database for audio history.
"""
import logging
from pathlib import Path
from typing import List

from database.database import Database
from models.audio_record import AudioRecord
from utils.file_utils import delete_file, get_audio_duration

logger = logging.getLogger(__name__)


class HistoryService:
    """Manages the audio history (CRUD + file deletion)."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ── Public ────────────────────────────────────────────────────────

    def add(self, record: AudioRecord) -> AudioRecord:
        """Persist a new record; returns it with its assigned id."""
        record.duration = get_audio_duration(record.filepath)
        record.id = self._db.insert_record(record)
        logger.info("History entry added: id=%s  file=%s", record.id, record.filename)
        return record

    def all_records(self) -> List[AudioRecord]:
        """Return all history entries, newest first."""
        return self._db.get_all_records()

    def delete(self, record_id: int, delete_file_too: bool = True) -> bool:
        """
        Remove a history entry from the database.
        Optionally also delete the audio file from disk.
        """
        record = self._db.get_record(record_id)
        if record is None:
            logger.warning("delete: record %s not found", record_id)
            return False

        if delete_file_too and record.filepath:
            delete_file(record.filepath)

        return self._db.delete_record(record_id)

    def refresh_duration(self, record: AudioRecord) -> float:
        """Re-read duration from disk and update the database."""
        dur = get_audio_duration(record.filepath)
        self._db.update_duration(record.id, dur)
        record.duration = dur
        return dur
