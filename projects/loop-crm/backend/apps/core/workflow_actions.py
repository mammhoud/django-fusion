"""Concrete, auditable actions for Loop-CRM workflow runs.

Actions are deliberately explicit and idempotent where possible. A missing
trigger object is recorded as ``skipped`` rather than creating fake data or
claiming an external provider call succeeded.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone


def _same_workspace(obj: Any, workspace_id: int | None) -> bool:
    return bool(obj and workspace_id and obj.workspace_id == workspace_id)


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
        return {"name": action, "status": "completed", "invoice_id": invoice.pk, "created": created}

    if action in {"publish_to_channels", "request_approval", "notify_sales", "notify_marketing_manager", "notify_revops", "refresh_analytics"}:
        # These are integration boundaries. They become completed only when a
        # connector/notification actor has a concrete provider implementation.
        return {"name": action, "status": "deferred", "reason": "Provider actor is not configured."}

    return {"name": action, "status": "skipped", "reason": "Unknown action."}


def execute_run(run: Any) -> list[dict[str, Any]]:
    """Execute all declared actions in one transaction and return the ledger."""
    with transaction.atomic():
        return [execute_action(action, run) for action in (run.definition.actions or [])]
