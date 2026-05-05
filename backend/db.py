"""
Garden & Grace — Public Edition
Database: SQLite (single file) on Render disk.
"""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", "/var/data/garden_grace_public.db")


def _dict_factory(cursor, row):
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        # Per-user daily query usage
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)
        # Premium subscriptions (Stripe)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id TEXT PRIMARY KEY,
                email TEXT,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                status TEXT NOT NULL DEFAULT 'inactive',
                current_period_end TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Catches feed (per-user; user_id from Supabase JWT)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS catches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                fish_type TEXT NOT NULL,
                location TEXT NOT NULL,
                note TEXT DEFAULT '',
                image_data TEXT DEFAULT '',
                posted_by TEXT DEFAULT 'Anonymous',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        _migrate(conn)


def _migrate(conn):
    """Add user_id to legacy catches table if it's missing."""
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(catches)").fetchall()]
    if "user_id" not in cols:
        conn.execute("ALTER TABLE catches ADD COLUMN user_id TEXT NOT NULL DEFAULT ''")
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
    cursor = conn.execute(sql, params or [])
    return cursor.fetchone()


def query_all(conn, sql, params=None):
    cursor = conn.execute(sql, params or [])
    return cursor.fetchall()


def execute(conn, sql, params=None):
    conn.execute(sql, params or [])
