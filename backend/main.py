"""
Garden & Grace — Public Edition
The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back

PUBLIC VERSION — separate from the family build.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import time
from threading import Lock

from .db import init_db
from .routes.features import router as features_router

app = FastAPI(title="Garden & Grace", version="2.0.0-public")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── RATE LIMITING ────────────────────────────────────────────────────────────
COOLDOWN_SECONDS = int(os.environ.get("GG_COOLDOWN_SECONDS", "20"))
DAILY_LIMIT_FREE = int(os.environ.get("GG_DAILY_LIMIT", "8"))

_rate_lock = Lock()
_last_request = {}
_daily_counts = {}


def _get_client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host or "unknown")


def _check_limits(ip: str):
    """Returns None if OK, or a response dict if limited."""
    now = time.time()
    today = time.strftime("%Y-%m-%d")

    with _rate_lock:
        # Cooldown check
        last = _last_request.get(ip, 0)
        if now - last < COOLDOWN_SECONDS:
            wait = int(COOLDOWN_SECONDS - (now - last))
            return {"type": "cooldown", "message": f"Please wait {wait} seconds before your next request."}

        # Daily cap check
        day_data = _daily_counts.get(ip)
        if day_data and day_data["date"] == today:
            if day_data["count"] >= DAILY_LIMIT_FREE:
                return {"type": "daily", "message": "Daily limit reached for now. Please try again tomorrow."}
        elif not day_data or day_data["date"] != today:
            _daily_counts[ip] = {"date": today, "count": 0}

        # All clear — record this request
        _last_request[ip] = now
        _daily_counts[ip]["count"] = _daily_counts[ip].get("count", 0) + 1

    return None


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/features/") and request.method == "POST":
        ip = _get_client_ip(request)
        limit = _check_limits(ip)
        if limit:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "limit_reached",
                    "message": limit["message"],
                    "type": limit["type"],
                },
            )
    return await call_next(request)


app.include_router(features_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "Garden & Grace Public", "version": "2.0.0"}


@app.get("/usage")
def usage_info(request: Request):
    """Let frontend check remaining daily uses."""
    ip = _get_client_ip(request)
    today = time.strftime("%Y-%m-%d")
    with _rate_lock:
        day_data = _daily_counts.get(ip)
        used = day_data["count"] if day_data and day_data["date"] == today else 0
    return {
        "daily_limit": DAILY_LIMIT_FREE,
        "used_today": used,
        "remaining": max(0, DAILY_LIMIT_FREE - used),
        "tier": "free",
    }


# ── BUG TESTER ───────────────────────────────────────────────────────────────

@app.get("/test/api")
def test_api():
    """Run backend health checks and return results."""
    results = []

    # 1. App running
    results.append({"test": "App running", "pass": True})

    # 2. Anthropic key set
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    results.append({"test": "ANTHROPIC_API_KEY set", "pass": bool(key and len(key) > 10)})

    # 3. SendGrid key set
    sg_key = os.environ.get("SENDGRID_API_KEY", "")
    results.append({"test": "SENDGRID_API_KEY set", "pass": bool(sg_key and len(sg_key) > 10)})

    # 4. Database connection
    try:
        from .db import get_db, query_one
        with get_db() as conn:
            query_one(conn, "SELECT 1 AS ok")
        results.append({"test": "Database connection", "pass": True})
    except Exception as e:
        results.append({"test": "Database connection", "pass": False, "error": str(e)[:200]})

    # 5. Catches table exists
    try:
        from .db import get_db, query_all
        with get_db() as conn:
            query_all(conn, "SELECT COUNT(*) FROM catches")
        results.append({"test": "Catches table exists", "pass": True})
    except Exception as e:
        results.append({"test": "Catches table exists", "pass": False, "error": str(e)[:200]})

    # 6. KJV service works (all modes)
    try:
        from .services.kjv_service import get_verse, get_daily_verse
        for mode in ["scripture", "sayings", "jokes"]:
            v = get_verse("fishing", mode)
            assert v and v.get("verse"), f"{mode} returned empty"
        dv = get_daily_verse("scripture")
        assert dv and dv.get("verse")
        results.append({"test": "Verse service (all modes)", "pass": True})
    except Exception as e:
        results.append({"test": "Verse service (all modes)", "pass": False, "error": str(e)[:200]})

    # 7. Claude service importable
    try:
        from .services import claude_service
        assert hasattr(claude_service, "identify_plant")
        assert hasattr(claude_service, "get_fishing_report")
        assert hasattr(claude_service, "identify_catch_and_recipe")
        results.append({"test": "Claude service functions exist", "pass": True})
    except Exception as e:
        results.append({"test": "Claude service functions exist", "pass": False, "error": str(e)[:200]})

    # 8. Rate limiter working
    results.append({"test": "Rate limiter loaded", "pass": COOLDOWN_SECONDS > 0 and DAILY_LIMIT_FREE > 0,
                     "info": f"Cooldown: {COOLDOWN_SECONDS}s, Daily: {DAILY_LIMIT_FREE}"})

    passed = sum(1 for r in results if r["pass"])
    return {
        "summary": f"{passed}/{len(results)} passed",
        "all_pass": passed == len(results),
        "results": results,
    }


frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/test")
    def serve_test_page():
        test_html = os.path.join(frontend_path, "test.html")
        if os.path.exists(test_html):
            return FileResponse(test_html)
        return {"error": "Test page not found"}

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        index = os.path.join(frontend_path, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"error": "Frontend not found"}


@app.on_event("startup")
def on_startup():
    init_db()
    print("🌿 Garden & Grace (Public Edition) is running.")
