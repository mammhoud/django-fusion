"""POS Cloud — API URL routing via django-fusion viewset auto-registration."""

from django.urls import path, include
from .views import (
    OrganizationViewSet,
    BranchViewSet,
    LeadViewSet,
    ContactViewSet,
    DealViewSet,
    InventoryReportViewSet,
    BranchReportViewSet,
)
from .sync_api import (
    BranchSyncLogViewSet,
    BranchProductViewSet,
    BranchSaleViewSet,
    BranchInventoryViewSet,
    sync_receive_products,
    sync_receive_sales,
    sync_receive_inventory,
    sync_receive_heartbeat,
)


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
    path("organizations/", _inc(OrganizationViewSet())),
    path("branches/", _inc(BranchViewSet())),
    path("leads/", _inc(LeadViewSet())),
    path("contacts/", _inc(ContactViewSet())),
    path("deals/", _inc(DealViewSet())),
    path("inventory-reports/", _inc(InventoryReportViewSet())),
    path("branch-reports/", _inc(BranchReportViewSet())),
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
]
