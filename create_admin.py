import sqlite3
import datetime

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    created_at TEXT,
    last_login TEXT
)
""")

conn.execute(
    "INSERT OR IGNORE INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
    ("admin", "admin123", "admin", str(datetime.datetime.now()))
)

conn.commit()
conn.close()

print("Admin created")