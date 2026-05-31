# ------------------------- #
# Don't Remove Credit 
# Ask Doubt @AU_Bot_Discussion 
# Owner @Mr_Mohammed_29 
# ------------------------- #

import sqlite3
import threading
from config import DB_NAME

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cur = conn.cursor()

# ------------------------- #
# TABLES
# ------------------------- #

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS stickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    file_id TEXT,
    unique_id TEXT
)
""")

conn.commit()

# ------------------------- #
# THREAD SAFE LOCK 
# ------------------------- #

db_lock = threading.Lock()

def safe_execute(query, params=()):
    """Thread-safe DB execution (prevents crashes on Render)"""
    with db_lock:
        cur.execute(query, params)
        conn.commit()

# ------------------------- #
# USER FUNCTIONS
# ------------------------- #

def add_user(uid):
    safe_execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))

def add_sticker(uid, file_id, unique_id):
    safe_execute(
        "INSERT INTO stickers (user_id, file_id, unique_id) VALUES (?, ?, ?)",
        (uid, file_id, unique_id)
    )

# ------------------------- #
# STATS
# ------------------------- #

def get_stats():
    with db_lock:
        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM stickers")
        stickers = cur.fetchone()[0]

    return users, stickers

# ------------------------- #
# ALL USERS (FIXED FOR BROADCAST)
# ------------------------- #

def get_all_users():
    with db_lock:
        cur.execute("SELECT user_id FROM users")
        return cur.fetchall()

# ------------------------- #
# SAFE EXTRA WRAPPERS (OPTIONAL)
# ------------------------- #

def add_user_safe(uid):
    safe_execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))

def add_sticker_safe(uid, file_id, unique_id):
    safe_execute(
        "INSERT INTO stickers (user_id, file_id, unique_id) VALUES (?, ?, ?)",
        (uid, file_id, unique_id)
    )

# ------------------------- #
# Don't Remove Credit 
# Ask Doubt @AU_Bot_Discussion 
# Owner @Mr_Mohammed_29 
# ------------------------- #
