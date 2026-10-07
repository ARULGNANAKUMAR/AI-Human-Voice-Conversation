"""
SQLite database layer — stores audio history metadata.
"""
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional

from config import DB_PATH
from models.audio_record import AudioRecord

logger = logging.getLogger(__name__)


class Database:
    """Thin wrapper around SQLite for audio history."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    # ── Internal ──────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        ddl = """
        CREATE TABLE IF NOT EXISTS audio_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT    NOT NULL,
            filepath    TEXT    NOT NULL,
            text        TEXT    DEFAULT '',
            voice       TEXT    DEFAULT '',
            language    TEXT    DEFAULT '',
            speed       REAL    DEFAULT 1.0,
            duration    REAL    DEFAULT 0.0,
            format      TEXT    DEFAULT 'mp3',
            created_at  TEXT    NOT NULL
        );
        """
        try:
            with self._connect() as conn:
                conn.execute(ddl)
                conn.commit()
            logger.info("Database initialised at %s", self.db_path)
        except sqlite3.Error as exc:
            logger.error("Failed to initialise database: %s", exc)
            raise

    # ── Public API ────────────────────────────────────────────────────

    def insert_record(self, record: AudioRecord) -> int:
        """Insert a new audio record and return its row id."""
        sql = """
        INSERT INTO audio_history
            (filename, filepath, text, voice, language, speed, duration, format, created_at)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._connect() as conn:
                cur = conn.execute(sql, (
                    record.filename,
                    record.filepath,
                    record.text[:500],   # cap stored text
                    record.voice,
                    record.language,
                    record.speed,
                    record.duration,
                    record.format,
                    record.created_at,
                ))
                conn.commit()
                new_id = cur.lastrowid
                logger.info("Inserted audio record id=%s", new_id)
                return new_id
        except sqlite3.Error as exc:
            logger.error("insert_record failed: %s", exc)
            raise

    def get_all_records(self) -> List[AudioRecord]:
        """Return all records, newest first."""
        sql = "SELECT * FROM audio_history ORDER BY id DESC"
        try:
            with self._connect() as conn:
                rows = conn.execute(sql).fetchall()
            return [self._row_to_record(r) for r in rows]
        except sqlite3.Error as exc:
            logger.error("get_all_records failed: %s", exc)
            return []

    def get_record(self, record_id: int) -> Optional[AudioRecord]:
        """Return a single record by id."""
        sql = "SELECT * FROM audio_history WHERE id = ?"
        try:
            with self._connect() as conn:
                row = conn.execute(sql, (record_id,)).fetchone()
            return self._row_to_record(row) if row else None
        except sqlite3.Error as exc:
            logger.error("get_record failed: %s", exc)
            return None

    def delete_record(self, record_id: int) -> bool:
        """Delete a record by id."""
        sql = "DELETE FROM audio_history WHERE id = ?"
        try:
            with self._connect() as conn:
                conn.execute(sql, (record_id,))
                conn.commit()
            logger.info("Deleted record id=%s", record_id)
            return True
        except sqlite3.Error as exc:
            logger.error("delete_record failed: %s", exc)
            return False

    def update_duration(self, record_id: int, duration: float) -> None:
        """Update the duration of an existing record."""
        sql = "UPDATE audio_history SET duration = ? WHERE id = ?"
        try:
            with self._connect() as conn:
                conn.execute(sql, (duration, record_id))
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("update_duration failed: %s", exc)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> AudioRecord:
        return AudioRecord(
            id         = row["id"],
            filename   = row["filename"],
            filepath   = row["filepath"],
            text       = row["text"],
            voice      = row["voice"],
            language   = row["language"],
            speed      = row["speed"],
            duration   = row["duration"],
            format     = row["format"],
            created_at = row["created_at"],
        )
