"""Stripe-backed SaaS billing services for Loop-CRM.

All Stripe access is gated behind ``billing_configured()``: with empty
``STRIPE_SECRET_KEY`` the checkout/portal/webhook roads return an honest
"billing not configured" state instead of raising. The webhook verifies the
Stripe signature and is idempotent through the ``RevenueEvent.external_ref``
unique constraint (one recognized SaaS revenue event per Stripe invoice).
"""
from __future__ import annotations

import logging
from decimal import Decimal

import stripe
from django.conf import settings
from django.utils import timezone

from apps.billing.gates import billing_configured
from apps.billing.models import BillingAccount, Plan, Seat

logger = logging.getLogger("loop.billing")


def _stripe():
    """Return a configured Stripe client, or None when billing is disabled."""
    if not billing_configured():
        return None
    client = getattr(_stripe, "_client", None)
    if client is None:
        client = stripe  # module-level client reads STRIPE_SECRET_KEY at call time
    return client


def plan_catalog() -> list[dict]:
    """Public tier catalog consumed by ``/apis/billing/plans/``.

    Mirrors the Wagtail pricing copy's *data*: enforceables live here, prose
    stays in the editor. ``checkout`` hrefs route to ``/billing/checkout/``.
    """
    catalog = []
    for plan in Plan.objects.filter(is_active=True).order_by("price_cents", "name"):
        catalog.append(
            {
                "slug": plan.slug,
                "name": plan.name,
                "price_cents": plan.price_cents,
                "price": plan.monthly_price_dollars,
                "period": plan.period,
                "seat_limit": plan.seat_limit,
                "feature_flags": plan.feature_flags or {},
                "checkout": f"/billing/checkout/?plan={plan.slug}&period={plan.period}",
            }
        )
    return catalog


def account_payload(account: BillingAccount | None, workspace_id: int | None) -> dict:
    """The authenticated ``/apis/billing/account/`` contract for /settings/plan/."""
    if account is None:
        return {
            "configured": billing_configured(),
            "workspace_id": workspace_id,
            "status": "none",
            "plan": None,
            "seats": 0,
        }
    seats = Seat.objects.filter(workspace_id=account.workspace_id).count()
    return {
        "configured": billing_configured(),
        "workspace_id": account.workspace_id,
        "status": account.status,
        "trial_ends_at": account.trial_ends_at.isoformat() if account.trial_ends_at else None,
        "plan": {
            "slug": account.plan.slug,
            "name": account.plan.name,
            "period": account.plan.period,
            "seat_limit": account.plan.seat_limit,
        }
        if account.plan
        else None,
        "seats": seats,
    }


def ensure_account(workspace_id: int) -> BillingAccount:
    """Get (or create) the workspace's billing account."""
    account, _ = BillingAccount.objects.get_or_create(workspace_id=workspace_id)
    return account


def ensure_customer(account: BillingAccount) -> str:
    """Return the Stripe customer id, creating one when it does not exist yet."""
    client = _stripe()
    if client is None:
        return ""
    if not account.stripe_customer_id:
        customer = client.Customer.create(
            name=account.workspace.name,
            metadata={"workspace_id": str(account.workspace_id)},
        )
        account.stripe_customer_id = customer["id"]
        account.save(update_fields=["stripe_customer_id", "updated_at"])
    return account.stripe_customer_id


def _price_id_for(plan: Plan, period: str) -> str:
    """Resolve the Stripe price id for a plan period.

    A single Stripe price id covers both periods when only one is configured
    (the catalog is seedable without live Stripe prices).
    """
    return plan.stripe_price_id or ""


def create_checkout_session(
    account: BillingAccount,
    plan: Plan,
    period: str,
    quantity: int = 1,
) -> dict:
    """Create a Stripe Checkout Session and return its client-safe payload."""
    client = _stripe()
    if client is None:
        return {"configured": False}
    customer_id = ensure_customer(account)
    price_id = _price_id_for(plan, period)
    if not price_id:
        return {"configured": True, "error": "This plan has no Stripe price configured yet."}

    success_url = settings.PUBLIC_SITE_URL.rstrip("/") + "/settings/plan/?checkout=success"
    cancel_url = settings.PUBLIC_SITE_URL.rstrip("/") + "/settings/plan/?checkout=canceled"
    session = client.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": max(1, quantity)}],
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={"metadata": {"workspace_id": str(account.workspace_id)}},
        metadata={"workspace_id": str(account.workspace_id), "plan": plan.slug},
    )
    return {"configured": True, "url": session["url"]}


def create_portal_session(account: BillingAccount) -> dict:
    """Create a Stripe Billing Portal session for self-service plan changes."""
    client = _stripe()
    if client is None:
        return {"configured": False}
    customer_id = ensure_customer(account)
    return_url = settings.PUBLIC_SITE_URL.rstrip("/") + "/settings/plan/"
    session = client.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return {"configured": True, "url": session["url"]}


def handle_webhook(payload: bytes, signature: str) -> tuple[bool, str | None]:
    """Verify and process a Stripe webhook. Returns (ok, error_message)."""
    client = _stripe()
    if client is None:
        return False, "Billing is not configured."
    if not settings.STRIPE_WEBHOOK_SECRET:
        return False, "STRIPE_WEBHOOK_SECRET is not set."
    try:
        event = client.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as exc:  # noqa: BLE001
        return False, f"Invalid webhook signature: {exc}"

    event_type = event["type"]
    data = event["data"]["object"]
    if event_type == "customer.subscription.updated":
        _apply_subscription(data)
    elif event_type == "customer.subscription.deleted":
        _apply_subscription(data, canceled=True)
    elif event_type == "invoice.payment_succeeded":
        _apply_invoice_paid(data)
    return True, None


def _account_for_subscription(subscription_id: str) -> BillingAccount | None:
    return (
        BillingAccount.objects.select_related("workspace")
        .filter(stripe_subscription_id=subscription_id)
        .first()
    )


def _apply_subscription(subscription, canceled: bool = False) -> None:
    account = _account_for_subscription(subscription["id"])
    if account is None:
        return
    if canceled or subscription.get("status") == "canceled":
        account.status = "canceled"
    elif subscription.get("status") == "past_due":
        account.status = "past_due"
    elif subscription.get("status") in {"active", "trialing"}:
        account.status = "active"
    account.save(update_fields=["status", "updated_at"])


def _apply_invoice_paid(invoice) -> None:
    """Recognize SaaS revenue from a paid Stripe invoice (idempotent)."""
    from apps.finance.models import RevenueEvent

    subscription_id = invoice.get("subscription")
    workspace_id = (invoice.get("metadata") or {}).get("workspace_id")
    if workspace_id is not None:
        account = BillingAccount.objects.select_related("workspace").filter(
            workspace_id=int(workspace_id)
        ).first()
    else:
        account = _account_for_subscription(subscription_id) if subscription_id else None
    if account is None:
        return
    account.status = "active"
    account.stripe_subscription_id = subscription_id or account.stripe_subscription_id
    account.save(update_fields=["status", "stripe_subscription_id", "updated_at"])

    amount = invoice.get("amount_paid", 0)
    external_ref = f"stripe:{invoice['id']}"
    _, created = RevenueEvent.objects.get_or_create(
        workspace=account.workspace,
        external_ref=external_ref,
        defaults={
            "kind": "subscription",
            "amount": Decimal(amount) / 100,
            "recognized_on": timezone.localdate(),
            "metadata": {"stripe_invoice_id": invoice["id"], "source": "stripe"},
        },
    )
    if created:
        logger.info("Recognized SaaS revenue %s for workspace %s", external_ref, account.workspace_id)
