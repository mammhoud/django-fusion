"""Report catalog — the single list of reports surfaced at ``/reports/``.

Each report names the source data and the route (or API road) that renders it.
Reports whose data is already live are marked ``available``; the employee
activity report and SaaS billing report are catalogued here and materialize as
the underlying surfaces (custom-object employees, apps.billing) ship.
"""
from __future__ import annotations

REPORTS = [
    {
        "id": "revenue-trend",
        "name": "Revenue trend",
        "module": "finance",
        "href": "/finance/revenue/",
        "description": "Monthly recognized revenue, trailing six months, split by deal vs POS.",
        "available": True,
    },
    {
        "id": "attribution-models",
        "name": "Attribution models",
        "module": "attribution",
        "href": "/attribution/reports/",
        "description": "First, last, linear, time-decay, and position-based revenue views.",
        "available": True,
    },
    {
        "id": "audit-trail",
        "name": "Audit trail",
        "module": "workspace",
        "href": "/settings/audit/",
        "description": "The append-only record of workspace mutations, with CSV export.",
        "available": True,
    },
    {
        "id": "pipeline-forecast",
        "name": "Pipeline forecast",
        "module": "crm",
        "href": "/crm/pipelines/",
        "description": "Deal value by stage and probability, for a weighted forecast.",
        "available": True,
    },
    {
        "id": "publishing-analytics",
        "name": "Publishing analytics",
        "module": "marketing",
        "href": "/marketing/calendar/",
        "description": "Impressions, clicks, and engagement across scheduled and published posts.",
        "available": True,
    },
    {
        "id": "employee-activity",
        "name": "Employee activity",
        "module": "workspace",
        "href": "/employees/",
        "description": "Live member activity, deals touched, posts approved, and invoices created per workspace member.",
        "available": True,
    },
    {
        "id": "saas-billing",
        "name": "SaaS billing & seats",
        "module": "workspace",
        "href": "/settings/plan/",
        "description": "Subscription state, plan limits, and seat usage for the workspace.",
        "available": True,
    },
]


def report_catalog() -> list[dict]:
    return [dict(report) for report in REPORTS]
