"""
Database manager — SQLite setup and shared connection management.
All tables are created here on first run.
"""

import os
import sqlite3
import threading
from typing import Optional


class DatabaseManager:
    """Manages the SQLite database for the application."""

    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._db_path: Optional[str] = None
        self._initialized = False

    def initialize(self, db_dir: Optional[str] = None):
        """Set up the database and create tables if they don't exist."""
        if self._initialized:
            return
        with DatabaseManager._lock:
            if self._initialized:
                return
            if db_dir is None:
                from kivy.app import App
                try:
                    app = App.get_running_app()
                    db_dir = app.get_app_dir()
                except Exception:
                    db_dir = os.path.expanduser("~")

            os.makedirs(db_dir, exist_ok=True)
            self._db_path = os.path.join(db_dir, "dubbing_studio.db")
            self._create_tables()
            self._initialized = True

    def _create_tables(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_path  TEXT NOT NULL,
                    output_path TEXT,
                    source_lang TEXT,
                    target_lang TEXT,
                    segments    INTEGER DEFAULT 0,
                    created_at  TEXT DEFAULT (datetime('now')),
                    status      TEXT DEFAULT 'completed'
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS batch_jobs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_name    TEXT,
                    created_at  TEXT DEFAULT (datetime('now')),
                    status      TEXT DEFAULT 'queued',
                    total       INTEGER DEFAULT 0,
                    completed   INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS batch_items (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id      INTEGER REFERENCES batch_jobs(id),
                    input_path  TEXT,
                    output_path TEXT,
                    status      TEXT DEFAULT 'queued',
                    error       TEXT
                );
            """)

    def _connect(self) -> sqlite3.Connection:
        if not self._db_path:
            raise RuntimeError("DatabaseManager.initialize() must be called first.")
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, sql: str, params=()) -> sqlite3.Cursor:
        """Execute a write query and return the cursor."""
        with DatabaseManager._lock:
            with self._connect() as conn:
                cur = conn.execute(sql, params)
                conn.commit()
                return cur

    def query(self, sql: str, params=()) -> list:
        """Execute a read query and return all rows as dicts."""
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def query_one(self, sql: str, params=()) -> Optional[dict]:
        """Execute a read query and return the first row as a dict, or None."""
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    @property
    def db_path(self) -> Optional[str]:
        return self._db_path
