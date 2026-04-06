"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""

import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition
)

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "garden@thegoodneighborguard.com")
FROM_NAME = "Garden & Grace"
APP_URL = os.environ.get("APP_URL", "https://garden-and-grace.onrender.com")

def send_magic_link(to_email: str, name: str, token: str) -> bool:
    """Send a magic link login email."""
    magic_url = f"{APP_URL}/auth/verify?token={token}"
    html_content = f"""
    <div style="font-family: Georgia, serif; max-width: 520px; margin: 0 auto; padding: 32px; background: #faf6ef; border-radius: 12px;">
      <div style="text-align: center; margin-bottom: 24px;">
        <h1 style="color: #3d6b3f; font-size: 28px; margin: 0;">🌿 Garden &amp; Grace</h1>
        <p style="color: #7a5c3a; font-size: 14px; margin: 8px 0 0;">A gift made with love</p>
      </div>
      <p style="color: #333; font-size: 18px;">Good day, {name}! 🌸</p>
      <p style="color: #555; font-size: 16px; line-height: 1.6;">
        Tap the button below to open your Garden &amp; Grace app. You won't need to log in again after this.
      </p>
      <div style="text-align: center; margin: 32px 0;">
        <a href="{magic_url}"
           style="background: #3d6b3f; color: white; padding: 18px 36px; border-radius: 8px;
                  text-decoration: none; font-size: 18px; font-family: Georgia, serif;">
          Open Garden &amp; Grace 🌿
        </a>
      </div>
      <p style="color: #999; font-size: 13px; text-align: center; margin-top: 24px;">
        This link expires in 24 hours. If you didn't request this, you can ignore it.
      </p>
      <hr style="border: 1px solid #e0d5c5; margin: 24px 0;" />
      <p style="color: #c9953a; font-style: italic; text-align: center; font-size: 14px;">
        "This is the day which the LORD hath made; we will rejoice and be glad in it."<br>
        <span style="color: #7a5c3a;">— Psalm 118:24</span>
      </p>
      <p style="color: #bbb; font-size: 11px; text-align: center; margin-top: 16px;">
        Made with love by Chris · The Good Neighbor Guard
      </p>
    </div>
    """

    message = Mail(
        from_email=(FROM_EMAIL, FROM_NAME),
        to_emails=to_email,
        subject="🌿 Your Garden & Grace link is ready",
        html_content=html_content
    )
    return _send(message)


def send_pdf_email(to_email: str, name: str, subject: str, body_html: str,
                   pdf_bytes: bytes, pdf_filename: str) -> bool:
    """Send a PDF attachment email."""
    encoded = base64.b64encode(pdf_bytes).decode()
    attachment = Attachment(
        FileContent(encoded),
        FileName(pdf_filename),
        FileType("application/pdf"),
        Disposition("attachment")
    )
    message = Mail(
        from_email=(FROM_EMAIL, FROM_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=body_html
    )
    message.attachment = attachment
    return _send(message)


def send_recipe_pdf(to_email: str, name: str, dish_name: str, pdf_bytes: bytes) -> bool:
    body = f"""
    <div style="font-family: Georgia, serif; max-width: 520px; margin: 0 auto; padding: 32px; background: #faf6ef; border-radius: 12px;">
      <h1 style="color: #3d6b3f;">🍽️ Your Recipe is Ready, {name}!</h1>
      <p style="font-size: 16px; color: #555;">Here's your <strong>{dish_name}</strong> recipe with a full shopping list — all attached as a beautiful PDF.</p>
      <p style="color: #c9953a; font-style: italic;">"O taste and see that the LORD is good." — Psalm 34:8</p>
      <p style="color: #bbb; font-size: 11px;">Made with love by Chris · The Good Neighbor Guard</p>
    </div>
    """
    safe_name = dish_name.replace(" ", "_").replace("/", "-")[:40]
    return send_pdf_email(
        to_email, name,
        f"🍽️ {dish_name} — Recipe & Shopping List",
        body,
        pdf_bytes,
        f"Recipe_{safe_name}.pdf"
    )


def send_build_pdf(to_email: str, name: str, project_name: str, pdf_bytes: bytes) -> bool:
    body = f"""
    <div style="font-family: Georgia, serif; max-width: 520px; margin: 0 auto; padding: 32px; background: #faf6ef; border-radius: 12px;">
      <h1 style="color: #3d6b3f;">🔨 Your Build Plan is Ready, {name}!</h1>
      <p style="font-size: 16px; color: #555;">Here's your complete <strong>{project_name}</strong> plan with materials list and step-by-step instructions.</p>
      <p style="color: #c9953a; font-style: italic;">"Except the LORD build the house, they labour in vain that build it." — Psalm 127:1</p>
      <p style="color: #bbb; font-size: 11px;">Made with love by Chris · The Good Neighbor Guard</p>
    </div>
    """
    safe_name = project_name.replace(" ", "_").replace("/", "-")[:40]
    return send_pdf_email(
        to_email, name,
        f"🔨 {project_name} — Build Plan",
        body,
        pdf_bytes,
        f"BuildPlan_{safe_name}.pdf"
    )


def _send(message: Mail) -> bool:
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in (200, 201, 202)
    except Exception as e:
        print(f"[Email Error] {e}")
        return False
