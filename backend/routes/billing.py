"""
Stripe billing — checkout + webhook + status.

Free users get FREE_DAILY_LIMIT queries/day. Upgrading to premium
unlocks unlimited usage. Stripe is the source of truth for subscription
status; the local subscriptions table is a cached projection updated
by webhook events.
"""
import os
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth_middleware import get_current_user
from ..db import execute, get_db, query_one
from ..services import quota


router = APIRouter(prefix="/billing", tags=["billing"])


STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
APP_URL = os.environ.get("APP_URL", "")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


def _require_stripe():
    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        raise HTTPException(
            status_code=503,
            detail="Billing not configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID.",
        )


@router.get("/status")
def status(user=Depends(get_current_user)):
    """Frontend polls this to render the quota counter / upgrade button."""
    return {"user": {"email": user["email"]}, **quota.get_status(user["id"])}


@router.post("/create-checkout-session")
def create_checkout_session(request: Request, user=Depends(get_current_user)):
    """Create a Stripe Checkout Session for the premium subscription."""
    _require_stripe()
    base = APP_URL or str(request.base_url).rstrip("/")
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            customer_email=user["email"] or None,
            success_url=f"{base}/?upgraded=1",
            cancel_url=f"{base}/?upgrade=cancel",
            metadata={"user_id": user["id"], "email": user["email"] or ""},
            subscription_data={"metadata": {"user_id": user["id"]}},
            allow_promotion_codes=True,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message or str(e)}")
    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Stripe webhook — verifies signature, updates subscription state."""
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured.")
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")

    etype = event["type"]
    obj = event["data"]["object"]

    if etype == "checkout.session.completed":
        user_id = (obj.get("metadata") or {}).get("user_id")
        email = (obj.get("metadata") or {}).get("email") or obj.get("customer_email") or ""
        sub_id = obj.get("subscription")
        customer_id = obj.get("customer")
        if user_id and sub_id:
            sub = stripe.Subscription.retrieve(sub_id)
            _upsert_subscription(user_id, email, customer_id, sub)

    elif etype in ("customer.subscription.updated", "customer.subscription.created"):
        user_id = (obj.get("metadata") or {}).get("user_id")
        if user_id:
            _upsert_subscription(user_id, "", obj.get("customer"), obj)

    elif etype == "customer.subscription.deleted":
        user_id = (obj.get("metadata") or {}).get("user_id")
        if user_id:
            with get_db() as conn:
                execute(
                    conn,
                    "UPDATE subscriptions SET status = 'canceled', updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    [user_id],
                )

    return {"received": True}


def _upsert_subscription(user_id: str, email: str, customer_id: str, sub) -> None:
    status_str = sub.get("status") if isinstance(sub, dict) else sub.status
    period_end_ts = sub.get("current_period_end") if isinstance(sub, dict) else sub.current_period_end
    sub_id = sub.get("id") if isinstance(sub, dict) else sub.id
    period_end_iso = (
        datetime.fromtimestamp(period_end_ts, tz=timezone.utc).isoformat()
        if period_end_ts
        else None
    )
    with get_db() as conn:
        existing = query_one(conn, "SELECT user_id FROM subscriptions WHERE user_id = ?", [user_id])
        if existing:
            execute(
                conn,
                """UPDATE subscriptions
                   SET email = COALESCE(NULLIF(?, ''), email),
                       stripe_customer_id = ?,
                       stripe_subscription_id = ?,
                       status = ?,
                       current_period_end = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE user_id = ?""",
                [email, customer_id, sub_id, status_str, period_end_iso, user_id],
            )
        else:
            execute(
                conn,
                """INSERT INTO subscriptions
                   (user_id, email, stripe_customer_id, stripe_subscription_id, status, current_period_end)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [user_id, email, customer_id, sub_id, status_str, period_end_iso],
            )
