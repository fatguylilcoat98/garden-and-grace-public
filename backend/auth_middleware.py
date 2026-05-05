"""
Garden & Grace — Auth: verify Supabase JWT.

Supabase issues HS256 JWTs signed with SUPABASE_JWT_SECRET. We extract
the user id (`sub`) and email from claims to identify the user.
"""
import os
from fastapi import Header, HTTPException
import jwt


SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


def get_current_user(authorization: str = Header(None)):
    """FastAPI dependency: returns {id, email} for the authenticated user."""
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Auth not configured. Set SUPABASE_JWT_SECRET on the server.",
        )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not signed in.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session. Please sign in again.")

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session.")
    return {
        "id": user_id,
        "email": claims.get("email") or "",
    }
