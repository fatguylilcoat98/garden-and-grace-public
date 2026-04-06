"""
Garden & Grace — Public Edition
The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back

PUBLIC VERSION — no hardcoded family data.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services import claude_service, pdf_service, email_service
from ..services.kjv_service import get_verse, get_daily_verse

router = APIRouter(prefix="/features", tags=["features"])

# ── GARDEN ────────────────────────────────────────────────────────────────────

@router.post("/garden")
async def garden_identify(image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_plant(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this plant. Please try a clearer photo.")
    verse = get_verse("garden")
    return {"result": result, "verse": verse}

# ── BIRDS & WILDLIFE ──────────────────────────────────────────────────────────

@router.post("/birds")
async def birds_identify(image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.identify_bird_or_wildlife(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not identify this creature. Please try a clearer photo.")
    verse = get_verse("birds")
    return {"result": result, "verse": verse}

# ── FISHING ───────────────────────────────────────────────────────────────────

class FishingRequest(BaseModel):
    lat: float
    lon: float
    location_name: Optional[str] = ""

@router.post("/fishing")
async def fishing_report(req: FishingRequest):
    result = claude_service.get_fishing_report(req.lat, req.lon, req.location_name)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not get fishing report. Please try again.")
    verse = get_verse("fishing")
    return {"result": result, "verse": verse}

# ── RECIPE BUILDER ────────────────────────────────────────────────────────────

@router.post("/recipe")
async def recipe_from_photo(image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_recipe_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build recipe. Please try a clearer photo.")
    verse = get_verse("recipe")
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
async def build_from_photo(image: UploadFile = File(...)):
    image_bytes = await image.read()
    media_type = image.content_type or "image/jpeg"
    result = claude_service.build_plan_from_photo(image_bytes, media_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail="Could not build a plan. Please try a clearer photo.")
    verse = get_verse("build")
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

# ── DAILY SCRIPTURE ───────────────────────────────────────────────────────────

@router.get("/daily-verse")
async def daily_verse():
    return get_daily_verse()
