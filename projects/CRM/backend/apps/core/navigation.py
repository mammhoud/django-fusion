"""Canonical Loop-CRM navigation metadata.

The registry is deliberately plain data so the same module tree can feed
Django templates, HTMX fragments, JSON responses, and the Astro shell. Django
route declarations live in ``apps.core.fusion``; labels and hierarchy live
here, avoiding a second hand-maintained sidebar menu.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.utils.translation import gettext_lazy as _

MODULES: tuple[dict[str, Any], ...] = (
    {
        "id": "overview",
        "label": _("Overview"),
        "href": "/overview/",
        "icon": "overview",
        "description": _("Revenue, publishing, and attribution at a glance."),
        "children": (),
    },
    {
        "id": "crm",
        "label": _("CRM"),
        "href": "/crm/",
        "icon": "crm",
        "description": _("Companies, contacts, pipeline, and relationship history."),
        "children": (
            {"id": "companies", "label": _("Companies"), "href": "/crm/companies/"},
            {"id": "contacts", "label": _("Contacts"), "href": "/crm/contacts/"},
            {"id": "pipelines", "label": _("Pipelines"), "href": "/crm/pipelines/"},
            {"id": "deals", "label": _("Deals"), "href": "/crm/deals/"},
            {"id": "activities", "label": _("Activities"), "href": "/crm/activities/"},
        ),
    },
    {
        "id": "marketing",
        "label": _("Marketing"),
        "href": "/marketing/",
        "icon": "marketing",
        "description": _("Campaigns, content calendar, channels, and media."),
        "children": (
            {"id": "calendar", "label": _("Content calendar"), "href": "/marketing/calendar/"},
            {"id": "campaigns", "label": _("Campaigns"), "href": "/marketing/campaigns/"},
            {"id": "channels", "label": _("Channels"), "href": "/marketing/channels/"},
            {"id": "media", "label": _("Media library"), "href": "/marketing/media/"},
            {"id": "approvals", "label": _("Approvals"), "href": "/marketing/approvals/"},
        ),
    },
    {
        "id": "finance",
        "label": _("Finance"),
        "href": "/finance/",
        "icon": "finance",
        "description": _("Invoices, payments, recognized revenue, and cash visibility."),
        "children": (
            {"id": "invoices", "label": _("Invoices"), "href": "/finance/invoices/"},
            {"id": "payments", "label": _("Payments"), "href": "/finance/payments/"},
            {"id": "revenue", "label": _("Recognized revenue"), "href": "/finance/revenue/"},
        ),
    },
    {
        "id": "attribution",
        "label": _("Attribution"),
        "href": "/attribution/",
        "icon": "attribution",
        "description": _("Connect social touchpoints to pipeline revenue."),
        "children": (
            {"id": "touchpoints", "label": _("Touchpoints"), "href": "/attribution/touchpoints/"},
            {"id": "reports", "label": _("Revenue reports"), "href": "/attribution/reports/"},
        ),
    },
    {
        "id": "employees",
        "label": _("People"),
        "href": "/employees/",
        "icon": "people",
        "description": _("Workspace members, activity, and performance dossiers."),
        "children": (),
    },
    {
        "id": "ai",
        "label": _("AI Hub"),
        "href": "/ai/",
        "icon": "ai",
        "description": _("Consent-gated lead scoring, sales-email drafts, and social-post drafts."),
        "children": (),
    },
    {
        "id": "reports",
        "label": _("Reports"),
        "href": "/reports/",
        "icon": "reports",
        "description": _("The catalog of revenue, pipeline, publishing, employee, and billing reports."),
        "children": (),
    },
    {
        "id": "tasks",
        "label": _("Tasks"),
        "href": "/tasks/",
        "icon": "tasks",
        "description": _("Background job history — workflows, attribution, publishing, and finance."),
        "children": (),
    },
    {
        "id": "workspace",
        "label": _("Workspace"),
        "href": "/settings/",
        "icon": "workspace",
        "description": _("Members, workflows, integrations, and audit history."),
        "children": (
            {"id": "members", "label": _("Members & roles"), "href": "/settings/members/"},
            {"id": "workflows", "label": _("Workflows"), "href": "/settings/workflows/"},
            {"id": "integrations", "label": _("Integrations"), "href": "/settings/integrations/"},
            {"id": "email", "label": _("Email inbox"), "href": "/settings/email/"},
            {"id": "custom-fields", "label": _("Custom fields"), "href": "/settings/custom-fields/"},
            {"id": "custom-objects", "label": _("Custom objects"), "href": "/settings/custom-objects/"},
            {"id": "saved-views", "label": _("Saved views"), "href": "/settings/saved-views/"},
            {"id": "import", "label": _("Import"), "href": "/settings/import/"},
            {"id": "audit", "label": _("Audit log"), "href": "/settings/audit/"},
            {"id": "ledger", "label": _("Ledger settings"), "href": "/settings/ledger/"},
            {"id": "plan", "label": _("Plan & billing"), "href": "/settings/plan/"},
        ),
    },
)


def navigation_context(path: str = "/") -> list[dict[str, Any]]:
    """Return a request-safe navigation tree with active module and child flags."""
    current = path or "/"
    tree = deepcopy(MODULES)
    for module in tree:
        module["label"] = str(module["label"])
        module["description"] = str(module["description"])
        children = list(module.get("children", ()))
        for child in children:
            child["label"] = str(child["label"])
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
            crumbs = [{"label": str(_("Home")), "href": "/"}]
            if current != module["href"]:
                crumbs.append({"label": str(module["label"]), "href": module["href"]})
            crumbs.append({"label": str(title), "href": current})
            return crumbs
    return [{"label": str(_("Home")), "href": "/"}, {"label": str(title), "href": current}]


def module_by_id(module_id: str) -> dict[str, Any]:
    """Return one module metadata record, or the overview module."""
    for module in MODULES:
        if module["id"] == module_id:
            return module
    return MODULES[0]
