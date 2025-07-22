import sqlite3

def get_db_connection():
    conn = sqlite3.connect('telemeet.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
        """, ("telegram_token", ""))
        conn.execute("""
            INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
        """, ("meet_url", ""))
        conn.execute("""
            INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
        """, ("youtube_url", ""))
    conn.close()

def get_config(key):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
    conn.close()
    return result['value'] if result else None

def set_config(key, value):
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE config SET value = ? WHERE key = ?", (value, key))
    conn.close()
