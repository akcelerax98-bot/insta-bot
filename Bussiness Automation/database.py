import sqlite3
import datetime
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacted_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            profile_url TEXT,
            date_contacted TEXT,
            message_status TEXT,
            has_replied INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_contacted_account(username, profile_url, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_contacted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute('''
            INSERT INTO contacted_accounts (username, profile_url, date_contacted, message_status)
            VALUES (?, ?, ?, ?)
        ''', (username, profile_url, date_contacted, status))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Account already exists
    finally:
        conn.close()

def is_account_contacted(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM contacted_accounts WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_replied(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE contacted_accounts SET has_replied = 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def has_replied(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT has_replied FROM contacted_accounts WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0] == 1
    return False
