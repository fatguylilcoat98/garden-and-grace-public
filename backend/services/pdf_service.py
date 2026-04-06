"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

# Brand colors
FOREST_GREEN = HexColor("#3d6b3f")
WARM_GOLD = HexColor("#c9953a")
SOFT_BROWN = HexColor("#7a5c3a")
CREAM = HexColor("#faf6ef")
LIGHT_GREEN = HexColor("#e8f2e8")

def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="GNG_Title",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=FOREST_GREEN,
        spaceAfter=6,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="GNG_Subtitle",
        fontName="Helvetica",
        fontSize=13,
        textColor=SOFT_BROWN,
        spaceAfter=4,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="GNG_Section",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=FOREST_GREEN,
        spaceBefore=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="GNG_Body",
        fontName="Helvetica",
        fontSize=11,
        textColor=black,
        spaceAfter=4,
        leading=16,
    ))
    styles.add(ParagraphStyle(
        name="GNG_Verse",
        fontName="Helvetica-Oblique",
        fontSize=12,
        textColor=SOFT_BROWN,
        spaceAfter=4,
        alignment=TA_CENTER,
        leading=18,
    ))
    styles.add(ParagraphStyle(
        name="GNG_Footer",
        fontName="Helvetica",
        fontSize=9,
        textColor=SOFT_BROWN,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="GNG_Step",
        fontName="Helvetica",
        fontSize=11,
        textColor=black,
        spaceAfter=6,
        leading=16,
        leftIndent=12,
    ))
    return styles

def _divider():
    return HRFlowable(width="100%", thickness=1, color=WARM_GOLD, spaceAfter=8, spaceBefore=8)

def _header(styles, title: str, subtitle: str = "") -> list:
    elements = []
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("🌿 Garden &amp; Grace", styles["GNG_Subtitle"]))
    elements.append(Paragraph(title, styles["GNG_Title"]))
    if subtitle:
        elements.append(Paragraph(subtitle, styles["GNG_Subtitle"]))
    elements.append(_divider())
    return elements

def _footer_elements(styles, verse: dict, recipient_name: str = "") -> list:
    elements = []
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(_divider())
    greeting = f"For {recipient_name} — " if recipient_name else ""
    elements.append(Paragraph(f'"{verse["verse"]}"', styles["GNG_Verse"]))
    elements.append(Paragraph(f'— {verse["ref"]}', styles["GNG_Verse"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(
        f"{greeting}Made with love by Chris · The Good Neighbor Guard · Truth · Safety · We Got Your Back",
        styles["GNG_Footer"]
    ))
    return elements

def generate_recipe_pdf(recipe: dict, verse: dict, recipient_name: str = "") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = _base_styles()
    elements = []

    # Header
    elements += _header(
        styles,
        recipe.get("dish_name", "Recipe"),
        f"Serves {recipe.get('serves', '')}  ·  Prep: {recipe.get('prep_time', '')}  ·  Cook: {recipe.get('cook_time', '')}"
    )

    # Description
    if recipe.get("description"):
        elements.append(Paragraph(recipe["description"], styles["GNG_Body"]))
    if recipe.get("health_note"):
        elements.append(Paragraph(f"💚 {recipe['health_note']}", styles["GNG_Body"]))
    elements.append(Spacer(1, 0.1 * inch))

    # Ingredients
    elements.append(Paragraph("Ingredients", styles["GNG_Section"]))
    for ing in recipe.get("ingredients", []):
        line = f"• <b>{ing.get('amount', '')}</b>  {ing.get('item', '')}"
        elements.append(Paragraph(line, styles["GNG_Body"]))

    # Instructions
    elements.append(Paragraph("Instructions", styles["GNG_Section"]))
    for i, step in enumerate(recipe.get("instructions", []), 1):
        clean_step = step.lstrip("0123456789. ").lstrip("Step :").strip()
        elements.append(Paragraph(f"<b>{i}.</b>  {clean_step}", styles["GNG_Step"]))

    if recipe.get("tips"):
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(f"✨ Tip: {recipe['tips']}", styles["GNG_Body"]))

    # Shopping list
    elements.append(Paragraph("Shopping List", styles["GNG_Section"]))
    shopping = recipe.get("shopping_list", [])
    if shopping:
        half = len(shopping) // 2 + len(shopping) % 2
        col1 = [Paragraph(f"☐  {item}", styles["GNG_Body"]) for item in shopping[:half]]
        col2 = [Paragraph(f"☐  {item}", styles["GNG_Body"]) for item in shopping[half:]]
        # Pad shorter column
        while len(col2) < len(col1):
            col2.append(Paragraph("", styles["GNG_Body"]))
        table_data = list(zip(col1, col2))
        t = Table(table_data, colWidths=[3.0 * inch, 3.0 * inch])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

    elements += _footer_elements(styles, verse, recipient_name)
    doc.build(elements)
    return buffer.getvalue()


def generate_build_pdf(plan: dict, verse: dict, recipient_name: str = "") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = _base_styles()
    elements = []

    # Header
    elements += _header(
        styles,
        plan.get("project_name", "Build Plan"),
        f"{plan.get('skill_level', '')}  ·  {plan.get('estimated_time', '')}  ·  Est. cost: {plan.get('estimated_cost', '')}"
    )

    if plan.get("description"):
        elements.append(Paragraph(plan["description"], styles["GNG_Body"]))
    if plan.get("dimensions"):
        elements.append(Paragraph(f"📐 Dimensions: {plan['dimensions']}", styles["GNG_Body"]))
    elements.append(Spacer(1, 0.1 * inch))

    # Tools
    if plan.get("tools_needed"):
        elements.append(Paragraph("Tools Needed", styles["GNG_Section"]))
        tools_text = "  ·  ".join(plan["tools_needed"])
        elements.append(Paragraph(tools_text, styles["GNG_Body"]))

    # Materials
    elements.append(Paragraph("Materials List", styles["GNG_Section"]))
    for mat in plan.get("materials", []):
        line = f"• <b>{mat.get('quantity', '')}</b>  {mat.get('item', '')}"
        elements.append(Paragraph(line, styles["GNG_Body"]))

    # Instructions
    elements.append(Paragraph("Build Instructions", styles["GNG_Section"]))
    for i, step in enumerate(plan.get("instructions", []), 1):
        clean_step = step.lstrip("0123456789. ").lstrip("Step :").strip()
        elements.append(Paragraph(f"<b>{i}.</b>  {clean_step}", styles["GNG_Step"]))

    # Tips
    if plan.get("tips"):
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph("Tips", styles["GNG_Section"]))
        for tip in plan["tips"]:
            elements.append(Paragraph(f"✨  {tip}", styles["GNG_Body"]))

    # Shopping list
    elements.append(Paragraph("Shopping List", styles["GNG_Section"]))
    shopping = plan.get("shopping_list", [])
    if shopping:
        half = len(shopping) // 2 + len(shopping) % 2
        col1 = [Paragraph(f"☐  {item}", styles["GNG_Body"]) for item in shopping[:half]]
        col2 = [Paragraph(f"☐  {item}", styles["GNG_Body"]) for item in shopping[half:]]
        while len(col2) < len(col1):
            col2.append(Paragraph("", styles["GNG_Body"]))
        table_data = list(zip(col1, col2))
        t = Table(table_data, colWidths=[3.0 * inch, 3.0 * inch])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

    elements += _footer_elements(styles, verse, recipient_name)
    doc.build(elements)
    return buffer.getvalue()
