"""
Garden & Grace — Public Edition · feature endpoints.

Every AI-powered endpoint requires a Supabase-authenticated user and
counts against their daily quota (5/day free, unlimited premium).
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel

from ..auth_middleware import get_current_user
from ..services import claude_service, quota
from ..services.kjv_service import get_daily_verse, get_verse


router = APIRouter(prefix="/features", tags=["features"])

VALID_MODES = {"scripture", "sayings", "jokes", "off"}


def _verse_mode(request: Request) -> str:
    mode = (request.query_params.get("verse_mode") or "scripture").lower()
    return mode if mode in VALID_MODES else "scripture"


def _quota_meta(meta: dict) -> dict:
    return {
        "tier": meta.get("tier"),
        "remaining": meta.get("remaining"),
        "used_today": meta.get("used_today"),
    }


# ── GARDEN ────────────────────────────────────────────────────────────────────

@router.post("/garden")
async def garden_identify(request: Request, image: UploadFile = File(...), user=Depends(get_current_user)):
    meta = quota.check_and_increment(user["id"])
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_plant(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this plant. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("garden", mode) if mode != "off" else None
    return {"result": result, "verse": verse, "quota": _quota_meta(meta)}


# ── BIRDS & WILDLIFE ──────────────────────────────────────────────────────────

@router.post("/birds")
async def birds_identify(request: Request, image: UploadFile = File(...), user=Depends(get_current_user)):
    meta = quota.check_and_increment(user["id"])
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_bird_or_wildlife(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this creature. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("birds", mode) if mode != "off" else None
    return {"result": result, "verse": verse, "quota": _quota_meta(meta)}


# ── FISHING ───────────────────────────────────────────────────────────────────

class FishingRequest(BaseModel):
    lat: float
    lon: float
    location_name: Optional[str] = ""


@router.post("/fishing")
async def fishing_report(request: Request, req: FishingRequest, user=Depends(get_current_user)):
    meta = quota.check_and_increment(user["id"])
    result = claude_service.get_fishing_report(req.lat, req.lon, req.location_name)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not get fishing report. Please try again.")
    mode = _verse_mode(request)
    verse = get_verse("fishing", mode) if mode != "off" else None
    return {"result": result, "verse": verse, "quota": _quota_meta(meta)}


@router.post("/fishing/catch-recipe")
async def catch_recipe(request: Request, image: UploadFile = File(...), user=Depends(get_current_user)):
    meta = quota.check_and_increment(user["id"])
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_catch_and_recipe(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this catch. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("fishing", mode) if mode != "off" else None
    return {"result": result, "verse": verse, "quota": _quota_meta(meta)}


# ── RECIPE BUILDER ────────────────────────────────────────────────────────────

@router.post("/recipe")
async def recipe_from_photo(request: Request, image: UploadFile = File(...), user=Depends(get_current_user)):
    meta = quota.check_and_increment(user["id"])
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_recipe_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build recipe. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("recipe", mode) if mode != "off" else None
    return {"result": result, "verse": verse, "quota": _quota_meta(meta)}


# ── BUILD IT ──────────────────────────────────────────────────────────────────

@router.post("/build")
async def build_from_photo(request: Request, image: UploadFile = File(...), user=Depends(get_current_user)):
    meta = quota.check_and_increment(user["id"])
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_plan_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build a plan. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("build", mode) if mode != "off" else None
    return {"result": result, "verse": verse, "quota": _quota_meta(meta)}


# ── CATCHES ───────────────────────────────────────────────────────────────────

class CatchPost(BaseModel):
    fish_type: str
    location: str
    note: Optional[str] = ""
    image_data: Optional[str] = ""
    posted_by: Optional[str] = "Anonymous"


@router.post("/catches")
async def post_catch(catch: CatchPost, user=Depends(get_current_user)):
    from ..db import execute, get_db
    if not catch.fish_type.strip():
        raise HTTPException(status_code=400, detail="Please enter the fish type.")
    if not catch.location.strip():
        raise HTTPException(status_code=400, detail="Please enter a location.")
    fish_type = catch.fish_type.strip()[:100]
    location = catch.location.strip()[:200]
    note = (catch.note or "").strip()[:300]
    posted_by = (catch.posted_by or "Anonymous").strip()[:50]
    image_data = (catch.image_data or "")[:2_800_000]
    with get_db() as conn:
        execute(conn, """
            INSERT INTO catches (user_id, fish_type, location, note, image_data, posted_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [user["id"], fish_type, location, note, image_data, posted_by])
    return {"message": "Catch posted!", "fish_type": fish_type}


@router.get("/catches")
async def get_catches(limit: int = 20):
    from ..db import get_db, query_all
    limit = min(max(1, limit), 50)
    with get_db() as conn:
        catches = query_all(conn, """
            SELECT id, fish_type, location, note, image_data, posted_by, created_at
            FROM catches ORDER BY created_at DESC LIMIT ?
        """, [limit])
    for c in catches:
        if c.get("created_at"):
            c["created_at"] = str(c["created_at"])
    return {"catches": catches}


# ── DAILY SCRIPTURE ───────────────────────────────────────────────────────────

@router.get("/daily-verse")
async def daily_verse(request: Request):
    mode = _verse_mode(request)
    if mode == "off":
        return {"verse": "", "ref": ""}
    return get_daily_verse(mode)
