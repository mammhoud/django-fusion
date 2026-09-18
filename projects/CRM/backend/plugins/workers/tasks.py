"""Django-Dramatiq actors for the Loop-CRM background boundary."""
from __future__ import annotations

import json
import socket
import time
from urllib.parse import urlparse

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django_fusion.tasks import task

#: How long a broker probe result is reused before re-probing (seconds).
_BROKER_PROBE_TTL = 5.0

_broker_reachable_cache: tuple[float, bool] | None = None


def broker_reachable(timeout: float = 0.4) -> bool:
    """Probe whether the Dramatiq broker answers, cached for a short window.

    ``execute_workflow.send`` performs a Redis round-trip (and, with a down
    broker, a connection error) on every call. Signal-driven tests create
    hundreds of invoices/payments/contacts, so that per-trigger cost adds up.
    This probes once and reuses the answer briefly so a down broker is skipped
    immediately instead of re-attempted on each trigger.
    """
    global _broker_reachable_cache
    now = time.monotonic()
    if _broker_reachable_cache is not None and now - _broker_reachable_cache[0] < _BROKER_PROBE_TTL:
        return _broker_reachable_cache[1]
    reachable = False
    try:
        url = settings.DRAMATIQ_BROKER["OPTIONS"]["url"]
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 6379
        with socket.create_connection((host, port), timeout=timeout):
            reachable = True
    except (OSError, KeyError, TypeError, ValueError):
        reachable = False
    _broker_reachable_cache = (now, reachable)
    return reachable


def broker_gated_send(actor, *args, **kwargs) -> tuple[bool, str]:
    """Best-effort enqueue for a plain actor, gated on broker reachability.

    Returns ``(ok, error)``. A down broker returns ``(False, "broker
    unreachable")`` without the ``.send()`` round-trip; a send failure returns
    ``(False, f"{exc.__class__.__name__}")``; success returns ``(True, "")``.
    Mirrors the gate in ``trigger_workflow``/``_enqueue_delivery`` so every
    sync request path that enqueues an actor fails fast when Redis is down.
    """
    if not broker_reachable():
        return False, "broker unreachable"
    try:
        actor.send(*args, **kwargs)
        return True, ""
    except Exception as exc:  # noqa: BLE001 - normalize any queue failure
        return False, f"{exc.__class__.__name__}"


def _ensure_fresh_channel(channel) -> bool:
    """Refresh an expired OAuth token through the provider adapter.

    Returns True when the channel is usable (token present and, if it had an
    expiry, refreshed). Channels without a token stay untouched so the
    dispatcher's honest ``UnconfiguredConnector`` decides the outcome.
    """
    if not channel.oauth_token:
        return False
    expired = channel.token_expires_at is not None and channel.token_expires_at <= timezone.now()
    if not expired:
        return True
    from apps.marketing.connectors import connector_for

    connector = connector_for(channel.platform, channel=channel)
    refresh = getattr(connector, "refresh", None)
    if callable(refresh):
        refresh()
    channel.refresh_from_db()
    return bool(channel.oauth_token)


@task(queue="marketing")
def publish_post(post_id: int) -> None:
    """Publish a post through its provider-neutral connector."""
    from apps.marketing.connectors import connector_for
    from apps.marketing.models import Post

    post = Post.objects.select_related("channel", "media").get(pk=post_id)
    post.status = "publishing"
    post.save(update_fields=["status", "updated_at"])
    # Refresh a stale OAuth token before publishing; channels without a token
    # fall through to the honest UnconfiguredConnector below.
    if post.channel.oauth_token:
        _ensure_fresh_channel(post.channel)
    # Pass the channel so a configured adapter (LinkedIn/X) runs; without a
    # token the dispatcher returns the honest UnconfiguredConnector.
    result = connector_for(post.channel.platform, channel=post.channel).publish(post)
    if not result.success:
        post.status = "failed"
        post.save(update_fields=["status", "updated_at"])
        return
    post.status = "published"
    post.external_id = result.external_id
    post.save(update_fields=["status", "external_id", "updated_at"])
    trigger_workflow(
        "publish-and-attribute",
        post.workspace_id,
        {"post_id": post.pk, "source": "post.published"},
    )
    from apps.core.webhooks import dispatch_webhooks

    dispatch_webhooks(
        post.workspace_id,
        "post_published",
        {"post_id": post.pk, "channel_id": post.channel_id},
    )


@task(queue="marketing")
def refresh_oauth_token(channel_id: int) -> None:
    """Refresh a connected channel through its provider adapter.

    Adapters without refresh support (or without client credentials) leave
    the channel untouched; the shared BackgroundTaskLog records the attempt.
    """
    from apps.marketing.connectors import connector_for
    from apps.marketing.models import SocialChannel

    channel = SocialChannel.objects.get(pk=channel_id)
    if not channel.oauth_token:
        return
    connector = connector_for(channel.platform, channel=channel)
    refresh = getattr(connector, "refresh", None)
    if callable(refresh):
        refresh()


