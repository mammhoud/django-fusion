"""Outbound webhook plumbing: HMAC signing, JSON POST, and dispatch.

``dispatch_webhooks`` is the single entry point domain code calls when a
webhook-worthy event happens. It creates one :class:`WebhookDelivery` per
subscribed active webhook and enqueues ``deliver_webhook``; the actor signs the
payload with ``sign_payload`` and posts it with retry backoff + a dead-letter
terminal state. A workspace with no webhooks short-circuits without touching
the broker.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import urllib.error
import urllib.request
from typing import Any

#: Number of attempts before a delivery is moved to the dead letter.
MAX_ATTEMPTS = 3

#: Domain events Loop-CRM can emit to subscribed webhooks.
SUPPORTED_EVENTS: tuple[str, ...] = (
    "deal_won",
    "post_published",
    "payment_received",
    "pos_sale_ingested",
)


def sign_payload(secret: str, raw_body: bytes) -> str:
    """Return the ``sha256=<hex>`` HMAC signature for a raw JSON body."""
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def post_json(url: str, payload: dict, headers: dict | None = None) -> tuple[int, dict]:
    """POST JSON via stdlib ``urllib``; returns ``(status, body)``, capturing errors."""
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    request = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/json", **(headers or {})},
        data=raw,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read().decode("utf-8", errors="replace"))
        except (ValueError, TypeError):
            return exc.code, {}
    except urllib.error.URLError as exc:
        return 0, {"detail": f"Network error: {exc.reason}"}


def dispatch_webhooks(workspace_id: int | None, event: str, payload: dict[str, Any]) -> int:
    """Create + enqueue deliveries for every subscribed active webhook.

    Returns the number of deliveries created. A webhook whose ``events`` list
    is empty subscribes to every event. Enqueue failures are recorded on the
    delivery (dead) rather than raising, so realtime/domain writes never break.
    """
    if workspace_id is None or event not in SUPPORTED_EVENTS:
        return 0
    from .models import Webhook, WebhookDelivery

    webhooks = list(Webhook.objects.filter(workspace_id=workspace_id, is_active=True))
    created = 0
    for webhook in webhooks:
        if webhook.events and event not in webhook.events:
            continue
        delivery = WebhookDelivery.objects.create(webhook=webhook, event=event, payload=payload)
        _enqueue_delivery(delivery)
        created += 1
    return created


def _enqueue_delivery(delivery: Any) -> None:
    """Best-effort enqueue; an unreachable broker marks the delivery dead.

    Mirrors ``trigger_workflow``: probe the broker (cached, so a down broker is
    skipped once per window instead of per delivery) before the ``.send()``
    round-trip, and dead-letter immediately when it is unreachable.
    """
    from plugins.workers.tasks import broker_reachable, deliver_webhook

    if not broker_reachable():
        delivery.status = "dead"
        delivery.last_error = "Webhook queue unavailable: broker unreachable"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
        return
    try:
        deliver_webhook.send(delivery.pk)
    except Exception as exc:  # noqa: BLE001 - webhook delivery is non-critical
        delivery.status = "dead"
        delivery.last_error = f"Webhook queue unavailable: {exc.__class__.__name__}"
        delivery.save(update_fields=["status", "last_error", "updated_at"])
