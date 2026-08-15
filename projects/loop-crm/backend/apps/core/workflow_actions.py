"""Concrete, auditable actions for Loop-CRM workflow runs.

Actions are deliberately explicit and idempotent where possible. A missing
trigger object is recorded as ``skipped`` rather than creating fake data or
claiming an external provider call succeeded.
"""
from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.core.integrations import EmailConnector, SlackConnector
from apps.core.realtime import safe_publish_workspace_event
from apps.core.webhooks import post_json, sign_payload


def _same_workspace(obj: Any, workspace_id: int | None) -> bool:
    return bool(obj and workspace_id and obj.workspace_id == workspace_id)


def _decimal(value: Any, fallback: Decimal = Decimal("0.00")) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return fallback


def _publish(workspace_id: int | None, event: str, resource: str, pk: int) -> None:
    """Emit a workspace resource event so realtime dashboards refresh.

    Workflow actions run in the Dramatiq worker (and via the manual run
    endpoint), so they bypass the HTTP mutation views that normally publish.
    """
    safe_publish_workspace_event(workspace_id, event, {"resource": resource, "pk": pk})


def execute_action(action: str, run: Any) -> dict[str, Any]:
    payload = run.trigger_payload or {}
    workspace_id = run.workspace_id

    if action == "assign_owner":
        from apps.crm.models import Contact, Deal

        owner_id = payload.get("owner_id") or getattr(run.definition, "created_by_id", None)
        if not owner_id:
            return {"name": action, "status": "skipped", "reason": "No owner was supplied."}
        deal = Deal.objects.filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        contact = Contact.objects.filter(pk=payload.get("contact_id"), workspace_id=workspace_id).first()
        updated = []
        if deal and deal.owner_id is None:
            deal.owner_id = owner_id
            deal.save(update_fields=["owner", "updated_at"])
            updated.append("deal")
        if contact and contact.owner_id is None:
            contact.owner_id = owner_id
            contact.save(update_fields=["owner", "updated_at"])
            updated.append("contact")
        return {"name": action, "status": "completed" if updated else "skipped", "updated": updated}

    if action == "create_activity":
        from apps.crm.models import Activity, Contact, Deal

        deal = Deal.objects.filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        if not deal:
            return {"name": action, "status": "skipped", "reason": "A workspace deal is required."}
        contact = Contact.objects.filter(pk=payload.get("contact_id"), workspace_id=workspace_id).first()
        activity, created = Activity.objects.get_or_create(
            workspace_id=workspace_id,
            deal=deal,
            contact=contact,
            activity_type="task",
            subject=payload.get("activity_subject", "Follow up on new lead"),
            defaults={"description": "Created by a Loop CRM workflow.", "created_by_id": run.definition.created_by_id},
        )
        return {"name": action, "status": "completed", "activity_id": activity.pk, "created": created}

    if action == "record_touchpoint":
        from apps.attribution.models import AttributionTouchpoint
        from apps.crm.models import Deal
        from apps.marketing.models import Post

        deal = Deal.objects.filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        post = Post.objects.select_related("campaign").filter(pk=payload.get("post_id"), workspace_id=workspace_id).first()
        if not deal or not post:
            return {"name": action, "status": "skipped", "reason": "A workspace deal and post are required."}
        touchpoint, created = AttributionTouchpoint.objects.get_or_create(
            workspace_id=workspace_id,
            deal=deal,
            post=post,
            defaults={"campaign": post.campaign, "source": post.channel.platform, "occurred_at": timezone.now()},
        )
        _publish(workspace_id, "resource.created" if created else "resource.updated", "touchpoints", touchpoint.pk)
        return {"name": action, "status": "completed", "touchpoint_id": touchpoint.pk, "created": created}

    if action == "recalculate_attribution":
        from apps.attribution.engines.calculator import AttributionCalculator
        from apps.crm.models import Deal

        deal = Deal.objects.filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        if not deal:
            return {"name": action, "status": "skipped", "reason": "A workspace deal is required."}
        AttributionCalculator.calculate_for_deal(deal.pk, payload.get("model_type", "linear"))
        return {"name": action, "status": "completed", "deal_id": deal.pk}

    if action == "update_campaign_roi":
        from apps.crm.models import Deal
        from apps.finance.models import RevenueEvent

        deal = Deal.objects.select_related("campaign").filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        if not deal or not deal.is_won:
            return {"name": action, "status": "skipped", "reason": "A closed-won workspace deal is required."}
        event, created = RevenueEvent.objects.get_or_create(
            workspace_id=workspace_id,
            deal=deal,
            kind="deal_won",
            defaults={"campaign": deal.campaign, "amount": deal.value, "metadata": {"source": "workflow"}},
        )
        _publish(workspace_id, "resource.created" if created else "resource.updated", "revenue", event.pk)
        return {"name": action, "status": "completed", "revenue_event_id": event.pk, "created": created}

    if action == "create_invoice":
        from apps.crm.models import Deal
        from apps.finance.models import Invoice

        deal = Deal.objects.select_related("company", "contact").filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        if not deal or not deal.is_won:
            return {"name": action, "status": "skipped", "reason": "A closed-won workspace deal is required."}
        invoice, created = Invoice.objects.get_or_create(
            workspace_id=workspace_id,
            number=f"DEAL-{deal.pk}",
            defaults={
                "company": deal.company,
                "contact": deal.contact,
                "deal": deal,
                "currency": deal.workspace.currency,
                "status": "issued",
                "issued_on": timezone.localdate(),
                "due_on": timezone.localdate() + timedelta(days=30),
                "subtotal": deal.value,
                "tax": 0,
                "created_by_id": run.definition.created_by_id,
            },
        )
        _publish(workspace_id, "resource.created" if created else "resource.updated", "invoices", invoice.pk)
        return {"name": action, "status": "completed", "invoice_id": invoice.pk, "created": created}

    if action == "mark_invoice_overdue":
        from apps.finance.models import Invoice

        invoice = Invoice.objects.filter(pk=payload.get("invoice_id"), workspace_id=workspace_id).first()
        if not invoice:
            return {"name": action, "status": "skipped", "reason": "A workspace invoice is required."}
        if invoice.status in {"paid", "void", "overdue"} or not invoice.is_overdue:
            return {"name": action, "status": "skipped", "reason": "The invoice is not newly overdue."}
        invoice.status = "overdue"
        invoice.save(update_fields=["status", "updated_at"])
        _publish(workspace_id, "resource.updated", "invoices", invoice.pk)
        return {"name": action, "status": "completed", "invoice_id": invoice.pk}

    if action == "record_payment":
        from apps.finance.models import Invoice, Payment

        invoice = Invoice.objects.filter(pk=payload.get("invoice_id"), workspace_id=workspace_id).first()
        if not invoice:
            return {"name": action, "status": "skipped", "reason": "A workspace invoice is required."}
        amount = _decimal(payload.get("amount"))
        if amount <= 0:
            return {"name": action, "status": "skipped", "reason": "A positive payment amount is required."}
        reference = str(payload.get("reference") or f"wf-payment-{invoice.pk}")
        payment, created = Payment.objects.get_or_create(
            workspace_id=workspace_id,
            invoice=invoice,
            reference=reference,
            defaults={
                "amount": amount,
                "method": payload.get("method") or "bank_transfer",
                "paid_on": timezone.localdate(),
                "created_by_id": run.definition.created_by_id,
            },
        )
        invoice.refresh_from_db()
        if invoice.outstanding <= 0:
            invoice.status = "paid"
        elif invoice.status not in {"paid", "void"}:
            invoice.status = "partially_paid"
        invoice.save(update_fields=["status", "updated_at"])
        _publish(workspace_id, "resource.created" if created else "resource.updated", "payments", payment.pk)
        _publish(workspace_id, "resource.updated", "invoices", invoice.pk)
        return {"name": action, "status": "completed", "payment_id": payment.pk, "created": created, "invoice_status": invoice.status}

    if action == "reconcile_pos_sale":
        from apps.pos.models import PosSale
        from apps.pos.services import reconcile_pos_sale

        pos_sale = PosSale.objects.filter(pk=payload.get("pos_sale_id"), workspace_id=workspace_id).first()
        if pos_sale is None and payload.get("external_id"):
            pos_sale = PosSale.objects.filter(workspace_id=workspace_id, external_id=payload["external_id"]).first()
        if pos_sale is None:
            return {"name": action, "status": "skipped", "reason": "A workspace POS sale is required."}
        result = reconcile_pos_sale(pos_sale)
        safe_publish_workspace_event(
            workspace_id, "resource.updated", {"resource": "revenue", "pos_sale_id": pos_sale.pk}
        )
        return {"name": action, "status": "completed", **result}

    if action == "create_follow_up_task":
        from apps.crm.models import Activity, Deal

        deal = Deal.objects.filter(pk=payload.get("deal_id"), workspace_id=workspace_id).first()
        if not deal:
            return {"name": action, "status": "skipped", "reason": "A workspace deal is required."}
        due_days = max(int(_decimal(payload.get("due_in_days"), fallback=Decimal("3"))), 0)
        scheduled = timezone.now() + timedelta(days=due_days)
        activity, created = Activity.objects.get_or_create(
            workspace_id=workspace_id,
            deal=deal,
            activity_type="task",
            subject=payload.get("task_subject") or "Follow up on deal",
            defaults={
                "description": "Created by a Loop CRM workflow.",
                "scheduled_at": scheduled,
                "status": "pending",
                "created_by_id": run.definition.created_by_id,
            },
        )
        return {"name": action, "status": "completed", "activity_id": activity.pk, "created": created}

    if action == "send_email":
        recipient = payload.get("to") or payload.get("email")
        if not recipient:
            return {"name": action, "status": "skipped", "reason": "A recipient email is required."}
        EmailConnector().send(
            payload.get("subject") or "Loop CRM notification",
            payload.get("body") or "",
            [recipient],
        )
        return {"name": action, "status": "completed", "to": recipient}

    if action == "send_slack":
        connector = SlackConnector(payload.get("slack_webhook_url"))
        if not connector.configured:
            return {"name": action, "status": "deferred", "reason": "No Slack webhook URL is configured."}
        status, body = connector.post(payload.get("text") or payload.get("subject") or "Loop CRM notification")
        if status not in (200, 201, 204):
            return {"name": action, "status": "failed", "reason": body.get("detail") or f"Slack returned HTTP {status}."}
        return {"name": action, "status": "completed"}

    if action == "call_webhook":
        url = payload.get("webhook_url")
        if not url:
            return {"name": action, "status": "skipped", "reason": "A webhook URL is required."}
        body = payload.get("webhook_payload") or payload
        secret = str(payload.get("webhook_secret") or "")
        headers = {}
        if secret:
            raw = json.dumps(body, sort_keys=True).encode("utf-8")
            headers["X-Loop-Signature"] = sign_payload(secret, raw)
        status, response = post_json(url, body, headers=headers)
        if status not in (200, 201, 202, 204):
            return {"name": action, "status": "failed", "reason": response.get("detail") or f"Webhook returned HTTP {status}."}
        return {"name": action, "status": "completed", "http_status": status}

    if action == "refresh_analytics":
        from apps.marketing.connectors import connector_for
        from apps.marketing.models import Post, PostAnalytics

        post = Post.objects.select_related("channel").filter(pk=payload.get("post_id"), workspace_id=workspace_id).first()
        if not post:
            return {"name": action, "status": "skipped", "reason": "A workspace post is required."}
        metrics = connector_for(post.channel.platform, channel=post.channel).fetch_analytics(post)
        if not metrics:
            return {"name": action, "status": "deferred", "reason": "Provider analytics are unavailable for this post."}
        PostAnalytics.objects.update_or_create(
            post=post,
            defaults={
                "impressions": int(metrics.get("impressions") or 0),
                "clicks": int(metrics.get("clicks") or 0),
                "likes": int(metrics.get("likes") or 0),
                "comments": int(metrics.get("comments") or 0),
                "shares": int(metrics.get("shares") or 0),
            },
        )
        return {"name": action, "status": "completed", "post_id": post.pk}

    if action in {"publish_to_channels", "request_approval", "notify_sales", "notify_marketing_manager", "notify_revops"}:
        # These are integration boundaries. They become completed only when a
        # connector/notification actor has a concrete provider implementation.
        return {"name": action, "status": "deferred", "reason": "Provider actor is not configured."}

    return {"name": action, "status": "skipped", "reason": "Unknown action."}


def execute_run(run: Any) -> list[dict[str, Any]]:
    """Execute all declared actions in one transaction and return the ledger."""
    with transaction.atomic():
        return [execute_action(action, run) for action in (run.definition.actions or [])]
