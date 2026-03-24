import sqlite3
from datetime import datetime
import uuid
from typing import Optional, List
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            source TEXT NOT NULL,
            marks INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chat_sessions(id)
        )
    """)

    conn.commit()
    conn.close()


def create_chat_session(user_id: str, title: str) -> str:
    """Create a new chat session and return its ID."""
    chat_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (id, user_id, title, created_at) VALUES (?, ?, ?, ?)",
        (chat_id, user_id, title, created_at)
    )
    conn.commit()
    conn.close()

    return chat_id


def save_message(
    chat_id: str,
    user_id: str,
    query: str,
    response: str,
    source: str,
    marks: int = 0
) -> str:
    """Save a message to the database and return its ID."""
    message_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (id, chat_id, user_id, query, response, source, marks, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (message_id, chat_id, user_id, query, response, source, marks, timestamp)
    )

    cursor.execute(
        "UPDATE chat_sessions SET title = ? WHERE id = ? AND title = 'New Chat'",
        (query[:50] + "..." if len(query) > 50 else query, chat_id)
    )

    conn.commit()
    conn.close()

    return message_id


def get_chat_session(chat_id: str) -> Optional[dict]:
    """Get a chat session by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, title, created_at FROM chat_sessions WHERE id = ?",
        (chat_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_chat_messages(chat_id: str) -> List[dict]:
    """Get all messages for a chat session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, user_id, query, response, source, marks, timestamp FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
        (chat_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_chat_sessions(user_id: str) -> List[dict]:
    """Get all chat sessions for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, title, created_at FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_chat_session(chat_id: str) -> bool:
    """Delete a chat session and all its messages."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True
