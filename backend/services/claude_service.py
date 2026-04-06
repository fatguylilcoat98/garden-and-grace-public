"""
Garden & Grace — Public Edition
The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""

import anthropic
import base64
import os
import json
from typing import Optional

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"

def _encode_image(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    encoded = base64.standard_b64encode(image_bytes).decode("utf-8")
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": media_type, "data": encoded}
    }

def _ask_claude(system: str, messages: list, max_tokens: int = 1200) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages
    )
    return response.content[0].text

# ── GARDEN ──────────────────────────────────────────────────────────────────

def identify_plant(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    system = """You are a warm, knowledgeable master gardener speaking to someone who loves their garden.
Your tone is like a wise neighbor — simple, encouraging, plain English. No jargon.
Respond ONLY with valid JSON in this exact shape:
{
  "name": "Common name (Scientific name)",
  "what_it_is": "2-3 plain sentences describing the plant warmly.",
  "care": "2-3 sentences on how to care for it day to day.",
  "watering": "Simple watering schedule in plain English.",
  "planting_tips": "2-3 practical tips for planting or growing.",
  "seasonal_advice": "What to do with it this season.",
  "fun_fact": "One delightful fact about this plant."
}"""
    messages = [{"role": "user", "content": [
        _encode_image(image_bytes, media_type),
        {"type": "text", "text": "What plant is this? Give me your full gardening guidance."}
    ]}]
    raw = _ask_claude(system, messages, 1000)
    return _safe_parse(raw)

# ── BIRDS & WILDLIFE ─────────────────────────────────────────────────────────

def identify_bird_or_wildlife(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    system = """You are a warm, enthusiastic wildlife naturalist. Your audience loves birds and all of God's creatures.
Plain English, no jargon. Tone like a trusted friend who knows a lot about nature.
Respond ONLY with valid JSON:
{
  "name": "Common name (Scientific name)",
  "type": "bird or animal type",
  "what_it_is": "2-3 warm sentences describing this creature.",
  "where_found": "Where this species lives and ranges.",
  "fun_facts": ["fact 1", "fact 2", "fact 3"],
  "nesting_or_habitat": "Info about its home, nest, or den.",
  "eagle_connection": "If this IS a Bald Eagle or connects to eagles, share something special. Otherwise leave as empty string.",
  "best_time_to_spot": "When and where to see this creature."
}"""
    messages = [{"role": "user", "content": [
        _encode_image(image_bytes, media_type),
        {"type": "text", "text": "What bird or animal is this? Tell me everything wonderful about it."}
    ]}]
    raw = _ask_claude(system, messages, 1000)
    return _safe_parse(raw)

# ── FISHING ──────────────────────────────────────────────────────────────────

def get_fishing_report(lat: float, lon: float, location_name: str = "") -> dict:
    system = """You are a friendly, experienced fishing guide who loves helping people have a great day on the water.
Plain English. Practical advice. Warm and encouraging tone — like a helpful fishing buddy.
Be honest when information is inferred from general conditions rather than exact local data.
Respond ONLY with valid JSON:
{
  "outlook": "One word: Slow, Fair, Promising, or Strong",
  "outlook_reason": "One sentence explaining why the outlook is what it is.",
  "conditions": "2-3 sentences describing today's fishing conditions overall.",
  "best_times": [
    {"window": "time range", "why": "short reason this window is good"}
  ],
  "active_species": [
    {"name": "species name", "activity": "Active, Moderate, or Slow", "note": "one short tip for this species"}
  ],
  "bait_and_lures": [
    {"name": "bait or lure name", "best_for": "what species or situation", "tip": "one practical note"}
  ],
  "tides_and_current": "If near coastal or tidal water: current tide phase, when the next high/low is, and how it affects fishing. If inland/non-tidal, say so briefly and skip tide details.",
  "water_and_weather": "2-3 sentences on how water temp, clarity, wind, or weather affects fishing today.",
  "hot_spots": [
    {"area_type": "type of area to target", "why": "why this area is good today", "tip": "one practical suggestion"}
  ],
  "technique_tip": "One practical next-step tip — the single best thing to try today.",
  "encouragement": "A short warm encouraging note for the day."
}

For hot_spots: suggest general types of areas (weed lines, shaded banks, creek mouths, rocky points, deeper ledges, coves, calm pockets near structure, etc.) — NOT exact coordinates or named locations unless you are confident. Be honest about what is inferred."""
    location_str = location_name if location_name else f"coordinates {lat:.4f}, {lon:.4f}"
    messages = [{"role": "user", "content": f"Give me a complete fishing report for {location_str} today. Include outlook, best times, species activity, bait ideas, water/weather impact, and hot spot suggestions for where to start."}]
    raw = _ask_claude(system, messages, 1500)
    return _safe_parse(raw)

# ── RECIPE BUILDER ────────────────────────────────────────────────────────────

def build_recipe_from_photo(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    system = """You are a warm, health-conscious home cook — like a beloved neighbor who shares wonderful recipes.
Your audience loves cooking healthy, wholesome meals for their family.
Plain English, simple steps, no fancy techniques. Warm and encouraging.
Respond ONLY with valid JSON:
{
  "dish_name": "Name of the dish",
  "description": "2-3 warm sentences about this dish.",
  "serves": "Number of servings",
  "prep_time": "Prep time",
  "cook_time": "Cook time",
  "health_note": "One brief note on why this is nourishing.",
  "ingredients": [
    {"amount": "1 cup", "item": "ingredient name"},
    ...
  ],
  "instructions": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "shopping_list": ["item 1", "item 2", ...],
  "tips": "One simple tip to make this dish even better."
}"""
    messages = [{"role": "user", "content": [
        _encode_image(image_bytes, media_type),
        {"type": "text", "text": "What dish is this? Give me the full recipe with ingredients, instructions, and a shopping list."}
    ]}]
    raw = _ask_claude(system, messages, 1500)
    return _safe_parse(raw)

# ── BUILD IT ──────────────────────────────────────────────────────────────────

def build_plan_from_photo(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    system = """You are a patient, skilled craftsman who loves helping regular folks build things themselves.
Your audience loves building — raised garden beds, birdhouses, shelves, gazebos.
Plain English. Very clear step-by-step instructions. Assume basic tool knowledge.
Respond ONLY with valid JSON:
{
  "project_name": "What this structure is",
  "description": "2-3 warm sentences about this project.",
  "skill_level": "Beginner / Intermediate / Advanced",
  "estimated_time": "How long this project takes",
  "estimated_cost": "Rough cost estimate in dollars",
  "dimensions": "Approximate dimensions of the structure",
  "tools_needed": ["tool 1", "tool 2", ...],
  "materials": [
    {"quantity": "8", "item": "2x4 lumber, 8 feet"},
    ...
  ],
  "instructions": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "tips": ["tip 1", "tip 2"],
  "shopping_list": ["item 1", "item 2", ...]
}"""
    messages = [{"role": "user", "content": [
        _encode_image(image_bytes, media_type),
        {"type": "text", "text": "What is this structure? Give me a complete build plan with materials list and step-by-step instructions."}
    ]}]
    raw = _ask_claude(system, messages, 1500)
    return _safe_parse(raw)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def _safe_parse(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned.strip())
    except Exception as e:
        return {"error": str(e), "raw": raw}
