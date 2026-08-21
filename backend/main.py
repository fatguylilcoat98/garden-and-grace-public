"""
Garden & Grace — Public Edition · FastAPI entry.
"""
import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .auth_middleware import get_current_user
from .db import init_db
from .routes.billing import router as billing_router
from .routes.features import router as features_router
from .services import quota


app = FastAPI(title="Garden & Grace", version="2.1.0-public")


# ── CORS ─────────────────────────────────────────────────────────────────────
# In production, lock to APP_URL. For local dev (no APP_URL set), permit any
# origin without credentials so a separate Vite/whatever dev server still works.
APP_URL = os.environ.get("APP_URL", "")
if APP_URL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[APP_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(features_router)
app.include_router(billing_router)


# ── PUBLIC INFO ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "app": "Garden & Grace Public", "version": "2.1.0"}


@app.get("/config")
def public_config():
    """Bootstrap values the frontend needs before sign-in.

    The Supabase anon key is safe to ship to the browser — RLS and the
    JWT secret keep the backend authoritative.
    """
    return {
        "supabaseUrl": os.environ.get("SUPABASE_URL", ""),
        "supabaseAnonKey": os.environ.get("SUPABASE_ANON_KEY", ""),
        "billingEnabled": bool(os.environ.get("STRIPE_SECRET_KEY") and os.environ.get("STRIPE_PRICE_ID")),
        "freeDailyLimit": quota.FREE_DAILY_LIMIT,
    }


@app.get("/usage")
def usage_info(user=Depends(get_current_user)):
    """Authenticated quota status (used by the header counter)."""
    return quota.get_status(user["id"])


# ── BUG TESTER ───────────────────────────────────────────────────────────────

@app.get("/test/api")
def test_api(live: bool = False):
    from .tests.test_suite import run_all_tests
    results = run_all_tests()
    if not live:
        results = [r for r in results if "Fishing: Response" not in r.get("test", "")]
    passed = sum(1 for r in results if r.get("passed"))
    failed = len(results) - passed
    return {
        "service": "Garden & Grace Public",
        "summary": f"{passed} passed / {failed} failed",
        "all_pass": failed == 0,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
    }


# ── STATIC FRONTEND ──────────────────────────────────────────────────────────

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
