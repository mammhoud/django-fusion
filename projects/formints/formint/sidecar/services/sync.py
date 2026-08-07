"""POS Full — product catalog and data synchronization between master and child nodes."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from asgiref.sync import sync_to_async

logger = logging.getLogger("pos.product_sync")


@dataclass
class SyncResult:
    status: str = "success"
    synced: int = 0
    errors: int = 0
    approvals_created: int = 0
    message: str = ""
    details: list[dict] = field(default_factory=list)


class ProductSyncEngine:
    """Coordinates product catalog and data sync between master and child nodes."""

    def __init__(self, sync_log_model=None, node_model=None, device_config_model=None,
                 node_event_model=None, sync_approval_model=None, cloud_link_model=None):
        self.SyncLog = sync_log_model
        self.Node = node_model
        self.DeviceConfig = device_config_model
        self.NodeEvent = node_event_model
        self.SyncApproval = sync_approval_model
        self.CloudLink = cloud_link_model

    @sync_to_async
    def push_products_to_node(self, master_node_id, target_node_id, product_data,
                              product_model=None, create_approval=True):
        result = SyncResult()
        result.message = f"Pushing {len(product_data)} products to {target_node_id}"
        if create_approval and self.SyncApproval:
            approval = self.SyncApproval.objects.create(
                node_id=target_node_id, entity_type="product",
                change_data={"products": product_data, "source_node_id": master_node_id, "action": "push_products"},
                change_summary=f"{len(product_data)} products from {master_node_id}", direction="push",
            )
            result.approvals_created = 1
            result.details.append({"action": "approval_created", "approval_id": approval.id, "status": "pending_review"})
            return result
        if product_model:
            for prod in product_data:
                try:
                    product_model.objects.update_or_create(id=prod.get("id"), defaults=prod)
                    result.synced += 1
                except Exception as exc:
                    logger.warning("Failed to sync product %s: %s", prod.get("id"), exc)
                    result.errors += 1
                    result.details.append({"product_id": prod.get("id"), "error": str(exc)})
        return result

    @sync_to_async
    def push_config_to_node(self, master_node_id, target_node_id, config_entries, category="system"):
        result = SyncResult()
        synced = 0
        for key, value in config_entries.items():
            try:
                self.DeviceConfig.objects.update_or_create(
                    node_id=target_node_id, config_key=key,
                    defaults={"config_value": value if isinstance(value, dict) else {"value": value}, "category": category})
                synced += 1
            except Exception as exc:
                logger.warning("Failed to push config %s to %s: %s", key, target_node_id, exc)
                result.errors += 1
        if synced and self.NodeEvent:
            self.NodeEvent.objects.create(
                node_id=master_node_id, event_type="sync_success",
                description=f"Config pushed to {target_node_id}: {synced} entries",
                metadata={"target": target_node_id, "entries": synced})
        result.synced = synced
        result.message = f"Pushed {synced} config entries to {target_node_id}"
        return result

    @sync_to_async
    def push_catalog_to_node(self, master_node_id, target_node_id, product_data, category_data=None, settings=None):
        result = self.push_products_to_node(master_node_id, target_node_id, product_data, create_approval=False)
        return SyncResult(status=result.status, synced=result.synced, errors=result.errors,
                          message=f"Catalog synced to {target_node_id}: {result.synced} items")

    @sync_to_async
    def receive_sales_from_node(self, node_id, sales_data, require_approval=True):
        result = SyncResult()
        if require_approval and self.SyncApproval:
            approval = self.SyncApproval.objects.create(
                node_id=node_id, entity_type="sale",
                change_data={"sales": sales_data, "count": len(sales_data), "action": "push_sales"},
                change_summary=f"{len(sales_data)} sales from {node_id}", direction="push")
            result.message = f"Created approval #{approval.id} for {len(sales_data)} sales"
            result.approvals_created = 1
            if self.NodeEvent:
                self.NodeEvent.objects.create(
                    node_id=node_id, event_type="sync_success",
                    description=f"Received {len(sales_data)} sales (pending approval #{approval.id})",
                    metadata={"approval_id": approval.id, "count": len(sales_data)})
        else:
            for sale in sales_data:
                result.details.append({"sale_id": sale.get("id"), "status": "received"})
            result.synced = len(sales_data)
            result.message = f"Received {len(sales_data)} sales from {node_id}"
        return result

    @sync_to_async
    def receive_reports_from_node(self, node_id, report_data, require_approval=True):
        result = SyncResult()
        if require_approval and self.SyncApproval:
            approval = self.SyncApproval.objects.create(
                node_id=node_id, entity_type="report",
                change_data={**report_data, "source_node_id": node_id, "action": "push_report"},
                change_summary=f"Report from {node_id}: {report_data.get('report_type', 'unknown')}",
                direction="push")
            result.approvals_created = 1
            result.message = f"Report approval #{approval.id} created"
        return result

    @sync_to_async
    def receive_inventory_changes(self, node_id, inventory_data, require_approval=True):
        result = SyncResult()
        if require_approval and self.SyncApproval:
            approval = self.SyncApproval.objects.create(
                node_id=node_id, entity_type="inventory",
                change_data={"transactions": inventory_data, "count": len(inventory_data), "action": "push_inventory"},
                change_summary=f"{len(inventory_data)} inventory changes from {node_id}", direction="push")
            result.approvals_created = 1
            result.message = f"Inventory approval #{approval.id} created"
        for tx in inventory_data:
            result.details.append({"tx_id": tx.get("id"), "status": "pending_approval"})
        return result

    @sync_to_async
    def approve_changes(self, approval_ids, reviewer="", notes=""):
        result = SyncResult()
        for aid in approval_ids:
            try:
                approval = self.SyncApproval.objects.get(id=aid, status="pending")
                approval.approve(reviewer=reviewer, notes=notes)
                result.synced += 1
                result.details.append({"approval_id": aid, "status": "approved"})
            except self.SyncApproval.DoesNotExist:
                result.errors += 1
                result.details.append({"approval_id": aid, "error": "not found or not pending"})
        result.message = f"Approved {result.synced} changes, {result.errors} errors"
        return result

    @sync_to_async
    def reject_changes(self, approval_ids, reviewer="", notes=""):
        result = SyncResult()
        for aid in approval_ids:
            try:
                approval = self.SyncApproval.objects.get(id=aid, status="pending")
                approval.reject(reviewer=reviewer, notes=notes)
                result.synced += 1
                result.details.append({"approval_id": aid, "status": "rejected"})
            except self.SyncApproval.DoesNotExist:
                result.errors += 1
                result.details.append({"approval_id": aid, "error": "not found or not pending"})
        result.message = f"Rejected {result.synced} changes, {result.errors} errors"
        return result

    @sync_to_async
    def get_pending_approvals(self, entity_type=None, node_id=None, limit=50):
        qs = self.SyncApproval.objects.filter(status="pending")
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        if node_id:
            qs = qs.filter(node_id=node_id)
        qs = qs.order_by("-created_at")[:limit]
        return [{"id": a.id, "node_id": a.node_id, "entity_type": a.entity_type,
                 "entity_id": a.entity_id, "change_summary": a.change_summary,
                 "change_data": a.change_data, "direction": a.direction,
                 "created_at": a.created_at.isoformat() if a.created_at else None} for a in qs]

    @sync_to_async
    def get_approval_stats(self):
        return {
            "pending": self.SyncApproval.objects.filter(status="pending").count(),
            "approved": self.SyncApproval.objects.filter(status="approved").count(),
            "rejected": self.SyncApproval.objects.filter(status="rejected").count(),
            "applied": self.SyncApproval.objects.filter(status="applied").count(),
            "total": self.SyncApproval.objects.count(),
            "by_type": {t[0]: self.SyncApproval.objects.filter(entity_type=t[0]).count()
                        for t in self.SyncApproval.ENTITY_TYPES},
        }
