"""
Settings manager — persistent key-value settings stored in SQLite.
Falls back to an in-memory dict if the database is not yet initialized.
"""

import json
import os
from typing import Any, Dict


DEFAULTS: Dict[str, Any] = {
    "theme": "dark",
    "whisper_model": "base.en",
    "piper_model": "en_US-amy-medium",
    "video_bitrate": "4000k",
    "audio_bitrate": "192k",
    "audio_quality": "192k",
    "cpu_threads": 4,
    "subtitle_style": "default",
    "gpu_enabled": False,
    "language": "en",
    "export_quality": "high",
    "normalize_audio": True,
    "remove_silence": False,
    "keep_background_music": True,
}


class SettingsManager:
    """Reads and writes application settings via the shared database."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._use_db = True

    def _db(self):
        try:
            from database.db_manager import DatabaseManager
            mgr = DatabaseManager()
            if not mgr.db_path:
                mgr.initialize()
            return mgr
        except Exception:
            self._use_db = False
            return None

    def load(self) -> Dict[str, Any]:
        """Return all settings, merging database values over defaults."""
        result = dict(DEFAULTS)
        if self._use_db:
            db = self._db()
            if db:
                rows = db.query("SELECT key, value FROM settings")
                for row in rows:
                    key = row["key"]
                    raw = row["value"]
                    try:
                        result[key] = json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = raw
        result.update(self._cache)
        return result

    def save(self, settings: Dict[str, Any]):
        """Persist a settings dict, updating only the keys provided."""
        self._cache.update(settings)
        if self._use_db:
            db = self._db()
            if db:
                for key, value in settings.items():
                    db.execute(
                        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                        (key, json.dumps(value)),
                    )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a single setting value."""
        all_settings = self.load()
        return all_settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a single setting value."""
        self.save({key: value})

    def reset_to_defaults(self):
        """Reset all settings to their default values."""
        if self._use_db:
            db = self._db()
            if db:
                db.execute("DELETE FROM settings")
        self._cache = {}
        self.save(DEFAULTS)
