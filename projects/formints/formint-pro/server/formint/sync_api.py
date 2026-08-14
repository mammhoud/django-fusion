"""
Formint — Sync API controllers (cloud server sync).

Exposes the merged POS ``ProductSyncEngine`` (``services/sync.py``) through
the Ninja API so the desktop app can drive cloud-server sync over HTTP
instead of only the Robyn WebSocket path. Every endpoint returns the
django-fusion encoder envelope (``{status, message, data}``) via the shared
``api.py`` renderer.

Endpoints (registered in ``api.py`` under the ``sync`` controller):

    POST   /api/v1/sync/push-products/     push catalog rows to a node (approval-gated)
    POST   /api/v1/sync/push-config/       push device config entries to a node
    POST   /api/v1/sync/push-catalog/      push full catalog (products + categories)
    POST   /api/v1/sync/receive-sales/     receive sales rows from a node (approval-gated)
    POST   /api/v1/sync/receive-reports/   receive report rows from a node
    POST   /api/v1/sync/receive-inventory/ receive inventory changes from a node
    POST   /api/v1/sync/approvals/{id}/approve/   approve a pending change
    POST   /api/v1/sync/approvals/{id}/reject/    reject a pending change
    GET    /api/v1/sync/approvals/         list pending approvals
    GET    /api/v1/sync/stats/             approval ledger stats
    GET    /api/v1/sync/status/            engine + cloud-link connectivity report

The engine methods are async (``@sync_to_async``); ninja-extra executes
``async def`` handlers natively, so DB work stays off the event loop.
"""

from typing import Any, Optional

from ninja import Schema
from ninja_extra import api_controller, http_get, http_post

from services.sync import ProductSyncEngine

__all__ = ["SyncController"]


class PushProductsIn(Schema):
    master_node_id: str
    target_node_id: str
    products: list[dict[str, Any]]
    create_approval: bool = True


class PushConfigIn(Schema):
    master_node_id: str
    target_node_id: str
    entries: dict[str, Any]
    category: str = "system"


class PushCatalogIn(Schema):
    master_node_id: str
    target_node_id: str
    products: list[dict[str, Any]]
    categories: list[dict[str, Any]] = []


class ReceiveSalesIn(Schema):
    node_id: str
    sales: list[dict[str, Any]]
    require_approval: bool = True


class ReceiveReportsIn(Schema):
    node_id: str
    report: dict[str, Any]
    require_approval: bool = True


class ReceiveInventoryIn(Schema):
    node_id: str
    transactions: list[dict[str, Any]]
    require_approval: bool = True


def _engine() -> ProductSyncEngine:
    """Build a ProductSyncEngine bound to the merged formint models."""
    from formint.models import (
        CloudLink, DeviceConfig, Node, NodeEvent, SyncApproval, SyncLog,
    )

    return ProductSyncEngine(
        sync_log_model=SyncLog,
        node_model=Node,
        device_config_model=DeviceConfig,
        node_event_model=NodeEvent,
        sync_approval_model=SyncApproval,
        cloud_link_model=CloudLink,
    )


@api_controller("/sync", tags=["sync"], auto_import=False)
class SyncController:
    """Cloud server sync — push/pull/approve across POS nodes."""

    @http_post("/push-products/", response={200: dict, 400: dict})
    async def push_products(self, payload: PushProductsIn):
        engine = _engine()
        result = await engine.push_products_to_node(
            payload.master_node_id,
            payload.target_node_id,
            payload.products,
            create_approval=payload.create_approval,
        )
        return 200, result.__dict__

    @http_post("/push-config/", response={200: dict, 400: dict})
    async def push_config(self, payload: PushConfigIn):
        engine = _engine()
        result = await engine.push_config_to_node(
            payload.master_node_id,
            payload.target_node_id,
            payload.entries,
            category=payload.category,
        )
        return 200, result.__dict__

    @http_post("/push-catalog/", response={200: dict, 400: dict})
    async def push_catalog(self, payload: PushCatalogIn):
        engine = _engine()
        result = await engine.push_catalog_to_node(
            payload.master_node_id,
            payload.target_node_id,
            payload.products,
            category_data=payload.categories,
        )
        return 200, result.__dict__

    @http_post("/receive-sales/", response={200: dict, 400: dict})
    async def receive_sales(self, payload: ReceiveSalesIn):
        engine = _engine()
        result = await engine.receive_sales_from_node(
            payload.node_id,
            payload.sales,
            require_approval=payload.require_approval,
        )
        return 200, result.__dict__

    @http_post("/receive-reports/", response={200: dict, 400: dict})
    async def receive_reports(self, payload: ReceiveReportsIn):
        engine = _engine()
        result = await engine.receive_reports_from_node(
            payload.node_id,
            payload.report,
            require_approval=payload.require_approval,
        )
        return 200, result.__dict__

    @http_post("/receive-inventory/", response={200: dict, 400: dict})
    async def receive_inventory(self, payload: ReceiveInventoryIn):
        engine = _engine()
        result = await engine.receive_inventory_changes(
            payload.node_id,
            payload.transactions,
            require_approval=payload.require_approval,
        )
        return 200, result.__dict__

    @http_post("/approvals/{approval_id}/approve/", response={200: dict, 400: dict})
    async def approve(
        self, approval_id: int, notes: str = "", reviewer: str = ""
    ):
        engine = _engine()
        result = await engine.approve_changes(
            [approval_id], reviewer=reviewer, notes=notes
        )
        return 200, result.__dict__

    @http_post("/approvals/{approval_id}/reject/", response={200: dict, 400: dict})
    async def reject(
        self, approval_id: int, notes: str = "", reviewer: str = ""
    ):
        engine = _engine()
        result = await engine.reject_changes(
            [approval_id], reviewer=reviewer, notes=notes
        )
        return 200, result.__dict__

    @http_get("/approvals/", response={200: dict, 400: dict})
    async def approvals(
        self,
        entity_type: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 50,
    ):
        engine = _engine()
        items = await engine.get_pending_approvals(
            entity_type=entity_type, node_id=node_id, limit=limit
        )
        return 200, {"count": len(items), "items": items}

    @http_get("/stats/", response={200: dict, 400: dict})
    async def stats(self):
        engine = _engine()
        return 200, await engine.get_approval_stats()

    @http_get("/status/", response={200: dict, 400: dict})
    async def status(self):
        """Engine health + active cloud links (connectivity report)."""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _report() -> dict:
            from datetime import timedelta

            from django.utils import timezone

            from formint.models import CloudLink, Node, SyncApproval, SyncLog

            node_count = Node.objects.count()
            online_nodes = Node.objects.filter(status="online").count()
            links = list(
                CloudLink.objects.filter(is_active=True).order_by("is_primary", "name")
            )
            recent_ok = SyncLog.objects.filter(
                status="success",
                created_at__gte=timezone.now() - timedelta(hours=24),
            ).count()
            return {
                "engine": "ProductSyncEngine",
                "nodes": {"total": node_count, "online": online_nodes},
                "cloud_links": [
                    {
                        "name": link.name,
                        "url": link.cloud_url,
                        "status": link.status,
                        "is_primary": link.is_primary,
                        "last_sync_at": link.last_sync_at.isoformat()
                        if link.last_sync_at
                        else None,
                    }
                    for link in links
                ],
                "sync_ok_last_24h": recent_ok,
                "pending_approvals": SyncApproval.objects.filter(
                    status="pending"
                ).count(),
            }

        return 200, await _report()
