"""POS Cloud — API URL routing via django-fusion viewset auto-registration."""

from django.urls import path, include
from apps.core.views import (
    OrganizationViewSet,
    BranchViewSet,
    LeadViewSet,
    ContactViewSet,
    DealViewSet,
    InventoryReportViewSet,
    BranchReportViewSet,
    DeviceTokenViewSet,
    SyncConflictViewSet,
    SyncQueueItemViewSet,
)
from apps.handlers.sync_api import (
    BranchSyncLogViewSet,
    BranchProductViewSet,
    BranchSaleViewSet,
    BranchInventoryViewSet,
    sync_receive_products,
    sync_receive_sales,
    sync_receive_inventory,
    sync_receive_heartbeat,
)
from apps.handlers import sync_dashboard
from apps.handlers.surface import bridge_products, bridge_sales, bridge_settings


def _inc(viewset):
    """Include a viewset's urls, destructuring the 3-tuple for Django 5.x compat."""
    patterns, app_name, namespace = viewset.urls
    return include((patterns, app_name), namespace=namespace)


# Simple health endpoint for SyncClient.health()
from django.http import JsonResponse
def _health(request):
    return JsonResponse({"status": "healthy", "service": "pos-cloud", "version": "1.0"})

urlpatterns = [
    path("health", _health, name="health"),
    # Community-UI data bridges (sidecar /api/sales|products|settings contract)
    path("sales", bridge_sales, name="bridge_sales"),
    path("products", bridge_products, name="bridge_products"),
    path("settings", bridge_settings, name="bridge_settings"),
    path("organizations/", _inc(OrganizationViewSet())),
    path("branches/", _inc(BranchViewSet())),
    path("leads/", _inc(LeadViewSet())),
    path("contacts/", _inc(ContactViewSet())),
    path("deals/", _inc(DealViewSet())),
    path("inventory-reports/", _inc(InventoryReportViewSet())),
    path("branch-reports/", _inc(BranchReportViewSet())),
    path("device-tokens/", _inc(DeviceTokenViewSet())),
    path("conflicts/", _inc(SyncConflictViewSet())),
    path("queue/", _inc(SyncQueueItemViewSet())),
    # Branch sync endpoints (query synced POS data)
    path("sync/logs/", _inc(BranchSyncLogViewSet())),
    path("sync/products/", _inc(BranchProductViewSet())),
    path("sync/sales/", _inc(BranchSaleViewSet())),
    path("sync/inventory/", _inc(BranchInventoryViewSet())),
    # Sync receiver endpoints (data push from branches)
    # Received via SyncClient._push -> /api/sync/push/{entity_type}
    path("sync/push/products", sync_receive_products, name="sync_receive_products"),
    path("sync/push/sales", sync_receive_sales, name="sync_receive_sales"),
    path("sync/push/inventory", sync_receive_inventory, name="sync_receive_inventory"),
    path("sync/push/heartbeat", sync_receive_heartbeat, name="sync_receive_heartbeat"),

    # ═════════════════════════════════════════════════════════
    # Sync Dashboard (health, queue, conflicts)
    # ═════════════════════════════════════════════════════════

    # Health
    path("dashboard/branches/health", sync_dashboard.all_branches_health, name="dashboard_all_branches_health"),
    path("dashboard/branches/<str:branch_code>/health", sync_dashboard.branch_health, name="dashboard_branch_health"),

    # Queue
    path("dashboard/queue/summary", sync_dashboard.queue_summary, name="dashboard_queue_summary"),
    path("dashboard/queue/by-branch", sync_dashboard.queue_by_branch, name="dashboard_queue_by_branch"),
    path("dashboard/queue/list/<str:status>", sync_dashboard.queue_list, name="dashboard_queue_list"),
    path("dashboard/queue/retry/<int:item_id>", sync_dashboard.queue_retry, name="dashboard_queue_retry"),
    path("dashboard/queue/cancel/<int:item_id>", sync_dashboard.queue_cancel, name="dashboard_queue_cancel"),

    # Conflicts
    path("dashboard/conflicts", sync_dashboard.conflict_list, name="dashboard_conflict_list"),
    path("dashboard/conflicts/stats", sync_dashboard.conflict_stats, name="dashboard_conflict_stats"),
    path("dashboard/conflicts/<int:conflict_id>/resolve", sync_dashboard.conflict_resolve, name="dashboard_conflict_resolve"),
    path("dashboard/conflicts/<int:conflict_id>/dismiss", sync_dashboard.conflict_dismiss, name="dashboard_conflict_dismiss"),

    # Activity
    path("dashboard/activity", sync_dashboard.recent_activity, name="dashboard_recent_activity"),
]
