import sqlite3
from datetime import datetime
import uuid
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")


def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_tables():
    """Initialize users table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def create_user(username: str, email: str, password: str, phone: str = "") -> str:
    """Create a new user and return their ID."""
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)
    created_at = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (id, username, email, password_hash, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, email, password_hash, phone, created_at)
        )
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Username or email already exists")
    finally:
        conn.close()


def get_user_by_username_or_email(username_or_email: str) -> Optional[dict]:
    """Get user by username or email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?",
        (username_or_email, username_or_email)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def user_exists(username: str, email: str) -> bool:
    """Check if user exists by username or email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT 1 FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    
    return exists
