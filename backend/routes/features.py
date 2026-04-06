"""
Garden & Grace — Public Edition
The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back

PUBLIC VERSION — no hardcoded family data.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from ..services import claude_service, pdf_service, email_service
from ..services.kjv_service import get_verse, get_daily_verse

router = APIRouter(prefix="/features", tags=["features"])

VALID_MODES = {"scripture", "sayings", "jokes", "off"}

def _verse_mode(request: Request) -> str:
    mode = (request.query_params.get("verse_mode") or "scripture").lower()
    return mode if mode in VALID_MODES else "scripture"

# ── GARDEN ────────────────────────────────────────────────────────────────────

@router.post("/garden")
async def garden_identify(request: Request, image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_plant(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this plant. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("garden", mode) if mode != "off" else None
    return {"result": result, "verse": verse}

# ── BIRDS & WILDLIFE ──────────────────────────────────────────────────────────

@router.post("/birds")
async def birds_identify(request: Request, image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_bird_or_wildlife(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this creature. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("birds", mode) if mode != "off" else None
    return {"result": result, "verse": verse}

# ── FISHING ───────────────────────────────────────────────────────────────────

class FishingRequest(BaseModel):
    lat: float
    lon: float
    location_name: Optional[str] = ""

@router.post("/fishing")
async def fishing_report(request: Request, req: FishingRequest):
    result = claude_service.get_fishing_report(req.lat, req.lon, req.location_name)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not get fishing report. Please try again.")
    mode = _verse_mode(request)
    verse = get_verse("fishing", mode) if mode != "off" else None
    return {"result": result, "verse": verse}

# ── CATCH ID + RECIPE ────────────────────────────────────────────────────────

@router.post("/fishing/catch-recipe")
async def catch_recipe(request: Request, image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_catch_and_recipe(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this catch. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("fishing", mode) if mode != "off" else None
    return {"result": result, "verse": verse}

# ── RECIPE BUILDER ────────────────────────────────────────────────────────────

@router.post("/recipe")
async def recipe_from_photo(request: Request, image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_recipe_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build recipe. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("recipe", mode) if mode != "off" else None
    return {"result": result, "verse": verse}

class EmailRequest(BaseModel):
    email: str

@router.post("/recipe/email")
async def email_recipe_pdf(image: UploadFile = File(...), email: str = ""):
    if not email:
        raise HTTPException(status_code=400, detail="Please provide an email address.")
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_recipe_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build recipe.")
    verse = get_verse("recipe")
    pdf_bytes = pdf_service.generate_recipe_pdf(result, verse, "Friend")
    sent = email_service.send_recipe_pdf(
        email, "Friend",
        result.get("dish_name", "Your Recipe"), pdf_bytes
    )
    if not sent:
        raise HTTPException(status_code=500, detail="Recipe ready but email failed. Please try again.")
    return {"message": "Recipe sent! Check your inbox.", "dish_name": result.get("dish_name")}

# ── BUILD IT ──────────────────────────────────────────────────────────────────

@router.post("/build")
async def build_from_photo(request: Request, image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_plan_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build a plan. Please try a clearer photo.")
    mode = _verse_mode(request)
    verse = get_verse("build", mode) if mode != "off" else None
    return {"result": result, "verse": verse}

@router.post("/build/email")
async def email_build_pdf(image: UploadFile = File(...), email: str = ""):
    if not email:
        raise HTTPException(status_code=400, detail="Please provide an email address.")
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_plan_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build plan.")
    verse = get_verse("build")
    pdf_bytes = pdf_service.generate_build_pdf(result, verse, "Friend")
    sent = email_service.send_build_pdf(
        email, "Friend",
        result.get("project_name", "Your Build Plan"), pdf_bytes
    )
    if not sent:
        raise HTTPException(status_code=500, detail="Plan ready but email failed. Please try again.")
    return {"message": "Build plan sent! Check your inbox.", "project_name": result.get("project_name")}

# ── CATCHES ───────────────────────────────────────────────────────────────────

class CatchPost(BaseModel):
    fish_type: str
    location: str
    note: Optional[str] = ""
    image_data: Optional[str] = ""
    posted_by: Optional[str] = "Anonymous"

@router.post("/catches")
async def post_catch(catch: CatchPost):
    from ..db import get_db, execute
    if not catch.fish_type.strip():
        raise HTTPException(status_code=400, detail="Please enter the fish type.")
    if not catch.location.strip():
        raise HTTPException(status_code=400, detail="Please enter a location.")
    # Limit input lengths
    fish_type = catch.fish_type.strip()[:100]
    location = catch.location.strip()[:200]
    note = (catch.note or "").strip()[:300]
    posted_by = (catch.posted_by or "Anonymous").strip()[:50]
    # Store base64 image data (limited to ~2MB encoded)
    image_data = (catch.image_data or "")[:2_800_000]
    with get_db() as conn:
        execute(conn, """
            INSERT INTO catches (fish_type, location, note, image_data, posted_by)
            VALUES ($1, $2, $3, $4, $5)
        """, [fish_type, location, note, image_data, posted_by])
    return {"message": "Catch posted!", "fish_type": fish_type}

@router.get("/catches")
async def get_catches(limit: int = 20):
    from ..db import get_db, query_all
    limit = min(max(1, limit), 50)
    with get_db() as conn:
        catches = query_all(conn, f"""
            SELECT id, fish_type, location, note, image_data, posted_by, created_at
            FROM catches ORDER BY created_at DESC LIMIT {limit}
        """)
    # Format timestamps
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
