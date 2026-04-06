"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""
import os
import re
from contextlib import contextmanager
import pg8000.native

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def _parse_url(url):
    pattern = r"postgresql://([^:]+):([^@]+)@([^/:]+)(?::(\d+))?/(.+)"
    m = re.match(pattern, url)
    if not m:
        raise ValueError(f"Invalid DATABASE_URL: {url}")
    user, password, host, port, database = m.groups()
    return {
        "user":     user,
        "password": password,
        "host":     host,
        "port":     int(port) if port else 5432,
        "database": database,
    }

def _convert_params(sql, params):
    """
    Convert $1, $2 style placeholders to :1, :2 for pg8000 native.
    Also convert params list to keyword dict {1: val, 2: val}.
    """
    if not params:
        return sql, {}
    param_dict = {str(i + 1): v for i, v in enumerate(params)}
    new_sql = re.sub(r'\$(\d+)', r':\1', sql)
    return new_sql, param_dict

def init_db():
    with get_db() as conn:
        conn.run("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.run("""
            CREATE TABLE IF NOT EXISTS magic_tokens (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                used INTEGER DEFAULT 0,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.run("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

@contextmanager
def get_db():
    kwargs = _parse_url(DATABASE_URL)
    conn = pg8000.native.Connection(**kwargs)
    try:
        yield conn
        conn.run("COMMIT")
    except Exception:
        conn.run("ROLLBACK")
        raise
    finally:
        conn.close()

def _rows_to_dicts(conn, rows):
    if not rows:
        return []
    cols = [c["name"] for c in conn.columns]
    return [dict(zip(cols, row)) for row in rows]

def query_one(conn, sql, params=None):
    new_sql, param_dict = _convert_params(sql, params)
    rows = conn.run(new_sql, **param_dict)
    result = _rows_to_dicts(conn, rows)
    return result[0] if result else None

def query_all(conn, sql, params=None):
    new_sql, param_dict = _convert_params(sql, params)
    rows = conn.run(new_sql, **param_dict)
    return _rows_to_dicts(conn, rows)

def execute(conn, sql, params=None):
    new_sql, param_dict = _convert_params(sql, params)
    conn.run(new_sql, **param_dict)
