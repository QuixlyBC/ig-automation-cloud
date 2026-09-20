"""
SQLite database for the queue of reels to post.
"""

import sqlite3
import datetime
from typing import List, Dict

import config


def init_db():
    """Create the queue table if it doesn't exist."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            description TEXT,
            status TEXT DEFAULT 'pending',
            video_path TEXT,
            posted_url TEXT,
            error_msg TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            posted_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_reel(url: str, description: str = None) -> Dict:
    """Add a reel URL to the queue with optional custom description."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO queue (url, description, status)
            VALUES (?, ?, 'pending')
        """, (url, description))
        conn.commit()
        item_id = c.lastrowid
        result = {"ok": True, "id": item_id, "url": url}
    except sqlite3.IntegrityError:
        result = {"ok": False, "error": "URL already in queue"}
    finally:
        conn.close()
    return result


def get_pending() -> Dict:
    """Get the next pending reel."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, url, description
        FROM queue
        WHERE status = 'pending'
        ORDER BY created_at
        LIMIT 1
    """)
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "url": row[1], "description": row[2]}


def update_status(item_id: int, status: str, video_path: str = None, posted_url: str = None, error_msg: str = None):
    """Update the status of a queued item."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE queue
        SET status = ?, video_path = ?, posted_url = ?, error_msg = ?, updated_at = CURRENT_TIMESTAMP, posted_at = CASE WHEN ? = 'posted' THEN CURRENT_TIMESTAMP ELSE posted_at END
        WHERE id = ?
    """, (status, video_path, posted_url, error_msg, status, item_id))
    conn.commit()
    conn.close()


def get_all() -> List[Dict]:
    """Get all queue items (for dashboard)."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, url, status, posted_url, error_msg, created_at, posted_at
        FROM queue
        ORDER BY created_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "url": r[1],
            "status": r[2],
            "posted_url": r[3],
            "error": r[4],
            "created_at": r[5],
            "posted_at": r[6],
        }
        for r in rows
    ]


def delete_item(item_id: int):
    """Delete an item from the queue."""
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM queue WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
