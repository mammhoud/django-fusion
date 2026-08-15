"""POS Full — multi-terminal sync changeset collector.

Multi-terminal Sync (P1): every terminal writes to the same master, and the
``sync_signals`` handlers flag each changed row ``is_synced=False``. This
module turns that flag into a pullable change feed so a peer terminal can
ask "what changed since I last synced?", apply it, and acknowledge.

* ``SYNC_TRACKED_MODELS`` — every model carrying the ``is_synced`` flag.
* ``SyncChangeCollector.collect`` — return pending rows grouped per entity,
  optionally filtered by ``entity_type``.
* ``SyncChangeCollector.acknowledge`` — mark rows synced once a peer confirms.

The WebSocket layer (``consumers.broadcast_entities``) notifies connected
terminals in real time; the collector is the pull half of that contract.
"""

from __future__ import annotations

import logging
from datetime import datetime, date
from decimal import Decimal

from django.utils import timezone

from models.config import CloudLink, DeviceConfig, MasterDevice
from models.extra import (
    Ingredient,
    InventoryAdjustment,
    ReceiptTemplate,
    Recipe,
    Role,
)
from models.loyalty import ClientCategory, LoyaltyTransaction
from models.menu import Menu, MenuItem, MenuItemAssignment, MenuVersion
from models.node import Heartbeat, NodeEvent
from models.pos import (
    Category,
    Customer,
    Employee,
    InventoryTransaction,
    Product,
    Sale,
    SaleItem,
)
from models.sync import SyncLog

logger = logging.getLogger("pos.sync_changes")

# (entity_type, model) — the canonical order a peer applies changes in
# (parents before children so FKs resolve during apply).
SYNC_TRACKED_MODELS: list[tuple[str, type]] = [
    ("category", Category),
    ("product", Product),
    ("customer", Customer),
    ("sale", Sale),
    ("sale_item", SaleItem),
    ("inventory_transaction", InventoryTransaction),
    ("employee", Employee),
    ("client_category", ClientCategory),
    ("loyalty_transaction", LoyaltyTransaction),
    ("menu", Menu),
    ("menu_item", MenuItem),
    ("menu_item_assignment", MenuItemAssignment),
    ("menu_version", MenuVersion),
    ("ingredient", Ingredient),
    ("recipe", Recipe),
    ("receipt_template", ReceiptTemplate),
    ("role", Role),
    ("inventory_adjustment", InventoryAdjustment),
    ("device_config", DeviceConfig),
    ("master_device", MasterDevice),
    ("cloud_link", CloudLink),
    ("heartbeat", Heartbeat),
    ("node_event", NodeEvent),
    ("sync_log", SyncLog),
]

_MODELS_BY_TYPE = {et: model for et, model in SYNC_TRACKED_MODELS}


def serialize_row(instance) -> dict:
    """Serialize a model instance to a plain JSON-safe dict (all local fields)."""
    data: dict = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.attname, None)
        if isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, (datetime, date)):
            value = value.isoformat()
        data[field.attname] = value
    return data


class SyncChangeCollector:
    """Collect pending (``is_synced=False``) rows across sync-tracked models."""

    def collect(self, entity_type: str | None = None, limit: int = 1000) -> dict:
        """Return all pending changes, optionally filtered to one entity type."""
        changes: list[dict] = []
        for et, model in SYNC_TRACKED_MODELS:
            if entity_type and et != entity_type:
                continue
            qs = model.objects.filter(is_synced=False).order_by("id")
            for obj in qs[:limit]:
                changes.append(
                    {"entity_type": et, "id": obj.pk, "data": serialize_row(obj)}
                )
        return {
            "changes": changes,
            "count": len(changes),
            "generated_at": timezone.now().isoformat(),
        }

    def acknowledge(self, entity_type: str, ids: list[int]) -> dict:
        """Mark the given rows as synced (a peer confirmed receipt)."""
        model = _MODELS_BY_TYPE.get(entity_type)
        if model is None:
            return {"acknowledged": 0, "error": f"unknown entity_type: {entity_type}"}
        if not ids:
            return {"acknowledged": 0}
        updated = model.objects.filter(id__in=ids).update(
            is_synced=True,
            synced_at=timezone.now(),
            sync_status="synced",
        )
        return {"entity_type": entity_type, "acknowledged": updated}


def entity_types() -> list[str]:
    """Return the list of sync-tracked entity types (for clients/discovery)."""
    return [et for et, _ in SYNC_TRACKED_MODELS]
