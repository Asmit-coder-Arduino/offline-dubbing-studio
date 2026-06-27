"""
History manager — record and retrieve past dubbing projects.
"""

import os
from datetime import datetime
from typing import List, Dict, Optional


class HistoryManager:
    """Manages the dubbing project history stored in SQLite."""

    def _db(self):
        from database.db_manager import DatabaseManager
        mgr = DatabaseManager()
        if not mgr.db_path:
            mgr.initialize()
        return mgr

    def add_entry(self, entry: Dict) -> int:
        """
        Record a completed dubbing job.

        Args:
            entry: dict with keys: input, output, source_lang, target_lang, segments.

        Returns:
            The row ID of the inserted record.
        """
        db = self._db()
        cur = db.execute(
            """
            INSERT INTO history (input_path, output_path, source_lang, target_lang, segments)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry.get("input", ""),
                entry.get("output", ""),
                entry.get("source_lang", ""),
                entry.get("target_lang", ""),
                entry.get("segments", 0),
            ),
        )
        return cur.lastrowid

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Return the most recent history entries."""
        rows = self._db().query(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [self._format_row(r) for r in rows]

    def get_all(self) -> List[Dict]:
        """Return all history entries, oldest first."""
        rows = self._db().query("SELECT * FROM history ORDER BY created_at ASC")
        return [self._format_row(r) for r in rows]

    def get_by_id(self, record_id: int) -> Optional[Dict]:
        """Return a single history entry by its ID."""
        row = self._db().query_one("SELECT * FROM history WHERE id = ?", (record_id,))
        return self._format_row(row) if row else None

    def delete_entry(self, record_id: int):
        """Delete a single history entry by ID."""
        self._db().execute("DELETE FROM history WHERE id = ?", (record_id,))

    def clear_all(self):
        """Delete all history entries."""
        self._db().execute("DELETE FROM history")

    def count(self) -> int:
        """Return the total number of history entries."""
        row = self._db().query_one("SELECT COUNT(*) as n FROM history")
        return row["n"] if row else 0

    @staticmethod
    def _format_row(row: Dict) -> Dict:
        """Normalize a database row into the format expected by the UI."""
        return {
            "id": row.get("id"),
            "input": row.get("input_path", ""),
            "output": row.get("output_path", ""),
            "source_lang": row.get("source_lang", ""),
            "target_lang": row.get("target_lang", ""),
            "segments": row.get("segments", 0),
            "date": row.get("created_at", "")[:10],
            "status": row.get("status", "completed"),
        }
