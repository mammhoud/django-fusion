"""Canonical Loop-CRM navigation metadata.

The registry is deliberately plain data so the same module tree can feed
Django templates, HTMX fragments, JSON responses, and the Astro shell. Django
route declarations live in ``apps.core.fusion``; labels and hierarchy live
here, avoiding a second hand-maintained sidebar menu.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

MODULES: tuple[dict[str, Any], ...] = (
    {
        "id": "overview",
        "label": "Overview",
        "href": "/overview/",
        "icon": "overview",
        "description": "Revenue, publishing, and attribution at a glance.",
        "children": (),
    },
    {
        "id": "crm",
        "label": "CRM",
        "href": "/crm/",
        "icon": "crm",
        "description": "Companies, contacts, pipeline, and relationship history.",
        "children": (
            {"id": "companies", "label": "Companies", "href": "/crm/companies/"},
            {"id": "contacts", "label": "Contacts", "href": "/crm/contacts/"},
            {"id": "pipelines", "label": "Pipelines", "href": "/crm/pipelines/"},
            {"id": "deals", "label": "Deals", "href": "/crm/deals/"},
            {"id": "activities", "label": "Activities", "href": "/crm/activities/"},
        ),
    },
    {
        "id": "marketing",
        "label": "Marketing",
        "href": "/marketing/",
        "icon": "marketing",
        "description": "Campaigns, content calendar, channels, and media.",
        "children": (
            {"id": "calendar", "label": "Content calendar", "href": "/marketing/calendar/"},
            {"id": "campaigns", "label": "Campaigns", "href": "/marketing/campaigns/"},
            {"id": "channels", "label": "Channels", "href": "/marketing/channels/"},
            {"id": "media", "label": "Media library", "href": "/marketing/media/"},
            {"id": "approvals", "label": "Approvals", "href": "/marketing/approvals/"},
        ),
    },
    {
        "id": "finance",
        "label": "Finance",
        "href": "/finance/",
        "icon": "finance",
        "description": "Invoices, payments, recognized revenue, and cash visibility.",
        "children": (
            {"id": "invoices", "label": "Invoices", "href": "/finance/invoices/"},
            {"id": "payments", "label": "Payments", "href": "/finance/payments/"},
            {"id": "revenue", "label": "Recognized revenue", "href": "/finance/revenue/"},
        ),
    },
    {
        "id": "attribution",
        "label": "Attribution",
        "href": "/attribution/",
        "icon": "attribution",
        "description": "Connect social touchpoints to pipeline revenue.",
        "children": (
            {"id": "touchpoints", "label": "Touchpoints", "href": "/attribution/touchpoints/"},
            {"id": "reports", "label": "Revenue reports", "href": "/attribution/reports/"},
        ),
    },
    {
        "id": "reports",
        "label": "Reports",
        "href": "/reports/",
        "icon": "reports",
        "description": "The catalog of revenue, pipeline, publishing, employee, and billing reports.",
        "children": (),
    },
    {
        "id": "tasks",
        "label": "Tasks",
        "href": "/tasks/",
        "icon": "tasks",
        "description": "Background job history — workflows, attribution, publishing, and finance.",
        "children": (),
    },
    {
        "id": "workspace",
        "label": "Workspace",
        "href": "/settings/",
        "icon": "workspace",
        "description": "Members, workflows, integrations, and audit history.",
        "children": (
            {"id": "members", "label": "Members & roles", "href": "/settings/members/"},
            {"id": "workflows", "label": "Workflows", "href": "/settings/workflows/"},
            {"id": "integrations", "label": "Integrations", "href": "/settings/integrations/"},
            {"id": "email", "label": "Email inbox", "href": "/settings/email/"},
            {"id": "custom-fields", "label": "Custom fields", "href": "/settings/custom-fields/"},
            {"id": "custom-objects", "label": "Custom objects", "href": "/settings/custom-objects/"},
            {"id": "saved-views", "label": "Saved views", "href": "/settings/saved-views/"},
            {"id": "import", "label": "Import", "href": "/settings/import/"},
            {"id": "audit", "label": "Audit log", "href": "/settings/audit/"},
            {"id": "plan", "label": "Plan & billing", "href": "/settings/plan/"},
        ),
    },
)


def navigation_context(path: str = "/") -> list[dict[str, Any]]:
    """Return a request-safe navigation tree with active module and child flags."""
    current = path or "/"
    tree = deepcopy(MODULES)
    for module in tree:
        children = list(module.get("children", ()))
        for child in children:
            child["active"] = current == child["href"] or current.startswith(child["href"])
        module["children"] = children
        module["active"] = current == module["href"] or (
            module["href"] != "/" and current.startswith(module["href"])
        )
    return tree


def breadcrumbs_for(path: str, title: str) -> list[dict[str, str]]:
    """Build a stable Home → module → current-page trail for any CRM route."""
    current = path or "/"
    if current == "/":
        return []
    for module in MODULES[1:]:
        if current == module["href"] or current.startswith(module["href"]):
            crumbs = [{"label": "Home", "href": "/"}]
            if current != module["href"]:
                crumbs.append({"label": module["label"], "href": module["href"]})
            crumbs.append({"label": title, "href": current})
            return crumbs
    return [{"label": "Home", "href": "/"}, {"label": title, "href": current}]


def module_by_id(module_id: str) -> dict[str, Any]:
    """Return one module metadata record, or the overview module."""
    for module in MODULES:
        if module["id"] == module_id:
            return module
    return MODULES[0]
