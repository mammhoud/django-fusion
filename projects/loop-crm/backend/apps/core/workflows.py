"""Loop-CRM workflow catalog.

These workflow definitions are intentionally provider-neutral. They describe
triggers and actions in the same way Twenty workflow automation and Postiz
approval/publishing flows do, while Dramatiq remains the execution runtime.
Persisted workflow instances can be added without changing the navigation or
connector contracts.
"""
from __future__ import annotations

from typing import Any

from django.db import OperationalError, ProgrammingError

WORKFLOW_ACTION_CATALOG: tuple[dict[str, str], ...] = (
    {"id": "assign_owner", "label": "Assign owner", "module": "crm"},
    {"id": "create_activity", "label": "Create sales activity", "module": "crm"},
    {"id": "request_approval", "label": "Request approval", "module": "marketing"},
    {"id": "notify_sales", "label": "Notify sales", "module": "crm"},
    {"id": "notify_marketing_manager", "label": "Notify marketing manager", "module": "marketing"},
    {"id": "publish_to_channels", "label": "Publish to connected channels", "module": "marketing"},
    {"id": "record_touchpoint", "label": "Record attribution touchpoint", "module": "attribution"},
    {"id": "refresh_analytics", "label": "Refresh post analytics", "module": "marketing"},
    {"id": "recalculate_attribution", "label": "Recalculate attribution", "module": "attribution"},
    {"id": "update_campaign_roi", "label": "Update campaign revenue", "module": "finance"},
    {"id": "create_invoice", "label": "Create invoice from won deal", "module": "finance"},
    {"id": "notify_revops", "label": "Notify RevOps", "module": "workspace"},
)


WORKFLOW_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "lead-capture",
        "name": "Route a new lead",
        "module": "crm",
        "trigger": "contact.created",
        "actions": ["assign_owner", "create_activity", "notify_sales"],
        "status": "ready",
    },
    {
        "id": "content-approval",
        "name": "Approve scheduled content",
        "module": "marketing",
        "trigger": "post.submitted_for_review",
        "actions": ["request_approval", "notify_marketing_manager"],
        "status": "ready",
    },
    {
        "id": "publish-and-attribute",
        "name": "Publish and create touchpoint",
        "module": "marketing",
        "trigger": "post.published",
        "actions": ["publish_to_channels", "record_touchpoint", "refresh_analytics"],
        "status": "ready",
    },
    {
        "id": "deal-won",
        "name": "Close the revenue loop",
        "module": "attribution",
        "trigger": "deal.stage_changed:closed_won",
        "actions": ["recalculate_attribution", "update_campaign_roi", "create_invoice", "notify_revops"],
        "status": "ready",
    },
)


def workflow_action_catalog() -> list[dict[str, str]]:
    return [dict(action) for action in WORKFLOW_ACTION_CATALOG]


def workflow_catalog() -> list[dict[str, Any]]:
    """Return the product's immutable workflow template catalog."""
    return [dict(workflow, actions=list(workflow["actions"])) for workflow in WORKFLOW_CATALOG]


def persisted_workflow_catalog() -> list[dict[str, Any]]:
    """Return workflow records from the database without a dummy-data fallback."""
    from .models import WorkflowDefinition

    try:
        definitions = WorkflowDefinition.objects.exclude(status="archived").order_by("name")
        return [
            {
                "id": definition.slug,
                "name": definition.name,
                "module": definition.module,
                "description": definition.description,
                "trigger": definition.trigger,
                "actions": list(definition.actions or []),
                "status": definition.status,
            }
            for definition in definitions
        ]
    except (OperationalError, ProgrammingError):
        return []
