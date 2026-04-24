import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, Tuple, List

def init_db():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    
    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        points INTEGER DEFAULT 1,
        join_verified BOOLEAN DEFAULT 0,
        join_verified_at TIMESTAMP,
        total_referrals INTEGER DEFAULT 0,
        total_used_points INTEGER DEFAULT 0,
        redeemed_codes TEXT DEFAULT '[]'
    )""")
    
    # Gift codes table
    c.execute("""CREATE TABLE IF NOT EXISTS gift_codes (
        code TEXT PRIMARY KEY,
        points INTEGER,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0,
        expires_at TIMESTAMP,
        created_by INTEGER
    )""")
    
    # Code redemptions table
    c.execute("""CREATE TABLE IF NOT EXISTS code_redemptions (
        code TEXT,
        user_id INTEGER,
        redeemed_at TIMESTAMP,
        FOREIGN KEY (code) REFERENCES gift_codes(code)
    )""")
    
    # Required channels table (NEW)
    c.execute("""CREATE TABLE IF NOT EXISTS required_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_username TEXT UNIQUE,
        channel_type TEXT DEFAULT 'public',
        added_by INTEGER,
        added_at TIMESTAMP
    )""")
    
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Dict:
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "first_name": row[1],
            "username": row[2],
            "points": row[3],
            "join_verified": row[4],
            "join_verified_at": row[5],
            "total_referrals": row[6],
            "total_used_points": row[7],
            "redeemed_codes": json.loads(row[8]),
        }
    return None

def create_user(user_id: int, first_name: str, username: str):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (user_id, first_name, username, points) VALUES (?, ?, ?, ?)",
        (user_id, first_name, username, DEFAULT_POINTS),
    )
    conn.commit()
    conn.close()

def update_user_points(user_id: int, points_change: int):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points_change, user_id))
    if points_change < 0:
        c.execute("UPDATE users SET total_used_points = total_used_points + ? WHERE user_id = ?", (-points_change, user_id))
    conn.commit()
    conn.close()

def update_join_verification(user_id: int):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET join_verified = 1, join_verified_at = ? WHERE user_id = ?", (datetime.now(), user_id))
    conn.commit()
    conn.close()

def add_referral(user_id: int):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("UPDATE users SET total_referrals = total_referrals + 1 WHERE user_id = ?", (user_id,))
    c.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Channel management functions (NEW)
def get_all_channels():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT channel_username, channel_type FROM required_channels ORDER BY id")
    channels = c.fetchall()
    conn.close()
    return channels

def add_channel(channel_username: str, channel_type: str, added_by: int) -> bool:
    try:
        conn = sqlite3.connect("bot_data.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO required_channels (channel_username, channel_type, added_by, added_at) VALUES (?, ?, ?, ?)",
            (channel_username, channel_type, added_by, datetime.now())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_channel(channel_username: str) -> bool:
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("DELETE FROM required_channels WHERE channel_username = ?", (channel_username,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def clear_all_channels():
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("DELETE FROM required_channels")
    conn.commit()
    conn.close()
