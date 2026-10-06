import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "conversation.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                employee_id TEXT,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                thread_id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (thread_id) REFERENCES chat_sessions(thread_id)
            )
        """)


def save_message(thread_id, employee_id, role, message):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO conversations
            (thread_id, employee_id, role, message, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (thread_id, employee_id, role, message, datetime.now().isoformat()),
        )


def create_chat_session(thread_id, employee_id, title):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chat_sessions (thread_id, employee_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (thread_id, employee_id, title, now, now),
        )


def get_chat_session(thread_id, employee_id):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT thread_id, employee_id, title, created_at, updated_at
            FROM chat_sessions
            WHERE thread_id = ? AND employee_id = ?
            """,
            (thread_id, employee_id),
        ).fetchone()
    if row is None:
        return None
    return {
        "thread_id": row[0],
        "employee_id": row[1],
        "title": row[2],
        "created_at": row[3],
        "updated_at": row[4],
    }


def list_chat_sessions(employee_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT thread_id, employee_id, title, created_at, updated_at
            FROM chat_sessions
            WHERE employee_id = ?
            ORDER BY updated_at DESC
            """,
            (employee_id,),
        ).fetchall()
    return [
        {
            "thread_id": row[0],
            "employee_id": row[1],
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }
        for row in rows
    ]


def save_chat_message(thread_id, employee_id, role, message):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM chat_sessions WHERE thread_id = ? AND employee_id = ?",
            (thread_id, employee_id),
        )
        if cursor.fetchone() is None:
            raise ValueError("Chat session does not belong to this employee.")
        conn.execute(
            """
            INSERT INTO chat_messages (thread_id, role, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (thread_id, role, message, now),
        )
        conn.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE thread_id = ?",
            (now, thread_id),
        )


def get_chat_messages(thread_id, employee_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, message, created_at
            FROM chat_messages
            WHERE thread_id = ? AND EXISTS (
                SELECT 1 FROM chat_sessions
                WHERE chat_sessions.thread_id = chat_messages.thread_id
                  AND chat_sessions.employee_id = ?
            )
            ORDER BY id ASC
            """,
            (thread_id, employee_id),
        ).fetchall()
    return [
        {"role": row[0], "message": row[1], "created_at": row[2]}
        for row in rows
    ]


def get_conversation(thread_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, message, created_at
            FROM conversations
            WHERE thread_id = ?
            ORDER BY id ASC
            """,
            (thread_id,),
        ).fetchall()
    return [
        {
            "role": row[0],
            "message": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]