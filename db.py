"""SQLite access for contact form submissions."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""


def get_connection(db_path):
    """Open a SQLite connection to db_path, creating its parent directory if needed."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    """Create the submissions table at db_path if it doesn't already exist."""
    conn = get_connection(db_path)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def insert_submission(db_path, name, email, subject, message):
    """Insert one contact submission; created_at is set by the database default."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO submissions (name, email, subject, message) VALUES (?, ?, ?, ?)",
            (name, email, subject, message),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_all_submissions(db_path):
    """Return all submissions as dicts, newest first."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT id, name, email, subject, message, created_at "
            "FROM submissions ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