@task(queue="marketing")
def aggregate_post_analytics(post_id: int) -> None:
    """Fetch and persist per-post metrics through the provider adapter."""
    from apps.marketing.connectors import connector_for
    from apps.marketing.models import Post, PostAnalytics

    post = Post.objects.select_related("channel").get(pk=post_id)
    if not post.external_id:
        return
    connector = connector_for(post.channel.platform, channel=post.channel)
    metrics = connector.fetch_analytics(post)
    if not metrics:
        return
    PostAnalytics.objects.update_or_create(
        post=post,
        defaults={
            "impressions": metrics.get("impressions", 0),
            "clicks": metrics.get("clicks", 0),
            "likes": metrics.get("likes", 0),
            "comments": metrics.get("comments", 0),
            "shares": metrics.get("shares", 0),
        },
    )


@task(queue="finance")
def recalculate_attribution(deal_id: int, model_type: str = "linear") -> None:
    """Reweight a deal's touchpoints with the selected strategy."""
    from apps.attribution.engines.calculator import AttributionCalculator

    AttributionCalculator.calculate_for_deal(deal_id, model_type)


def trigger_workflow(slug: str, workspace_id: int, payload: dict) -> None:
    """Create and queue the best workspace-specific workflow definition."""
    from apps.core.models import WorkflowDefinition, WorkflowRun

    definition = (
        WorkflowDefinition.objects.filter(slug=slug)
        .filter(Q(workspace_id=workspace_id) | Q(workspace__isnull=True))
        .order_by("-workspace_id")
        .first()
    )
    if definition is None or definition.status != "active":
        return
    run = WorkflowRun.objects.create(
        definition=definition,
        workspace_id=workspace_id,
        trigger_payload=payload,
    )
    if not broker_reachable():
        run.status = "failed"
        run.error = "Workflow queue unavailable: broker unreachable"
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error", "finished_at"])
        return
    try:
        execute_workflow.send(run.pk)
    except Exception as exc:  # noqa: BLE001 - persist an honest queue failure
        run.status = "failed"
        run.error = f"Workflow queue unavailable: {exc.__class__.__name__}"
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error", "finished_at"])


@task(queue="crm")
def deliver_webhook(delivery_id: int) -> None:
    """Deliver one webhook: HMAC-signed POST with retry backoff + dead-letter."""
    from apps.core.models import WebhookDelivery
    from apps.core.webhooks import MAX_ATTEMPTS, post_json, sign_payload

    delivery = WebhookDelivery.objects.select_related("webhook").get(pk=delivery_id)
    if delivery.status not in {"queued", "failed"}:
        return
    delivery.attempt_count += 1
    raw = json.dumps(delivery.payload, sort_keys=True).encode("utf-8")
    headers: dict[str, str] = {
        "X-Loop-Event": delivery.event,
        "X-Delivery-Id": str(delivery.pk),
    }
    if delivery.webhook.secret:
        headers["X-Loop-Signature"] = sign_payload(delivery.webhook.secret, raw)
    status, body = post_json(delivery.webhook.url, delivery.payload, headers=headers)

    if status in (200, 201, 202, 204):
        delivery.status = "succeeded"
        delivery.response_status = status
        delivery.last_error = ""
    else:
        delivery.response_status = status or None
        delivery.last_error = str(body.get("detail") or f"HTTP {status}")
        delivery.status = "dead" if delivery.attempt_count >= MAX_ATTEMPTS else "failed"
    delivery.save(update_fields=["status", "response_status", "last_error", "attempt_count", "updated_at"])

    if delivery.status == "failed":
        # Exponential backoff: 2s, then 4s before the final attempt.
        delay_ms = (2 ** delivery.attempt_count) * 1000
        deliver_webhook.send_with_options(args=(delivery.pk,), delay=delay_ms)


@task(queue="crm")
def sync_email_account(account_id: int) -> None:
    """Sync one connected mailbox (Gmail/Outlook) into the CRM timeline.

    Runs the provider connector through ``apps.core.email_sync.sync_account``;
    an unconfigured account returns an honest summary without raising.
    """
    from apps.core.email_sync import sync_account
    from apps.core.models import EmailAccount

    account = EmailAccount.objects.select_related("workspace").get(pk=account_id)
    sync_account(account)


@task(queue="crm")
def execute_workflow(run_id: int) -> None:
    """Execute a declarative workflow and persist every action decision.

    Domain actions remain explicit in the run result instead of being faked:
    provider calls and notifications are dispatched by their own actors as
    those integrations become configured.
    """
    from apps.core.models import WorkflowRun

    run = WorkflowRun.objects.select_related("definition").get(pk=run_id)
    if run.status != "queued":
        return
    run.status = "running"
    run.started_at = timezone.now()
    run.save(update_fields=["status", "started_at"])

    from apps.core.workflow_actions import execute_run

    run.result = {
        "trigger": run.definition.trigger,
        "actions": execute_run(run),
    }
    run.status = "succeeded"
    run.finished_at = timezone.now()
    run.save(update_fields=["result", "status", "finished_at"])


__all__ = [
    "aggregate_post_analytics",
    "deliver_webhook",
    "execute_workflow",
    "sync_email_account",
    "trigger_workflow",
    "publish_post",
    "recalculate_attribution",
    "refresh_oauth_token",
]
