"""
Per-user daily quota.

Free tier:    FREE_DAILY_LIMIT (default 5) AI queries per UTC day.
Premium tier: unlimited (subscriptions table, status='active').
"""
import os
from datetime import datetime, timezone
from fastapi import HTTPException

from ..db import get_db, query_one, execute


FREE_DAILY_LIMIT = int(os.environ.get("FREE_DAILY_LIMIT", "5"))


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _is_premium(conn, user_id: str) -> bool:
    sub = query_one(
        conn,
        "SELECT status, current_period_end FROM subscriptions WHERE user_id = ?",
        [user_id],
    )
    if not sub:
        return False
    if sub.get("status") != "active":
        return False
    cpe = sub.get("current_period_end") or ""
    if not cpe:
        return True  # Active but no period info — treat as good
    try:
        end = datetime.fromisoformat(cpe.replace("Z", "+00:00"))
        return end > datetime.now(timezone.utc)
    except ValueError:
        return True


def get_status(user_id: str) -> dict:
    """Read-only status — does not increment."""
    today = _today()
    with get_db() as conn:
        premium = _is_premium(conn, user_id)
        row = query_one(conn, "SELECT count FROM usage WHERE user_id = ? AND date = ?", [user_id, today])
        used = row["count"] if row else 0
    if premium:
        return {"tier": "premium", "used_today": used, "daily_limit": None, "remaining": None}
    return {
        "tier": "free",
        "used_today": used,
        "daily_limit": FREE_DAILY_LIMIT,
        "remaining": max(0, FREE_DAILY_LIMIT - used),
    }


def check_and_increment(user_id: str) -> dict:
    """Atomically check the daily cap and bump the counter.

    Raises 402 (Payment Required) when a free user has hit the cap so the
    frontend can show the paywall.
    """
    today = _today()
    with get_db() as conn:
        premium = _is_premium(conn, user_id)
        execute(
            conn,
            "INSERT OR IGNORE INTO usage (user_id, date, count) VALUES (?, ?, 0)",
            [user_id, today],
        )
        if premium:
            execute(
                conn,
                "UPDATE usage SET count = count + 1 WHERE user_id = ? AND date = ?",
                [user_id, today],
            )
            return {"tier": "premium", "used_today": None, "remaining": None}

        row = query_one(conn, "SELECT count FROM usage WHERE user_id = ? AND date = ?", [user_id, today])
        used = row["count"] if row else 0
        if used >= FREE_DAILY_LIMIT:
            raise HTTPException(
                status_code=402,
                detail=f"You've used all {FREE_DAILY_LIMIT} free queries today. Upgrade for unlimited access.",
            )
        execute(
            conn,
            "UPDATE usage SET count = count + 1 WHERE user_id = ? AND date = ?",
            [user_id, today],
        )
        return {
            "tier": "free",
            "used_today": used + 1,
            "remaining": FREE_DAILY_LIMIT - (used + 1),
        }
