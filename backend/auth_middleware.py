"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""

from fastapi import Header, HTTPException
from .db import get_db, query_one

def get_current_user(authorization: str = Header(None)):
    """Dependency: validates session token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in.")
    token = authorization.split(" ", 1)[1]
    with get_db() as conn:
        row = query_one(conn, """
            SELECT u.id, u.name, u.email
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = $1
        """, [token])
    if not row:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    return row
