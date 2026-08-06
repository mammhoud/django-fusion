"""
POS Full — Django views replacing ALL Robyn route handlers.

Post-migration from Robyn → Django (django-bolt + Ninja + Channels), this
module consolidates every HTTP endpoint that was previously scattered across
the Robyn ``routes/`` package. All views are sync Django views (Django ORM
calls are sync, no ``sync_to_async`` needed).

Route groups:
  * /, /health, /stats           — server info + health (was routes/info.py)
  * /kds/*                       — KDS display data (was routes/kds.py)
  * /nodes/*                     — node registry CRUD (was routes/nodes.py)
  * /sync/*, /sales/*            — sync + sales ops (was routes/sync.py)
  * /transactions, /analytics    — data aggregation (was routes/data.py)
  * /admin/*                     — Jinja2 admin dashboard (was routes/admin.py)
  * /crm/*                       — CRM endpoints (was routes/crm.py)
  * /reports/*                   — reports (was routes/reports.py)
  * /approvals/*                 — sync approvals (was routes/approvals.py)
  * /webhooks/*                  — webhook receiver (was routes/webhooks.py)
  * /config/*                    — device/master config (was routes/config.py)
  * /events                      — node events (was routes/nodes.py /events)
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import socket as _socket
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect
from django.utils import timezone as dj_timezone

from consumers import broadcast_config, broadcast_entities, broadcast_nodes

from models.apikey import ApiKey
from models.approval import SyncApproval
from models.audit import SignalEvent
from models.config import CloudLink, DeviceConfig, MasterDevice
from models.extra import Ingredient, InventoryAdjustment, ReceiptTemplate, Recipe, Role
from models.forge_gaps import Coupon, DeliveryType, DeliveryZone, Shift
from models.hr import EmployeeSchedule, Payroll, TaxReport
from models.inventory import PurchaseOrder, PurchaseOrderItem, Supplier
from models.loyalty import ClientCategory, LoyaltyTransaction, UserSettings
from models.menu import Menu, MenuItem, MenuItemAssignment
from models.node import Heartbeat, Node, NodeEvent
from models.notes import Note
from models.ops import KitchenTicket, SupportTicket
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
from models.token import DeviceToken

from services.sync import ProductSyncEngine

logger = logging.getLogger("pos.views")

# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

_start_time = datetime.now(timezone.utc)
_about_version = "1.0.0"
try:
    from about import __version__ as _v, __service_name_full__ as _svc, __service_desc_full__ as _desc
    _about_version = _v
    _about_service_name = _svc
    _about_service_desc = _desc
except ImportError:
    _about_service_name = "POS Full Server"
    _about_service_desc = "POS Full Edition — Django + django-bolt + Ninja"

DB_PATH = Path(__file__).resolve().parent.parent / "restaurant.db"

ALL_MODELS = [
    Category, Product, Customer, Sale, SaleItem, InventoryTransaction,
    Employee, MenuItem, Menu, MenuItemAssignment, Node, Heartbeat,
    NodeEvent, SyncLog, DeviceConfig, MasterDevice, CloudLink,
    SyncApproval, DeviceToken, SignalEvent,
    Supplier, PurchaseOrder, PurchaseOrderItem,
    KitchenTicket, SupportTicket, Payroll, EmployeeSchedule, TaxReport,
    Note, Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
    ClientCategory, LoyaltyTransaction, UserSettings, ApiKey,
    Coupon, DeliveryType, DeliveryZone, Shift,
]

PYDANTIC_READY = False
NodeRegisterRequest = None
HeartbeatRequest = None
try:
    from pydantic import BaseModel, Field
    PYDANTIC_READY = True

    class _NodeRegisterRequest(BaseModel):
        node_id: str | None = None
        hostname: str | None = None
        node_type: str = "pos-full"
        version: str = "unknown"
        status: str = "online"
        product_count: int = 0
        transaction_count: int = 0
        customer_count: int = 0
        ip_address: str | None = None
        port: int | None = None
        capabilities: dict = {}
        metadata: dict = {}
        model_config = {"extra": "allow"}

    class _HeartbeatRequest(BaseModel):
        node_id: str
        status: str = "online"
        version: str | None = None
        product_count: int | None = None
        transaction_count: int | None = None
        model_config = {"extra": "allow"}

    NodeRegisterRequest = _NodeRegisterRequest
    HeartbeatRequest = _HeartbeatRequest
except ImportError:
    pass


def _error(status: int, msg: str) -> JsonResponse:
    return JsonResponse({"error": msg}, status=status)


def _html(content: str, status: int = 200) -> HttpResponse:
    return HttpResponse(content, status=status, content_type="text/html; charset=utf-8")


def _json(data: Any, status: int = 200) -> JsonResponse:
    return JsonResponse(data, status=status, safe=False)


def _ser_model(obj) -> dict:
    """Serialize a Django model instance to a plain dict (all fields)."""
    data = {}
    for field in obj._meta.fields:
        val = getattr(obj, field.attname, None)
        if isinstance(val, Decimal):
            val = float(val)
        elif isinstance(val, datetime):
            val = val.isoformat() if val else None
        data[field.name] = val
    return data


def _ser_node(node: Node) -> dict:
    data = _ser_model(node)
    if node.last_seen:
        data["last_seen"] = node.last_seen.isoformat()
    return data


# ═══════════════════════════════════════════════════════════════════════════
# Info routes (was routes/info.py)
# ═══════════════════════════════════════════════════════════════════════════

def index(request: HttpRequest) -> JsonResponse:
    counts = {}
    for m in ALL_MODELS:
        try:
            counts[m.__name__] = m.objects.count()
        except Exception:
            counts[m.__name__] = -1
    return _json({
        "service": _about_service_desc,
        "version": _about_version,
        "database": str(DB_PATH),
        "django_orm": True,
        "pydantic": PYDANTIC_READY,
        "num_models": len(ALL_MODELS),
        "counts": counts,
    })


def health(request: HttpRequest) -> JsonResponse:
    return _json({
        "status": "healthy",
        "service": _about_service_name,
        "version": _about_version,
        "uptime": (datetime.now(timezone.utc) - _start_time).total_seconds(),
        "django_orm": True,
        "database": str(DB_PATH),
    })


def stats_endpoint(request: HttpRequest) -> JsonResponse:
    stats = {}
    for m in ALL_MODELS:
        try:
            stats[m.__name__] = m.objects.count()
        except Exception:
            stats[m.__name__] = -1
    stats["nodes_online"] = Node.objects.filter(status="online").count()
    stats["nodes_offline"] = Node.objects.filter(status="offline").count()
    stats["uptime_seconds"] = (datetime.now(timezone.utc) - _start_time).total_seconds()
    return _json(stats)


# ═══════════════════════════════════════════════════════════════════════════
# KDS routes (was routes/kds.py)
# ═══════════════════════════════════════════════════════════════════════════

def _ser_ticket(ticket: KitchenTicket) -> dict:
    data = _ser_model(ticket)
    if "sale_id" not in data:
        data["sale_id"] = ticket.sale_id
    return data


def kds_list_tickets(request: HttpRequest) -> JsonResponse:
    status_filter = request.GET.get("status", "").strip() or None
    qs = KitchenTicket.objects.select_related("sale").all()
    if status_filter and status_filter != "all":
        qs = qs.filter(status=status_filter)
    qs = qs.order_by("-priority", "created_at")[:200]
    tickets = []
    for ticket in qs:
        data = _ser_ticket(ticket)
        sale = ticket.sale
        data["sale_id"] = sale.id
        data["order_type"] = getattr(sale, "order_type", "dine-in")
        data["table_number"] = getattr(sale, "table_number", None)
        data["delivery_address"] = getattr(sale, "delivery_address", None)
        data["total_amount"] = float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
        tickets.append(data)
    return _json(tickets)


def kds_get_ticket(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        ticket = KitchenTicket.objects.select_related("sale").get(id=pk)
    except KitchenTicket.DoesNotExist:
        return _error(404, "Ticket not found")
    data = _ser_ticket(ticket)
    sale = ticket.sale
    data["sale_id"] = sale.id
    data["order_type"] = getattr(sale, "order_type", "dine-in")
    data["table_number"] = getattr(sale, "table_number", None)
    data["delivery_address"] = getattr(sale, "delivery_address", None)
    data["total_amount"] = float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
    return _json(data)


def kds_update_ticket(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        ticket = KitchenTicket.objects.select_related("sale").get(id=pk)
    except KitchenTicket.DoesNotExist:
        return _error(404, "Ticket not found")
    body = json.loads(request.body) if request.body else {}
    if "status" in body:
        ticket.status = body["status"]
        if body["status"] == "delivered" and not ticket.completed_at:
            ticket.completed_at = datetime.now(timezone.utc)
    if "notes" in body:
        ticket.notes = body["notes"]
    if "priority" in body:
        ticket.priority = body["priority"]
    if "prepare_time_minutes" in body:
        ticket.prepare_time_minutes = body["prepare_time_minutes"]
    ticket.save()
    data = _ser_ticket(ticket)
    sale = ticket.sale
    data["sale_id"] = sale.id
    data["order_type"] = getattr(sale, "order_type", "dine-in")
    data["table_number"] = getattr(sale, "table_number", None)
    data["total_amount"] = float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
    return _json(data)


def kds_get_sale_items(request: HttpRequest, sale_id: int) -> HttpResponse:
    try:
        sale = Sale.objects.get(id=sale_id)
        items = SaleItem.objects.filter(sale=sale).select_related("product")
    except Sale.DoesNotExist:
        return _html('<p class="text-xs text-red-500">Sale not found</p>', status=404)

    if not items.exists():
        return _html('<p class="text-xs opacity-50 italic py-3">No items recorded for this order.</p>')

    rows = []
    for item in items:
        product_name = getattr(item, "product_name", "") or (
            item.product.name if hasattr(item, "product") and item.product else "—"
        )
        price = float(getattr(item, "price", 0) or 0)
        qty = getattr(item, "quantity", 1) or 1
        subtotal = price * qty
        safe_name = product_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows.append(
            f'<div class="flex items-center justify-between py-1.5 px-2 rounded-lg text-xs">'
            f'<div class="flex items-center gap-2 min-w-0">'
            f'<span class="w-5 h-5 rounded flex items-center justify-center text-[11px] font-bold shrink-0" '
            f'style="background:var(--color-surface-raised);color:var(--color-text-secondary)">{qty}</span>'
            f'<span class="font-medium truncate" style="color:var(--color-text-primary)">{safe_name}</span>'
            f'</div>'
            f'<span class="shrink-0 ml-2" style="color:var(--color-text-secondary)">${subtotal:.2f}</span>'
            f'</div>'
        )
    total = sum(
        float(getattr(i, "price", 0) or 0) * (getattr(i, "quantity", 1) or 1)
        for i in items
    )
    rows.append(
        f'<div class="flex items-center justify-between py-2 px-2 mt-1 border-t font-bold text-xs" '
        f'style="border-color:var(--color-border-subtle);color:var(--color-text-primary)">'
        f'<span>Total</span><span>${total:.2f}</span></div>'
    )
    return _html("".join(rows))


def kds_stats(request: HttpRequest) -> JsonResponse:
    total = KitchenTicket.objects.count()
    by_status = dict(
        KitchenTicket.objects.values("status").annotate(n=Count("id")).values_list("status", "n")
    )
    now = datetime.now(timezone.utc)
    recent = KitchenTicket.objects.filter(created_at__gte=now - timedelta(hours=24)).count()
    return _json({
        "total": total,
        "by_status": by_status,
        "last_24h": recent,
        "pending": by_status.get("pending", 0),
        "preparing": by_status.get("preparing", 0),
        "ready": by_status.get("ready", 0),
        "delivered": by_status.get("delivered", 0),
    })


# ═══════════════════════════════════════════════════════════════════════════
# Node routes (was routes/nodes.py — CRUD only, WS moved to consumers.py)
# ═══════════════════════════════════════════════════════════════════════════

def node_list(request: HttpRequest) -> JsonResponse:
    nodes = Node.objects.all()
    return _json([_ser_node(n) for n in nodes])


def node_detail(request: HttpRequest, node_id: str) -> JsonResponse:
    try:
        return _json(_ser_node(Node.objects.get(node_id=node_id)))
    except Node.DoesNotExist:
        return _error(404, "Node not found")


def node_register(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    if PYDANTIC_READY and NodeRegisterRequest:
        try:
            validated = NodeRegisterRequest(**body)
            body = validated.model_dump(exclude_none=True)
        except Exception as exc:
            return _error(400, str(exc))

    nid = body.get("node_id") or f"NODE-{uuid.uuid4().hex[:8].upper()}"
    hst = body.get("hostname") or _socket.gethostname()
    node, created = Node.objects.update_or_create(
        node_id=nid,
        defaults={
            "hostname": hst, "version": body.get("version", "unknown"),
            "api_version": body.get("api_version", "1.0"),
            "status": body.get("status", "online"),
            "node_type": body.get("node_type", "pos-full"),
            "product_count": body.get("product_count", 0),
            "transaction_count": body.get("transaction_count", 0),
            "customer_count": body.get("customer_count", 0),
            "ip_address": body.get("ip_address"),
            "port": body.get("port"),
            "capabilities": body.get("capabilities", {}),
            "metadata": body.get("metadata", {}),
        },
    )
    Heartbeat.objects.create(
        node_id=nid, status=node.status,
        payload={"version": node.version, "product_count": node.product_count},
    )
    if created:
        NodeEvent.objects.create(
            node_id=nid, event_type="registered",
            description=f"Node {nid} registered ({node.node_type})",
            metadata={"hostname": hst, "version": node.version},
        )
    node_data = _ser_node(node)
    broadcast_nodes({"type": "registered", "node_id": nid, "data": node_data})
    return _json({"status": "registered", "node": node_data}, status=201)


def node_heartbeat(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    node_id = body.pop("node_id", None)
    if not node_id:
        return _error(400, "node_id is required")
    if PYDANTIC_READY and HeartbeatRequest:
        try:
            validated = HeartbeatRequest(node_id=node_id, **body)
            body = validated.model_dump(exclude_none=True)
            node_id = body.pop("node_id", node_id)
        except Exception as exc:
            return _error(400, str(exc))
    try:
        node = Node.objects.get(node_id=node_id)
    except Node.DoesNotExist:
        return _error(404, f"node '{node_id}' not found. Register first.")
    was_offline = node.status == "offline"
    node.status = body.get("status", "online")
    if "version" in body:
        node.version = body["version"]
    if "product_count" in body:
        node.product_count = body["product_count"]
    if "transaction_count" in body:
        node.transaction_count = body["transaction_count"]
    node.save()
    Heartbeat.objects.create(node_id=node_id, status=node.status, payload=body)
    if was_offline:
        NodeEvent.objects.create(
            node_id=node_id, event_type="heartbeat_restored",
            description=f"Node {node_id} restored to online",
        )
    node_data = _ser_node(node)
    broadcast_nodes({"type": "heartbeat", "node_id": node_id, "data": node_data})
    return _json({"status": "ok", "node": node_data})


def node_update(request: HttpRequest, node_id: str) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    try:
        node = Node.objects.get(node_id=node_id)
    except Node.DoesNotExist:
        return _error(404, "node not found")
    allowed = {"hostname", "version", "api_version", "status", "status_message",
               "product_count", "transaction_count", "customer_count",
               "ip_address", "port", "node_type", "is_active",
               "capabilities", "metadata"}
    changed = [k for k in body if k in allowed and hasattr(node, k)]
    for k in changed:
        setattr(node, k, body[k])
    if changed:
        node.save(update_fields=changed + ["updated_at"])
        NodeEvent.objects.create(
            node_id=node_id, event_type="config_change",
            description=f"Node updated: {', '.join(changed)}",
            metadata={"changed_fields": changed},
        )
    node_data = _ser_node(node)
    broadcast_nodes({"type": "config_change", "node_id": node_id, "data": node_data})
    return _json(node_data)


def node_delete(request: HttpRequest, node_id: str) -> JsonResponse:
    try:
        n = Node.objects.get(node_id=node_id)
        n.delete()
        NodeEvent.objects.create(
            node_id=node_id, event_type="deleted",
            description=f"Node {node_id} deleted",
        )
        broadcast_nodes({"type": "deleted", "node_id": node_id, "data": {"node_id": node_id, "status": "deleted"}})
        return _json({"status": "deleted"})
    except Node.DoesNotExist:
        return _error(404, "node not found")


def node_get_config(request: HttpRequest, node_id: str) -> JsonResponse:
    entries = DeviceConfig.objects.filter(node_id=node_id, is_active=True)
    return _json({
        "node_id": node_id,
        "configs": {e.config_key: e.config_value for e in entries},
        "count": entries.count(),
    })


def node_set_config(request: HttpRequest, node_id: str) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    config_key = body.get("config_key", "")
    if not config_key:
        return _error(400, "config_key is required")
    obj, created = DeviceConfig.objects.update_or_create(
        node_id=node_id, config_key=config_key,
        defaults={
            "config_value": body.get("config_value", {}),
            "category": body.get("category", "system"),
            "description": body.get("description", ""),
        },
    )
    action = "created" if created else "updated"
    NodeEvent.objects.create(
        node_id=node_id, event_type="config_change",
        description=f"Config {config_key} {action}",
        metadata={"config_key": config_key, "action": action},
    )
    broadcast_config({"type": f"config_{action}", "node_id": node_id, "data": {
        "config_key": config_key, "category": body.get("category", "system"),
    }})
    return _json({
        "node_id": node_id, "config_key": config_key,
        "config_value": obj.config_value, "action": action, "version": obj.version,
    })


def node_delete_config(request: HttpRequest, node_id: str, config_key: str) -> JsonResponse:
    deleted, _ = DeviceConfig.objects.filter(node_id=node_id, config_key=config_key).delete()
    if deleted:
        NodeEvent.objects.create(
            node_id=node_id, event_type="config_change",
            description=f"Config {config_key} deleted",
            metadata={"config_key": config_key, "action": "deleted"},
        )
    broadcast_config({"type": "config_deleted", "node_id": node_id, "data": {"config_key": config_key}})
    return _json({"deleted": deleted > 0})


def node_history(request: HttpRequest, node_id: str) -> JsonResponse:
    limit = min(int(request.GET.get("limit", "100")), 500)
    return _json({
        "node_id": node_id,
        "events": list(NodeEvent.objects.filter(node_id=node_id)
            .order_by("-created_at")[:limit]
            .values("id", "event_type", "description", "metadata", "created_at")),
        "heartbeats": list(Heartbeat.objects.filter(node_id=node_id)
            .order_by("-received_at")[:limit]
            .values("id", "status", "latency_ms", "received_at")),
        "configs": list(DeviceConfig.objects.filter(node_id=node_id, is_active=True)
            .values("config_key", "category", "version", "updated_at")),
        "syncs": list(SyncLog.objects.filter(node_id=node_id)
            .order_by("-created_at")[:50]
            .values("entity_type", "entity_id", "direction", "status", "created_at")),
        "total_events": NodeEvent.objects.filter(node_id=node_id).count(),
    })


def list_events(request: HttpRequest) -> JsonResponse:
    node_id_filter = request.GET.get("node_id")
    event_type_filter = request.GET.get("event_type")
    limit = min(int(request.GET.get("limit", "50")), 500)
    qs = NodeEvent.objects.all()
    if node_id_filter:
        qs = qs.filter(node_id=node_id_filter)
    if event_type_filter:
        qs = qs.filter(event_type=event_type_filter)
    qs = qs.order_by("-created_at")[:limit]
    return _json({
        "events": [{
            "id": e.id, "node_id": e.node_id,
            "event_type": e.event_type, "description": e.description,
            "metadata": e.metadata,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        } for e in qs],
        "total": 0,
    })


# ═══════════════════════════════════════════════════════════════════════════
# Sync routes (was routes/sync.py)
# ═══════════════════════════════════════════════════════════════════════════

def _load_sync_state() -> dict:
    path = Path(__file__).resolve().parent / "sync_state.json"
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return {}


def _save_sync_state(state: dict) -> None:
    path = Path(__file__).resolve().parent / "sync_state.json"
    path.write_text(json.dumps(state, indent=2))


def sale_cashback(request: HttpRequest, pk: int) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    amount = body.get("cashback_amount", 0)
    try:
        sale = Sale.objects.get(id=pk)
    except Sale.DoesNotExist:
        return _error(404, "Sale not found")
    if sale.status in ("refunded", "cancelled"):
        return _error(400, f"Cannot add cashback to {sale.status} sale")
    sale.cashback_amount = Decimal(str(amount))
    sale.total = sale.subtotal - sale.discount_amount + sale.tax_amount - sale.cashback_amount
    sale.save(update_fields=["cashback_amount", "total", "updated_at"])
    return _json(_ser_model(sale))


def sale_return(request: HttpRequest, pk: int) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    items_to_return = body.get("items", [])
    if not items_to_return:
        return _error(400, "items list is required")
    try:
        sale = Sale.objects.get(id=pk)
    except Sale.DoesNotExist:
        return _error(404, "Sale not found")
    if sale.status in ("refunded", "cancelled"):
        return _error(400, f"Cannot return a {sale.status} sale")

    if sale.cashback_amount is None:
        sale.cashback_amount = Decimal("0.00")

    results = []
    refunded_total = Decimal("0.00")
    with db_transaction.atomic():
        for item_data in items_to_return:
            si_id = item_data.get("sale_item_id")
            qty = abs(item_data.get("quantity", 0))
            disposition = item_data.get("disposition", "restock")
            notes = item_data.get("notes", "")
            if qty <= 0:
                results.append({"sale_item_id": si_id, "status": "skipped", "reason": "invalid quantity"})
                continue
            try:
                sale_item = SaleItem.objects.get(id=si_id, sale=sale)
            except SaleItem.DoesNotExist:
                results.append({"sale_item_id": si_id, "status": "error", "reason": "not found"})
                continue
            if qty > sale_item.quantity:
                results.append({
                    "sale_item_id": si_id, "status": "error",
                    "reason": f"only {sale_item.quantity} available, requested {qty}",
                })
                continue
            tx_type = "waste" if disposition == "waste" else "restock"
            InventoryTransaction.objects.create(
                product_id=sale_item.product_id,
                transaction_type=tx_type,
                quantity=qty,
                reference=f"return_sale_{pk}",
                inventory_id="main",
                notes=notes or f"Return from sale #{pk}: {sale_item.product_name}",
            )
            sale_item.quantity -= qty
            partial_line_total = sale_item.unit_price * qty
            refunded_total += partial_line_total
            sale_item.line_total = Decimal("0.00") if sale_item.quantity <= 0 else sale_item.unit_price * sale_item.quantity
            sale_item.save(update_fields=["quantity", "line_total", "updated_at"])
            results.append({
                "sale_item_id": si_id,
                "product_name": sale_item.product_name,
                "quantity_returned": qty,
                "disposition": disposition,
                "status": "returned",
            })
        all_returned = SaleItem.objects.filter(sale=sale, quantity__gt=0).count() == 0
        sale.subtotal -= refunded_total
        sale.total = sale.subtotal - sale.discount_amount + sale.tax_amount - sale.cashback_amount
        if sale.total < 0:
            sale.total = Decimal("0.00")
        return_cashback = Decimal(str(body.get("cashback_amount", 0)))
        if return_cashback:
            sale.cashback_amount += return_cashback
        if all_returned:
            sale.status = "refunded"
            sale.total = Decimal("0.00")
        sale.save(update_fields=["subtotal", "total", "cashback_amount", "status", "updated_at"])
    return _json({
        "sale_id": pk,
        "status": "refunded" if all_returned else "partially_returned",
        "items_returned": len([r for r in results if r.get("status") == "returned"]),
        "refunded_amount": float(refunded_total),
        "sale_total": float(sale.total),
        "sale_cashback": float(sale.cashback_amount),
        "results": results,
    })


def sync_status(request: HttpRequest) -> JsonResponse:
    state = _load_sync_state()
    return _json({
        "config": {
            "enabled": state.get("enabled", True),
            "cloud_url": state.get("cloud_url", os.environ.get("CLOUD_CRM_URL", "")),
            "status": state.get("status", "idle"),
            "last_sync": state.get("last_sync"),
            "items_synced": state.get("items_synced", 0),
            "errors": state.get("errors", 0),
        },
        "local_logs": {
            "total_logs": SyncLog.objects.count(),
            "pending": SyncLog.objects.filter(status="pending").count(),
            "failed": SyncLog.objects.filter(status="failed").count(),
            "success": SyncLog.objects.filter(status="success").count(),
        },
        "cloud_crm": {"status": "ok"},
    })


def sync_config(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    state = _load_sync_state()
    if "cloud_url" in body:
        state["cloud_url"] = body["cloud_url"]
    if "api_key" in body:
        state["api_key"] = body["api_key"]
    if "enabled" in body:
        state["enabled"] = bool(body["enabled"])
    _save_sync_state(state)
    return _json({"status": "ok", "config": state})


def sync_log(request: HttpRequest) -> JsonResponse:
    limit = min(int(request.GET.get("limit", "50")), 200)
    qs = SyncLog.objects.all().order_by("-created_at")[:limit]
    state = _load_sync_state()
    entries = [{
        "id": log.id, "node_id": log.node_id,
        "entity_type": log.entity_type, "entity_id": log.entity_id,
        "direction": log.direction, "status": log.status,
        "error_message": log.error_message,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    } for log in qs]
    return _json({
        "entries": entries, "total": len(entries),
        "sync_config": {
            "last_sync": state.get("last_sync"),
            "status": state.get("status", "idle"),
            "items_synced": state.get("items_synced", 0),
            "errors": state.get("errors", 0),
        },
    })


def create_sale_with_items(request: HttpRequest) -> JsonResponse:
    """Legacy alias — delegates to ``sale_checkout``."""
    return sale_checkout(request)


def sale_checkout(request: HttpRequest) -> JsonResponse:
    """POST /sales/ — Full checkout: Sale + SaleItems + KitchenTicket in a single tx.

    Expects JSON body::

        {
            "customer_id": 2,                  # optional
            "items": [
                {
                    "product_id": 5,
                    "product_name": "Latte",
                    "quantity": 2,
                    "unit_price": 4.50,
                    "line_total": 9.00,
                    "notes": "extra shot"       # optional
                }
            ],
            "subtotal": 9.00,
            "tax_amount": 0.72,
            "discount_amount": 0.00,
            "total": 9.72,
            "payment_method": "card",          # cash | card | mobile | mixed | credit
            "status": "completed",              # pending | completed
            "notes": "",                        # optional sale-level note
            "create_kitchen_ticket": true,      # default true — creates a KDS ticket
            "kitchen_priority": 0,              # 0 = normal, 1 = rush, 2 = urgent
            "kitchen_prep_minutes": 15,         # estimated prep time
            "order_type": "dine-in",            # dine-in | takeaway | delivery
            "table_number": 7,                  # for dine-in
        }

    Returns 201 with the created Sale, its items, and the KitchenTicket::

        {
            "sale_id": 42,
            "status": "completed",
            "total": 9.72,
            "items": [ ... ],
            "kitchen_ticket": { "id": 15, "status": "pending", ... } | null,
            "stock_deductions": [ ... ]
        }

    Everything runs inside ``transaction.atomic()`` — if stock is
    insufficient or any model fails, the whole sale rolls back.
    """
    # ── Parse & validate ─────────────────────────────────────────────
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    items_data = body.get("items")
    if not items_data or not isinstance(items_data, list) or len(items_data) == 0:
        return _error(400, "At least one item is required")

    # ── Build the sale inside an atomic block ─────────────────────────
    with db_transaction.atomic():
        # Resolve customer (optional)
        customer = None
        customer_id = body.get("customer_id")
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return _error(400, f"Customer {customer_id} not found")

        # Create the Sale
        sale = Sale.objects.create(
            customer=customer,
            subtotal=Decimal(str(body.get("subtotal", 0))),
            tax_amount=Decimal(str(body.get("tax_amount", 0))),
            discount_amount=Decimal(str(body.get("discount_amount", 0))),
            total=Decimal(str(body.get("total", 0))),
            payment_method=body.get("payment_method", "cash"),
            status=body.get("status", "completed"),
            notes=body.get("notes", ""),
        )

        # Create SaleItems + deduct stock
        sale_items_out = []
        stock_deductions = []

        for idx, item in enumerate(items_data):
            product_id = item.get("product_id")
            quantity = int(item.get("quantity", 1))
            unit_price = Decimal(str(item.get("unit_price", 0)))
            line_total = Decimal(str(item.get("line_total", unit_price * quantity)))

            if quantity <= 0:
                return _error(400, f"Item {idx}: quantity must be positive")

            # Resolve product (required for stock deduction)
            product = None
            if product_id:
                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    return _error(400, f"Item {idx}: Product {product_id} not found")

                # Deduct stock
                if product.stock_quantity is not None and product.stock_quantity < quantity:
                    return _error(
                        409,
                        f"Insufficient stock for '{product.name}': "
                        f"requested {quantity}, available {product.stock_quantity}",
                    )
                if product.stock_quantity is not None:
                    product.stock_quantity -= quantity
                    product.save(update_fields=["stock_quantity", "updated_at"])

                    inv_tx = InventoryTransaction.objects.create(
                        product=product,
                        transaction_type="out",
                        quantity=quantity,
                        reference=f"sale_{sale.id}",
                        inventory_id="main",
                        notes=f"Sold {quantity}x {item.get('product_name', product.name)}",
                    )
                    stock_deductions.append(_ser_model(inv_tx))

            # Create the line item
            sale_item = SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=item.get("product_name", product.name if product else "Unknown"),
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
                notes=item.get("notes", ""),
            )
            sale_items_out.append(_ser_model(sale_item))

        # Create KitchenTicket (when requested and there are items)
        kitchen_ticket = None
        if body.get("create_kitchen_ticket", True) and sale_items_out:
            kitchen_ticket = KitchenTicket.objects.create(
                sale=sale,
                status="pending",
                priority=body.get("kitchen_priority", 0),
                prepare_time_minutes=body.get("kitchen_prep_minutes", 15),
                notes=body.get("kitchen_notes", "") or f"Order for Sale #{sale.id}",
            )

        # Save custom metadata on the sale for KDS enrichment
        order_type = body.get("order_type")
        table_number = body.get("table_number")
        if order_type or table_number:
            # Store in the sale's notes as structured JSON for downstream enrichment
            meta = {}
            if order_type:
                meta["order_type"] = order_type
            if table_number is not None:
                meta["table_number"] = table_number
            if sale.notes:
                meta["_original_notes"] = sale.notes
            sale.notes = json.dumps(meta)
            sale.save(update_fields=["notes"])

    # ── Build response (outside atomic block) ─────────────────────────
    response = {
        "sale_id": sale.id,
        "status": sale.status,
        "subtotal": float(sale.subtotal),
        "tax_amount": float(sale.tax_amount),
        "discount_amount": float(sale.discount_amount),
        "total": float(sale.total),
        "payment_method": sale.payment_method,
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "items": sale_items_out,
        "item_count": len(sale_items_out),
        "kitchen_ticket": _ser_model(kitchen_ticket) if kitchen_ticket else None,
        "stock_deductions": stock_deductions,
    }

    # Broadcast entity change to WebSocket clients
    broadcast_entities({
        "type": "sale_created",
        "entity": "sale",
        "id": sale.id,
        "total": float(sale.total),
    })

    return _json(response, status=201)


def sync_trigger(request: HttpRequest) -> JsonResponse:
    # Stub — full sync trigger needs async cloud client; returns status
    return _json({"triggered": False, "note": "Sync trigger migrated; full async cloud client pending Channels integration"})


def cloud_push(request: HttpRequest, entity_type: str) -> JsonResponse:
    valid = {"nodes", "heartbeats", "events", "products", "sales", "customers", "inventory"}
    if entity_type not in valid:
        return _json({"error": f"invalid type: {entity_type}", "valid": list(valid)})
    return _json({"status": "pushed", "entity_type": entity_type, "note": "Cloud push — async client pending"})


def receive_push(request: HttpRequest, entity_type: str) -> JsonResponse:
    valid = {"nodes", "heartbeats", "events", "products", "sales", "customers", "inventory"}
    if entity_type not in valid:
        return _json({"error": f"invalid type: {entity_type}", "valid": list(valid)})
    body = json.loads(request.body) if request.body else {}
    SyncLog.objects.create(
        node_id=body.get("node_id", "unknown"),
        entity_type=entity_type, entity_id=body.get("id", ""),
        direction="push", status="success",
        payload_size=len(json.dumps(body)),
    )
    broadcast_nodes({"type": "sync_push", "node_id": body.get("node_id", "unknown"), "data": {
        "entity_type": entity_type, "payload_size": len(json.dumps(body)),
        "node_id": body.get("node_id"),
    }})
    return _json({
        "status": "received", "entity_type": entity_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ═══════════════════════════════════════════════════════════════════════════
# Data routes (was routes/data.py)
# ═══════════════════════════════════════════════════════════════════════════

def list_transactions(request: HttpRequest) -> JsonResponse:
    limit = int(request.GET.get("limit", "50"))
    offset = int(request.GET.get("offset", "0"))
    qs = Sale.objects.all().order_by("-created_at")
    total = qs.count()
    sales = qs[offset:offset + limit]
    result = []
    for sale in sales:
        items = list(sale.items.all().values("product_name", "quantity", "unit_price", "line_total"))
        result.append({
            "id": sale.id,
            "items": [{
                "name": i["product_name"],
                "price": float(i["unit_price"]),
                "quantity": i["quantity"],
                "unit": "pcs",
                "subtotal": float(i["line_total"]),
            } for i in items],
            "total_amount": float(sale.total),
            "currency": "USD",
            "date": sale.sale_date.strftime("%Y-%m-%d") if sale.sale_date else "",
            "time": sale.sale_date.strftime("%H:%M") if sale.sale_date else "",
            "order_type": sale.payment_method or "dine-in",
            "status": sale.status or "completed",
        })
    return _json({"data": result, "total": total, "returned": len(result)})


def get_transaction_detail(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        sale = Sale.objects.get(id=pk)
    except Sale.DoesNotExist:
        return _error(404, "Transaction not found")
    items = list(sale.items.all().values("product_name", "quantity", "unit_price", "line_total"))
    return _json({
        "id": sale.id,
        "items": [{
            "name": i["product_name"],
            "price": float(i["unit_price"]),
            "quantity": i["quantity"],
            "unit": "pcs",
            "subtotal": float(i["line_total"]),
        } for i in items],
        "total_amount": float(sale.total),
        "currency": "USD",
        "date": sale.sale_date.strftime("%Y-%m-%d") if sale.sale_date else "",
        "time": sale.sale_date.strftime("%H:%M") if sale.sale_date else "",
        "order_type": sale.payment_method or "dine-in",
        "status": sale.status or "completed",
    })


def get_analytics(request: HttpRequest) -> JsonResponse:
    """Data & Analytics dashboard endpoint — scoped by ``?days=N`` query param.

    Query params:
        days (int): Lookback window in days. Clamped between 7 and 365.
                    Default 30. All sections (daily_revenue, top_products,
                    product_distribution, and summary) are scoped to the
                    same window so switching periods gives consistent results.

    Comparison mode: the response also includes ``previous_period`` — the
    daily revenue + summary for the *preceding* window of the same length
    (e.g. days=7 → current week vs the week before), so the frontend can
    overlay a second transparent series.
    """
    try:
        window_days = int(request.GET.get("days", "30"))
    except (ValueError, TypeError):
        window_days = 30
    window_days = max(7, min(window_days, 365))

    # Windows are whole calendar days ending yesterday, so a "7d" view is
    # exactly the previous 7 full days and the comparison period is the 7
    # full days before that — no partial-day buckets from ``now``'s clock time.
    cur_end = dj_timezone.localdate() - timedelta(days=1)   # yesterday
    cur_start = cur_end - timedelta(days=window_days - 1)   # inclusive window
    prev_end = cur_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=window_days - 1)

    scoped_sales = Sale.objects.filter(
        sale_date__date__gte=cur_start, sale_date__date__lte=cur_end,
        status="completed",
    )

    def _daily_series(qs, start, end):
        """Group a sale queryset into one row per day from ``start``..``end``.

        Days without sales are zero-filled (revenue=0, orders=0) so the series
        is exactly window-aligned — the frontend overlay compares index-to-
        index, mapping to the same weekday in both periods.
        """
        rows = {
            d["day"]: {
                "date": str(d["day"]),
                "revenue": float(d["revenue"] or 0),
                "orders": d["orders"],
            }
            for d in (
                qs.annotate(day=TruncDate("sale_date"))
                .values("day")
                .annotate(revenue=Sum("total"), orders=Count("id"))
            )
        }
        return [
            rows.get(start + timedelta(days=offset), {
                "date": str(start + timedelta(days=offset)),
                "revenue": 0.0,
                "orders": 0,
            })
            for offset in range((end - start).days + 1)
        ]

    # Daily revenue chart — current window (zero-filled, weekday-aligned)
    daily_revenue = _daily_series(scoped_sales, cur_start, cur_end)

    # Previous-period window (same length, immediately preceding)
    previous_sales = Sale.objects.filter(
        sale_date__date__gte=prev_start, sale_date__date__lte=prev_end,
        status="completed",
    )
    previous_daily_revenue = _daily_series(previous_sales, prev_start, prev_end)
    prev_agg = previous_sales.aggregate(
        total_revenue=Sum("total"), total_orders=Count("id"),
    )
    prev_rev = float(prev_agg["total_revenue"] or 0)
    prev_orders = prev_agg["total_orders"] or 0

    # Top products — scope SaleItem aggregation to sales within the window
    scoped_sale_ids = scoped_sales.values_list("id", flat=True)
    top_items = (
        SaleItem.objects.filter(sale_id__in=scoped_sale_ids)
        .values("product_name")
        .annotate(sales=Sum("quantity"), revenue=Sum("line_total"))
        .order_by("-revenue")[:10]
    )
    top_products = [
        {"name": t["product_name"], "sales": int(t["sales"] or 0), "revenue": float(t["revenue"] or 0)}
        for t in top_items
    ]

    # Previous-period top products — a *lookup map* keyed by product name so
    # the frontend can annotate each current top product with its previous-
    # period revenue/sales (comparison column). Computed over the full prior
    # window (no [:10] limit) so products outside the current top-10 that sold
    # in the prior period still resolve.
    previous_sale_ids = previous_sales.values_list("id", flat=True)
    prev_top_items = (
        SaleItem.objects.filter(sale_id__in=previous_sale_ids)
        .values("product_name")
        .annotate(sales=Sum("quantity"), revenue=Sum("line_total"))
    )
    previous_top_products = {
        t["product_name"]: {
            "sales": int(t["sales"] or 0),
            "revenue": float(t["revenue"] or 0),
        }
        for t in prev_top_items
    }

    # Category distribution — scope to window
    by_category = (
        SaleItem.objects.filter(sale_id__in=scoped_sale_ids, product__category__isnull=False)
        .values("product__category__name")
        .annotate(value=Sum("quantity"))
        .order_by("-value")
    )
    product_distribution = [
        {"name": c["product__category__name"], "value": int(c["value"] or 0)}
        for c in by_category
    ]

    # Summary — scoped to the same window
    agg = scoped_sales.aggregate(total_revenue=Sum("total"), total_orders=Count("id"))
    total_rev = float(agg["total_revenue"] or 0)
    total_orders = agg["total_orders"] or 0

    return _json({
        "daily_revenue": daily_revenue,
        "previous_daily_revenue": previous_daily_revenue,
        "top_products": top_products,
        "previous_top_products": previous_top_products,
        "product_distribution": product_distribution,
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_rev,
            "average_order_value": round(total_rev / max(total_orders, 1), 2),
        },
        "previous_summary": {
            "total_orders": prev_orders,
            "total_revenue": prev_rev,
            "average_order_value": round(prev_rev / max(prev_orders, 1), 2),
        },
        "meta": {
            "days": window_days,
            "start": str(cur_start),
            "end": str(cur_end),
            "previous_start": str(prev_start),
        },
    })


# ═══════════════════════════════════════════════════════════════════════════
# Approval routes (was routes/approvals.py)
# ═══════════════════════════════════════════════════════════════════════════

def approval_approve(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        approval = SyncApproval.objects.get(id=pk)
        approval.status = "approved"
        approval.save()
        return _json({"status": "approved", "id": pk})
    except SyncApproval.DoesNotExist:
        return _error(404, "Approval not found")


def approval_reject(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        approval = SyncApproval.objects.get(id=pk)
        approval.status = "rejected"
        approval.save()
        return _json({"status": "rejected", "id": pk})
    except SyncApproval.DoesNotExist:
        return _error(404, "Approval not found")


def approval_stats(request: HttpRequest) -> JsonResponse:
    total = SyncApproval.objects.count()
    pending = SyncApproval.objects.filter(status="pending").count()
    approved = SyncApproval.objects.filter(status="approved").count()
    rejected = SyncApproval.objects.filter(status="rejected").count()
    return _json({"total": total, "pending": pending, "approved": approved, "rejected": rejected})


def approval_pending(request: HttpRequest) -> JsonResponse:
    qs = SyncApproval.objects.filter(status="pending").order_by("-created_at")[:100]
    return _json([_ser_model(a) for a in qs])


# ═══════════════════════════════════════════════════════════════════════════
# Webhook routes (was routes/webhooks.py)
# ═══════════════════════════════════════════════════════════════════════════

def webhook_receive(request: HttpRequest, signal_name: str) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    SignalEvent.objects.create(
        node_id=body.get("node_id", "unknown"),
        event_type=f"webhook_{signal_name}",
        description=body.get("description", f"Webhook: {signal_name}"),
        metadata=body.get("metadata", {}),
        payload=body,
    )
    return _json({"status": "received", "signal": signal_name})


def webhook_list(request: HttpRequest) -> JsonResponse:
    qs = SignalEvent.objects.filter(event_type__startswith="webhook_").order_by("-created_at")[:50]
    return _json([_ser_model(e) for e in qs])


def webhook_stats(request: HttpRequest) -> JsonResponse:
    total = SignalEvent.objects.filter(event_type__startswith="webhook_").count()
    return _json({"total_webhooks": total})


# ═══════════════════════════════════════════════════════════════════════════
# Config routes (was routes/config.py — non-WS endpoints)
# ═══════════════════════════════════════════════════════════════════════════

def config_cloud_link_test(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        link = CloudLink.objects.get(id=pk)
        return _json({"status": "ok", "tested": True, "url": link.url})
    except CloudLink.DoesNotExist:
        return _error(404, "CloudLink not found")


def config_master_sync(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        master = MasterDevice.objects.get(id=pk)
        return _json({"status": "ok", "synced": True, "master": str(master.name)})
    except MasterDevice.DoesNotExist:
        return _error(404, "MasterDevice not found")


# ═══════════════════════════════════════════════════════════════════════════
# CRM routes (was routes/crm.py)
# ═══════════════════════════════════════════════════════════════════════════

def crm_dashboard(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Company, Contact, Deal
    return _json({
        "companies": Company.objects.count(),
        "contacts": Contact.objects.count(),
        "deals": Deal.objects.count(),
    })


def crm_contacts(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Contact
    return _json([_ser_model(c) for c in Contact.objects.all()[:100]])


def crm_contact_detail(request: HttpRequest, contact_id: int) -> JsonResponse:
    from models.crm_models import Contact
    try:
        return _json(_ser_model(Contact.objects.get(id=contact_id)))
    except Contact.DoesNotExist:
        return _error(404, "Contact not found")


def crm_contact_create(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Contact
    body = json.loads(request.body) if request.body else {}
    contact = Contact.objects.create(**body)
    return _json(_ser_model(contact), status=201)


def crm_companies(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Company
    return _json([_ser_model(c) for c in Company.objects.all()[:100]])


def crm_deals(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Deal
    return _json([_ser_model(d) for d in Deal.objects.all()[:100]])


def crm_deal_create(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Deal
    body = json.loads(request.body) if request.body else {}
    deal = Deal.objects.create(**body)
    return _json(_ser_model(deal), status=201)


def crm_pipelines(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Pipeline
    return _json([_ser_model(p) for p in Pipeline.objects.all()])


def crm_activities(request: HttpRequest) -> JsonResponse:
    from models.crm_models import Activity
    return _json([_ser_model(a) for a in Activity.objects.all()[:100]])


def crm_notes(request: HttpRequest) -> JsonResponse:
    from models.crm_models import CRMNote
    return _json([_ser_model(n) for n in CRMNote.objects.all()[:100]])


# ═══════════════════════════════════════════════════════════════════════════
# Reports routes (was routes/reports.py)
# ═══════════════════════════════════════════════════════════════════════════

def report_sales(request: HttpRequest) -> JsonResponse:
    """Sales report with payment-method revenue breakdown, AOV, tax, and daily trend.

    Returns::
        {
            "total_revenue": 4633.20,
            "total_sales": 291,
            "avg_order_value": 15.92,
            "tax_collected": 370.66,
            "by_payment": {
                "card":  {"count": 131, "revenue": 2100.50},
                "cash":  {"count": 87,  "revenue": 1450.75},
                ...
            },
            "daily_trend": [
                {"date": "2026-07-31", "total": 328.32, "orders": 15, "label": "Thu"},
                ...
            ]
        }
    """
    completed = Sale.objects.filter(status="completed")
    total_rev = completed.aggregate(s=Sum("total"))["s"] or 0

    # Count + revenue per payment method
    payment_data = {}
    for row in (
        completed.values("payment_method")
        .annotate(n=Count("id"), rev=Sum("total"))
        .values_list("payment_method", "n", "rev")
    ):
        payment_data[row[0]] = {"count": row[1], "revenue": float(row[2] or 0)}

    # Tax collected (approximation: 8% of subtotal or use stored tax_amount)
    tax = completed.aggregate(t=Sum("tax_amount"))["t"] or 0

    # Daily trend — last 7 days (real data from DB)
    now = dj_timezone.now()
    week_ago = now - timedelta(days=7)
    daily_qs = (
        completed.filter(sale_date__gte=week_ago)
        .annotate(day=TruncDate("sale_date"))
        .values("day")
        .annotate(revenue=Sum("total"), orders=Count("id"))
        .order_by("day")
    )
    daily_trend = [
        {
            "date": str(d["day"]),
            "total": float(d["revenue"] or 0),
            "orders": d["orders"],
            "label": d["day"].strftime("%a") if d["day"] else "",
        }
        for d in daily_qs
    ]

    return _json({
        "total_revenue": float(total_rev),
        "total_sales": completed.count(),
        "avg_order_value": round(float(total_rev) / max(completed.count(), 1), 2),
        "tax_collected": float(tax),
        "by_payment": payment_data,
        "daily_trend": daily_trend,
    })


def report_inventory(request: HttpRequest) -> JsonResponse:
    """Inventory report with value, stock levels, and transaction breakdown.

    Returns::
        {
            "total_transactions": 12,
            "stock_in": 0,
            "stock_out": 0,
            "total_products": 18,
            "total_inventory_value": 1845.25,
            "low_stock_items": [
                {"id": 5, "name": "Latte", "stock": 3, "threshold": 10},
                ...
            ],
            "recent_transactions": [
                {"id": 1, "type": "out", "product": "Latte", "quantity": 2, "date": "..."},
                ...
            ]
        }
    """
    txs = InventoryTransaction.objects.all()

    # Inventory value: sum(cost_price * stock_quantity) across active products
    value_agg = (
        Product.objects.filter(is_active=True)
        .aggregate(v=Sum(F("cost_price") * F("stock_quantity")))
    )
    total_value = value_agg["v"] or Decimal("0.00")

    # Low stock items
    products = Product.objects.filter(is_active=True)
    low_stock = []
    for p in products:
        if (
            p.stock_quantity is not None
            and p.low_stock_threshold is not None
            and p.stock_quantity <= p.low_stock_threshold
        ):
            low_stock.append({
                "id": p.id,
                "name": p.name,
                "stock": p.stock_quantity,
                "threshold": p.low_stock_threshold,
            })

    # Recent inventory transactions (last 20)
    recent_txs = []
    for t in txs.select_related("product").order_by("-created_at")[:20]:
        recent_txs.append({
            "id": t.id,
            "type": t.transaction_type,
            "product": t.product.name if t.product else "Unknown",
            "quantity": t.quantity,
            "date": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "",
            "reference": t.reference or "",
        })

    return _json({
        "total_transactions": txs.count(),
        "stock_in": txs.filter(transaction_type="stock_in").count(),
        "stock_out": txs.filter(transaction_type__in=["stock_out", "out"]).count(),
        "total_products": products.count(),
        "total_inventory_value": float(total_value),
        "low_stock_items": low_stock,
        "recent_transactions": recent_txs,
    })


# ═══════════════════════════════════════════════════════════════════════════
# forge-gaps model views (coupons, delivery-types, delivery-zones, shifts)
# ═══════════════════════════════════════════════════════════════════════════

def list_coupons(request: HttpRequest) -> JsonResponse:
    return _json([_ser_model(c) for c in Coupon.objects.all().order_by("-created_at")])

def list_delivery_types(request: HttpRequest) -> JsonResponse:
    return _json([_ser_model(d) for d in DeliveryType.objects.all().order_by("name")])

def list_delivery_zones(request: HttpRequest) -> JsonResponse:
    return _json([_ser_model(z) for z in DeliveryZone.objects.all().order_by("name")])

def list_shifts(request: HttpRequest) -> JsonResponse:
    return _json([_ser_model(s) for s in Shift.objects.all().order_by("-opened_at")])
