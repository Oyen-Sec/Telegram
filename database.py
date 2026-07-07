import sqlite3
import json
import time
import os
import config

def get_connection():
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            source_group TEXT,
            status TEXT DEFAULT 'pending',
            error_reason TEXT,
            timestamp INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_counter (
            date TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_member(user_id, username, first_name, last_name, source_group):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO progress (user_id, username, first_name, last_name, source_group, status, timestamp)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (user_id, username or "", first_name or "", last_name or "", source_group, int(time.time())))
    conn.commit()
    conn.close()

def member_exists(user_id):
    conn = get_connection()
    cur = conn.execute("SELECT 1 FROM progress WHERE user_id = ?", (user_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def get_total_unique():
    conn = get_connection()
    cur = conn.execute("SELECT COUNT(*) FROM progress")
    total = cur.fetchone()[0]
    conn.close()
    return total

def get_pending_members(limit=None):
    conn = get_connection()
    if limit:
        cur = conn.execute("SELECT * FROM progress WHERE status = 'pending' ORDER BY timestamp ASC LIMIT ?", (limit,))
    else:
        cur = conn.execute("SELECT * FROM progress WHERE status = 'pending' ORDER BY timestamp ASC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def update_member_status(user_id, status, error_reason=None):
    conn = get_connection()
    conn.execute("""
        UPDATE progress SET status = ?, error_reason = ?, timestamp = ? WHERE user_id = ?
    """, (status, error_reason, int(time.time()), user_id))
    conn.commit()
    conn.close()

def get_daily_add_count():
    today = time.strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.execute("SELECT count FROM daily_counter WHERE date = ?", (today,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def increment_daily_counter():
    today = time.strftime("%Y-%m-%d")
    conn = get_connection()
    conn.execute("""
        INSERT INTO daily_counter (date, count) VALUES (?, 1)
        ON CONFLICT(date) DO UPDATE SET count = count + 1
    """, (today,))
    conn.commit()
    conn.close()

def save_checkpoint(data):
    with open(config.CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)

def load_checkpoint():
    if not os.path.exists(config.CHECKPOINT_FILE):
        return None
    with open(config.CHECKPOINT_FILE, "r") as f:
        return json.load(f)

def clear_checkpoint():
    if os.path.exists(config.CHECKPOINT_FILE):
        os.remove(config.CHECKPOINT_FILE)

def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
    added = conn.execute("SELECT COUNT(*) FROM progress WHERE status = 'added'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM progress WHERE status = 'failed'").fetchone()[0]
    skipped = conn.execute("SELECT COUNT(*) FROM progress WHERE status = 'skipped'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM progress WHERE status = 'pending'").fetchone()[0]
    conn.close()
    return {"total": total, "added": added, "failed": failed, "skipped": skipped, "pending": pending}
