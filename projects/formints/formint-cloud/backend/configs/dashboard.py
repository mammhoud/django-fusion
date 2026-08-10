"""POS Cloud — Unfold Admin Dashboard.

Provides the KPI context for the admin index via the modern
``UNFOLD["DASHBOARD_CALLBACK"]`` API (unfold >= 0.40): a callable that
receives ``(request, context)`` and returns the augmented context, which
``admin/index.html`` (overridden in ``templates/admin/``) renders as the
Tactical Telemetry dashboard.
"""

from __future__ import annotations

from django.utils import timezone


def dashboard_callback(request, context):
    """Augment the admin index context with POS Cloud KPIs + sync stats."""

    from django.db.models import Sum
    from apps.core.models import Organization, Branch, Lead, InventoryReport, BranchSyncLog

    # ── Live sync activity counters (total items synced; JS increments by batch delta) ──
    sync_logs = BranchSyncLog.objects
    products_synced = sync_logs.filter(
        entity_type="products", status="processed"
    ).aggregate(total=Sum("entity_count"))["total"] or 0
    sales_synced = sync_logs.filter(
        entity_type="sales", status="processed"
    ).aggregate(total=Sum("entity_count"))["total"] or 0
    inventory_synced = sync_logs.filter(
        entity_type="inventory", status="processed"
    ).aggregate(total=Sum("entity_count"))["total"] or 0
    last_sync = sync_logs.order_by("-received_at").first()
    last_sync_time = None
    if last_sync:
        last_sync_time = timezone.localtime(last_sync.received_at).strftime("%H:%M:%S")

    context.update({
        "org_count": Organization.objects.filter(is_active=True).count(),
        "branch_count": Branch.objects.filter(is_active=True).count(),
        "lead_count": Lead.objects.filter(is_active=True).count(),
        "report_count": InventoryReport.objects.count(),
        "cards": [
            {
                "title": "Active Organizations",
                "value": Organization.objects.filter(is_active=True).count(),
            },
            {
                "title": "Active Branches",
                "value": Branch.objects.filter(is_active=True).count(),
            },
            {
                "title": "Open Leads",
                "value": Lead.objects.filter(is_active=True, status="new").count(),
            },
            {
                "title": "Reports Generated",
                "value": InventoryReport.objects.count(),
            },
        ],
        "sync_stats": {
            "products_synced": products_synced,
            "sales_synced": sales_synced,
            "inventory_synced": inventory_synced,
            "last_sync_at": last_sync.received_at.isoformat() if last_sync else None,
            "last_sync_branch": last_sync.branch.name if last_sync and last_sync.branch else "—",
            "last_sync_time": last_sync_time,
        },
        "recent_leads": Lead.objects.filter(is_active=True)[:5],
        "recent_reports": InventoryReport.objects.select_related("organization")[:5],
    })
    return context
