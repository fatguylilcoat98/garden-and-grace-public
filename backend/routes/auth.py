"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import os

from ..db import get_db, query_one, execute
from ..services.email_service import send_magic_link

router = APIRouter(prefix="/auth", tags=["auth"])
TOKEN_EXPIRY_HOURS = 24

class SignupRequest(BaseModel):
    email: str
    name: str

class MagicLinkRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    token: str

@router.post("/signup")
def signup(req: SignupRequest):
    with get_db() as conn:
        existing = query_one(conn, "SELECT id FROM users WHERE email = $1", [req.email.lower()])
        if not existing:
            execute(conn, "INSERT INTO users (email, name) VALUES ($1, $2)", [req.email.lower(), req.name])
    return _create_and_send_link(req.email.lower(), req.name)

@router.post("/magic-link")
def request_magic_link(req: MagicLinkRequest):
    with get_db() as conn:
        user = query_one(conn, "SELECT name FROM users WHERE email = $1", [req.email.lower()])
        if not user:
            raise HTTPException(status_code=404, detail="Email not found. Please sign up first.")
    return _create_and_send_link(req.email.lower(), user["name"])

@router.post("/verify")
def verify_magic_link(req: VerifyRequest):
    with get_db() as conn:
        token_row = query_one(conn,
            "SELECT * FROM magic_tokens WHERE token = $1 AND used = 0", [req.token])

        if not token_row:
            raise HTTPException(status_code=400, detail="Invalid or already used link.")

        if datetime.utcnow() > datetime.fromisoformat(str(token_row["expires_at"])):
            raise HTTPException(status_code=400, detail="This link has expired. Please request a new one.")

        execute(conn, "UPDATE magic_tokens SET used = 1 WHERE token = $1", [req.token])

        user = query_one(conn, "SELECT * FROM users WHERE email = $1", [token_row["email"]])

        session_token = secrets.token_urlsafe(48)
        execute(conn,
            "INSERT INTO sessions (user_id, session_token) VALUES ($1, $2)",
            [user["id"], session_token])

    return {
        "session_token": session_token,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    }

def _create_and_send_link(email: str, name: str) -> dict:
    token = secrets.token_urlsafe(48)
    expires_at = (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat()
    with get_db() as conn:
        execute(conn,
            "INSERT INTO magic_tokens (email, token, expires_at) VALUES ($1, $2, $3)",
            [email, token, expires_at])
    app_url = os.environ.get("APP_URL", "https://garden-and-grace.onrender.com")
    magic_url = f"{app_url}/auth/verify?token={token}"
    send_magic_link(email, name, token)
    return {
        "message": f"Welcome {name}! Tap your link to enter.",
        "magic_url": magic_url,
        "token": token
    }
