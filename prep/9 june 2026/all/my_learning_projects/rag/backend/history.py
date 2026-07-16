"""Persistent chat history in SQLite (stdlib). Conversations + messages."""
import json
import sqlite3
import time
from contextlib import contextmanager


@contextmanager
def _conn(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db(path):
    with _conn(path) as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at REAL NOT NULL
            );
        """)


def create_conversation(path, title="New chat"):
    with _conn(path) as c:
        cur = c.execute("INSERT INTO conversations (title, created_at) VALUES (?, ?)",
                        (title, time.time()))
        return cur.lastrowid


def list_conversations(path):
    with _conn(path) as c:
        rows = c.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def rename_conversation(path, conv_id, title):
    with _conn(path) as c:
        c.execute("UPDATE conversations SET title=? WHERE id=?", (title, conv_id))


def delete_conversation(path, conv_id):
    with _conn(path) as c:
        c.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
        c.execute("DELETE FROM conversations WHERE id=?", (conv_id,))


def add_message(path, conv_id, role, content, sources=None):
    with _conn(path) as c:
        c.execute(
            "INSERT INTO messages (conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?)",
            (conv_id, role, content, json.dumps(sources or []), time.time()),
        )


def get_messages(path, conv_id):
    with _conn(path) as c:
        rows = c.execute(
            "SELECT role, content, sources, created_at FROM messages WHERE conversation_id=? ORDER BY id",
            (conv_id,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["sources"] = json.loads(d["sources"]) if d["sources"] else []
            out.append(d)
        return out
