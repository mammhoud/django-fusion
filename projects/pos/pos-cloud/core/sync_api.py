"""POS Cloud — Branch sync receiver API views and django-fusion sync viewsets."""

from datetime import datetime, timezone
import json
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_fusion.comp.routes import ModelViewset
from django_fusion.comp.generic import SearchableViewMixin
from django_filters import rest_framework as filters

from .models import (
    Organization, Branch, Lead, Contact, Deal,
    InventoryReport, BranchReport,
    BranchSyncLog, BranchProduct, BranchSale, BranchInventory,
)

logger = logging.getLogger("pos.sync_api")


# ══════════════════════════════════════════════════════════════════════
# Sync Receiver API — receives data pushed from pos-full nodes
# ══════════════════════════════════════════════════════════════════════


@csrf_exempt
@require_POST
def sync_receive_products(request):
    """POST /api/sync/receive/products — Receive product catalog from a branch."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    node_id = data.get("node_id", "unknown")
    products = data.get("products", [])

    branch = Branch.objects.filter(node_id=node_id, is_active=True).first()
    if not branch:
        return JsonResponse({"error": f"No active branch found for node_id={node_id}"}, status=404)

    synced = 0
    for prod in products:
        BranchProduct.objects.update_or_create(
            branch=branch,
            source_id=str(prod.get("id") or ""),
            defaults={
                "name": prod.get("name") or "",
                "price": prod.get("price") or 0,
                "sku": prod.get("sku") or "",
                "category_name": prod.get("category_name") or "",
                "stock_quantity": prod.get("stock_quantity") or 0,
                "description": prod.get("description") or "",
                "is_active": prod.get("is_active", True),
            },
        )
        synced += 1

    BranchSyncLog.objects.create(
        branch=branch, node_id=node_id, entity_type="products",
        entity_count=synced, status="processed",
        payload={"source_node_id": node_id, "count": synced},
    )

    # Broadcast real-time event to bolt dashboard WebSocket clients
    _broadcast_sync_event("products", {
        "entity_type": "products",
        "synced": synced,
        "branch": branch.name,
        "node_id": node_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return JsonResponse({"status": "received", "synced": synced, "branch": branch.name})


@csrf_exempt
@require_POST
def sync_receive_sales(request):
    """POST /api/sync/receive/sales — Receive sales data from a branch."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    node_id = data.get("node_id", "unknown")
    sales = data.get("sales", [])

    branch = Branch.objects.filter(node_id=node_id, is_active=True).first()
    if not branch:
        return JsonResponse({"error": f"No active branch found for node_id={node_id}"}, status=404)

    synced = 0
    for sale in sales:
        BranchSale.objects.update_or_create(
            branch=branch,
            source_id=str(sale.get("id") or ""),
            defaults={
                "customer_name": sale.get("customer_name") or "",
                "total_amount": sale.get("total_amount") or 0,
                "payment_method": sale.get("payment_method") or "cash",
                "sale_date": sale.get("sale_date") or datetime.now(timezone.utc),
                "item_count": sale.get("item_count") or 0,
                "items": sale.get("items") or [],
            },
        )
        synced += 1

    BranchSyncLog.objects.create(
        branch=branch, node_id=node_id, entity_type="sales",
        entity_count=synced, status="processed",
        payload={"source_node_id": node_id, "count": synced},
    )

    _broadcast_sync_event("sales", {
        "entity_type": "sales",
        "synced": synced,
        "branch": branch.name,
        "node_id": node_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return JsonResponse({"status": "received", "synced": synced, "branch": branch.name})


@csrf_exempt
@require_POST
def sync_receive_inventory(request):
    """POST /api/sync/receive/inventory — Receive inventory transactions from a branch."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    node_id = data.get("node_id", "unknown")
    transactions = data.get("transactions", [])

    branch = Branch.objects.filter(node_id=node_id, is_active=True).first()
    if not branch:
        return JsonResponse({"error": f"No active branch found for node_id={node_id}"}, status=404)

    synced = 0
    for tx in transactions:
        BranchInventory.objects.update_or_create(
            branch=branch,
            source_id=str(tx.get("id") or ""),
            defaults={
                "product_name": tx.get("product_name") or "",
                "transaction_type": tx.get("transaction_type") or "addition",
                "quantity": tx.get("quantity") or 0,
                "notes": tx.get("notes") or "",
                "transaction_date": tx.get("transaction_date") or datetime.now(timezone.utc),
            },
        )
        synced += 1

    BranchSyncLog.objects.create(
        branch=branch, node_id=node_id, entity_type="inventory",
        entity_count=synced, status="processed",
        payload={"source_node_id": node_id, "count": synced},
    )

    _broadcast_sync_event("inventory", {
        "entity_type": "inventory",
        "synced": synced,
        "branch": branch.name,
        "node_id": node_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return JsonResponse({"status": "received", "synced": synced, "branch": branch.name})


@csrf_exempt
@require_POST
def sync_receive_heartbeat(request):
    """POST /api/sync/receive/heartbeat — Receive heartbeat/status from a branch node."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    node_id = data.get("node_id", "unknown")

    branch = Branch.objects.filter(node_id=node_id, is_active=True).first()
    if not branch:
        return JsonResponse({"error": f"No active branch found for node_id={node_id}"}, status=404)

    BranchSyncLog.objects.create(
        branch=branch, node_id=node_id, entity_type="heartbeat",
        entity_count=1, status="received",
        payload=data,
    )

    _broadcast_sync_event("heartbeat", {
        "entity_type": "heartbeat",
        "branch": branch.name,
        "node_id": node_id,
        "status": data.get("status", "online"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return JsonResponse({"status": "received", "branch": branch.name})


# ══════════════════════════════════════════════════════════════════════
# WebSocket broadcast helper
# ══════════════════════════════════════════════════════════════════════


def _broadcast_sync_event(entity_type: str, data: dict) -> None:
    """Push a sync event to all connected bolt dashboard WebSocket clients.

    Uses the Django Channels layer to send a ``sync_event`` message
    to every consumer in the ``sync_events`` group.  If no channel
    layer is configured (e.g., running under plain WSGI), the call
    is silently ignored.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return  # No channel layer configured (e.g., WSGI mode)

    try:
        async_to_sync(channel_layer.group_send)(
            "sync_events",
            {"type": "sync_event", "data": data},
        )
    except Exception as exc:
        logger.warning("Failed to broadcast %s event: %s", entity_type, exc)


# ══════════════════════════════════════════════════════════════════════
# Sync Viewsets — django-fusion for querying synced branch data
# ══════════════════════════════════════════════════════════════════════

class BranchProductFilter(filters.FilterSet):
    branch = filters.NumberFilter(field_name="branch_id")
    is_active = filters.BooleanFilter()

    class Meta:
        model = BranchProduct
        fields = ["branch", "is_active"]


class BranchSaleFilter(filters.FilterSet):
    branch = filters.NumberFilter(field_name="branch_id")
    payment_method = filters.CharFilter()
    date_from = filters.DateFilter(field_name="sale_date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="sale_date", lookup_expr="lte")

    class Meta:
        model = BranchSale
        fields = ["branch", "payment_method"]


class BranchInventoryFilter(filters.FilterSet):
    branch = filters.NumberFilter(field_name="branch_id")
    transaction_type = filters.ChoiceFilter(choices=BranchInventory.TX_TYPES)

    class Meta:
        model = BranchInventory
        fields = ["branch", "transaction_type"]


class BranchSyncLogViewSet(SearchableViewMixin, ModelViewset):
    model = BranchSyncLog
    url_prefix = "sync/logs"
    url_namespace = "sync_logs"
    list_display = ["node_id", "branch", "entity_type", "entity_count", "status", "received_at"]
    search_fields = ["node_id", "entity_type"]


class BranchProductViewSet(SearchableViewMixin, ModelViewset):
    model = BranchProduct
    url_prefix = "sync/products"
    url_namespace = "sync_products"
    list_display = ["name", "branch", "sku", "price", "stock_quantity", "last_synced_at"]
    filterset_class = BranchProductFilter
    search_fields = ["name", "sku"]


class BranchSaleViewSet(ModelViewset):
    model = BranchSale
    url_prefix = "sync/sales"
    url_namespace = "sync_sales"
    list_display = ["source_id", "branch", "total_amount", "payment_method", "item_count", "sale_date"]
    filterset_class = BranchSaleFilter


class BranchInventoryViewSet(ModelViewset):
    model = BranchInventory
    url_prefix = "sync/inventory"
    url_namespace = "sync_inventory"
    list_display = ["source_id", "branch", "product_name", "transaction_type", "quantity", "transaction_date"]
    filterset_class = BranchInventoryFilter
