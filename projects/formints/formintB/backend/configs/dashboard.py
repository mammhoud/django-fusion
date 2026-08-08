"""POS Cloud — Unfold Admin Dashboard."""

from django.utils.translation import gettext_lazy as _
from unfold.views import UnfoldModelAdminViewMixin
from django.views.generic import TemplateView


class POSCloudDashboard(UnfoldModelAdminViewMixin, TemplateView):
    """Custom Unfold dashboard with POS Cloud KPIs and quick actions."""

    title = _("POS Cloud Dashboard")
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        context.update({
            "org_count": Organization.objects.filter(is_active=True).count(),
            "branch_count": Branch.objects.filter(is_active=True).count(),
            "lead_count": Lead.objects.filter(is_active=True).count(),
            "report_count": InventoryReport.objects.count(),
            "cards": [
                {
                    "title": "Active Organizations",
                    "value": Organization.objects.filter(is_active=True).count(),
                    "icon": "corporate_fare",
                    "color": "primary",
                },
                {
                    "title": "Active Branches",
                    "value": Branch.objects.filter(is_active=True).count(),
                    "icon": "store",
                    "color": "success",
                },
                {
                    "title": "Open Leads",
                    "value": Lead.objects.filter(is_active=True, status="new").count(),
                    "icon": "person_add",
                    "color": "warning",
                },
                {
                    "title": "Reports Generated",
                    "value": InventoryReport.objects.count(),
                    "icon": "analytics",
                    "color": "info",
                },
            ],
            "sync_stats": {
                "products_synced": products_synced,
                "sales_synced": sales_synced,
                "inventory_synced": inventory_synced,
                "last_sync_at": last_sync.received_at.isoformat() if last_sync else None,
                "last_sync_branch": last_sync.branch.name if last_sync and last_sync.branch else "—",
            },
        })
        return context
