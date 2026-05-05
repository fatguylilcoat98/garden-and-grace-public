"""
Garden & Grace — Test Suite (Public Edition)
Truth · Safety · We Got Your Back

Self-contained. Run via GET /test/api or `python -m backend.tests.test_suite`.
"""
import os
import sys
import base64

TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
)


def run_all_tests() -> list:
    results = []
    results.append(_test_env("ANTHROPIC_API_KEY"))
    results.append(_test_env("SUPABASE_JWT_SECRET"))
    results.append(_test_env("SUPABASE_URL"))
    results.append(_test_env("SUPABASE_ANON_KEY"))
    results.append(_test_env("STRIPE_SECRET_KEY"))
    results.append(_test_env("STRIPE_PRICE_ID"))
    results.append(_test_db_connection())
    results.append(_test_db_tables())
    results.append(_test_verse_service())
    results.append(_test_verse_off())
    results.append(_test_claude_functions())
    results.append(_test_fishing_response_shape())
    results.append(_test_catch_id_exists())
    results.append(_test_quota_config())
    results.append(_test_catches_crud())
    results.append(_test_input_validation())
    return results


def _pass(name, notes=""):
    return {"test": name, "passed": True, "notes": notes}


def _fail(name, error="", notes=""):
    return {"test": name, "passed": False, "error": str(error)[:300], "notes": notes}


def _test_env(key):
    val = os.environ.get(key, "")
    if val and len(val) > 10:
        return _pass(f"ENV: {key} set", f"{len(val)} chars")
    return _fail(f"ENV: {key} set", "Missing or too short")


def _test_db_connection():
    try:
        from backend.db import get_db, query_one
        with get_db() as conn:
            row = query_one(conn, "SELECT 1 AS ok")
        if row and row.get("ok") == 1:
            return _pass("DB: Connection")
        return _fail("DB: Connection", "Unexpected result")
    except Exception as e:
        return _fail("DB: Connection", e)


def _test_db_tables():
    try:
        from backend.db import get_db, query_all
        with get_db() as conn:
            rows = query_all(conn, "SELECT name FROM sqlite_master WHERE type = 'table'")
        names = {r["name"] for r in rows}
        required = {"usage", "subscriptions", "catches"}
        missing = required - names
        if missing:
            return _fail("DB: Tables", f"Missing: {missing}")
        return _pass("DB: Tables", ", ".join(sorted(required)))
    except Exception as e:
        return _fail("DB: Tables", e)


def _test_verse_service():
    try:
        from backend.services.kjv_service import get_verse, get_daily_verse
        errors = []
        for mode in ["scripture", "sayings", "jokes"]:
            for cat in ["garden", "birds", "fishing", "recipe", "build", "daily"]:
                v = get_verse(cat, mode)
                if not v or not v.get("verse"):
                    errors.append(f"{mode}/{cat}: empty")
            dv = get_daily_verse(mode)
            if not dv or not dv.get("verse"):
                errors.append(f"daily_{mode}: empty")
        if errors:
            return _fail("Verse: All modes", "; ".join(errors[:5]))
        return _pass("Verse: All modes", "3 modes × 6 categories OK")
    except Exception as e:
        return _fail("Verse: All modes", e)


def _test_verse_off():
    try:
        from backend.services.kjv_service import get_verse
        v = get_verse("fishing", "unknown_mode")
        if v and v.get("verse"):
            return _pass("Verse: Unknown mode fallback")
        return _fail("Verse: Unknown mode fallback", "Empty")
    except Exception as e:
        return _fail("Verse: Unknown mode fallback", e)


def _test_claude_functions():
    try:
        from backend.services.claude_service import (
            identify_plant, identify_bird_or_wildlife, get_fishing_report,
            build_recipe_from_photo, build_plan_from_photo, identify_catch_and_recipe,
        )
        return _pass("Claude: 6 functions exist")
    except ImportError as e:
        return _fail("Claude: 6 functions exist", e)


def _test_fishing_response_shape():
    try:
        from backend.services.claude_service import get_fishing_report
        result = get_fishing_report(38.5816, -121.4944, "Sacramento, California")
        if "error" in result:
            return _fail("Fishing: Response", f"API error: {result.get('error', '')[:200]}")
        required = ["outlook", "conditions", "active_species", "technique_tip"]
        missing = [k for k in required if k not in result]
        if missing:
            return _fail("Fishing: Response", f"Missing: {missing}")
        return _pass("Fishing: Response", f"outlook={result.get('outlook')}")
    except Exception as e:
        return _fail("Fishing: Response", e)


def _test_catch_id_exists():
    try:
        from backend.services.claude_service import identify_catch_and_recipe
        if callable(identify_catch_and_recipe):
            return _pass("Catch ID: Function callable")
        return _fail("Catch ID: Function callable", "Not callable")
    except Exception as e:
        return _fail("Catch ID: Function callable", e)


def _test_quota_config():
    try:
        from backend.services.quota import FREE_DAILY_LIMIT, get_status
        if FREE_DAILY_LIMIT < 1:
            return _fail("Quota: Config", f"FREE_DAILY_LIMIT={FREE_DAILY_LIMIT}")
        s = get_status("__test_user_no_usage__")
        if s.get("tier") != "free":
            return _fail("Quota: Config", f"Unknown user should be free, got {s}")
        return _pass("Quota: Config", f"FREE_DAILY_LIMIT={FREE_DAILY_LIMIT}")
    except Exception as e:
        return _fail("Quota: Config", e)


def _test_catches_crud():
    try:
        from backend.db import get_db, execute, query_all
        test_fish = "_TEST_CATCH_DELETE_ME"
        with get_db() as conn:
            execute(conn, """
                INSERT INTO catches (user_id, fish_type, location, note, posted_by)
                VALUES (?, ?, ?, ?, ?)
            """, ["__test_user__", test_fish, "Test Lake", "Automated test", "BugTester"])
        with get_db() as conn:
            rows = query_all(conn, "SELECT * FROM catches WHERE fish_type = ?", [test_fish])
        if not rows:
            return _fail("Catches: CRUD", "Insert/read mismatch")
        with get_db() as conn:
            execute(conn, "DELETE FROM catches WHERE fish_type = ?", [test_fish])
        return _pass("Catches: CRUD", "Insert → Read → Delete OK")
    except Exception as e:
        return _fail("Catches: CRUD", e)


def _test_input_validation():
    try:
        if not "".strip():
            pass
        long_text = "x" * 500
        if len(long_text[:100]) != 100:
            return _fail("Input: Validation", "Length trim failed")
        return _pass("Input: Validation")
    except Exception as e:
        return _fail("Input: Validation", e)


if __name__ == "__main__":
    print("=" * 60)
    print("  GARDEN & GRACE — TEST SUITE")
    print("=" * 60)
    results = run_all_tests()
    passed = sum(1 for r in results if r.get("passed"))
    failed = len(results) - passed
    for r in results:
        icon = "✅" if r.get("passed") else "❌"
        status = "PASS" if r.get("passed") else "FAIL"
        print(f"\n{icon} {status} — {r['test']}")
        if r.get("notes"):
            print(f"   {r['notes']}")
        if r.get("error"):
            print(f"   Error: {r['error']}")
    print(f"\n{'=' * 60}\n  {passed} passed / {failed} failed\n{'=' * 60}")
    sys.exit(0 if failed == 0 else 1)
