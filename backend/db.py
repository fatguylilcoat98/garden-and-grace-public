"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", "/var/data/garden_grace_public.db")


def _dict_factory(cursor, row):
    """Return rows as dicts instead of tuples."""
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS magic_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                used INTEGER DEFAULT 0,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS catches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fish_type TEXT NOT NULL,
                location TEXT NOT NULL,
                note TEXT DEFAULT '',
                image_data TEXT DEFAULT '',
                posted_by TEXT DEFAULT 'Anonymous',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_one(conn, sql, params=None):
    """Query returning a single row dict or None.
    Accepts $1, $2 style placeholders — converts to ? for sqlite3.
    """
    new_sql, new_params = _convert_params(sql, params)
    cursor = conn.execute(new_sql, new_params)
    row = cursor.fetchone()
    return row


def query_all(conn, sql, params=None):
    """Query returning a list of row dicts."""
    new_sql, new_params = _convert_params(sql, params)
    cursor = conn.execute(new_sql, new_params)
    return cursor.fetchall()


def execute(conn, sql, params=None):
    """Execute a statement (INSERT, UPDATE, DELETE)."""
    new_sql, new_params = _convert_params(sql, params)
    conn.execute(new_sql, new_params)


def _convert_params(sql, params):
    """Convert $1, $2 placeholders to ? for sqlite3.
    Keeps compatibility with routes that use Postgres-style params.
    """
    if not params:
        return sql, []
    import re
    # Replace $N with ? and reorder params accordingly
    placeholders = re.findall(r'\$(\d+)', sql)
    new_sql = re.sub(r'\$\d+', '?', sql)
    # Reorder params based on placeholder order ($2, $1 -> params[1], params[0])
    new_params = [params[int(p) - 1] for p in placeholders]
    return new_sql, new_params
