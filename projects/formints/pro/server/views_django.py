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
from models.menu import Menu, MenuItem, MenuItemAssignment, MenuVersion, publish_menu_version
from models.node import Heartbeat, Node, NodeEvent
from models.notes import Note
from models.ops import KitchenStation, KitchenTicket, SupportTicket, route_station_for_sale
from models.pos import (
    Category,
    Customer,
    Employee,
    InventoryTransaction,
    Product,
    Sale,
    SaleGroup,
    SaleItem,
)
from services.split_merge import (
    SplitMergeError,
    merge_group,
    merge_sale,
    split_sale,
)
from models.sync import SyncLog
from models.token import DeviceToken

from services.sync import ProductSyncEngine
from services.sync_changes import SyncChangeCollector, entity_types
from services.outbox import OfflineQueueService
from services.barcode import barcode_label_svg, resolve_product
from services.gaming import (
    GamingError,
    _elapsed_seconds,
    assign_next,
    cancel_queue_entry,
    enqueue,
    estimated_wait_minutes,
    pause_session,
    resume_session,
    start_session,
    stop_session,
)
from models.gaming import (
    GamingQueueEntry,
    GamingSession,
    GamingStation,
    GamingToken,
)
from models.giftcard import GiftCard, GiftCardTransaction
from services.giftcard import (
    GiftCardError,
    disable as giftcard_disable,
    get_card as giftcard_get,
    issue as giftcard_issue,
    redeem as giftcard_redeem,
    reload as giftcard_reload,
)
from models.tables import RestaurantTable, TableReservation
from services import tables as tables_svc
from models.delivery import DeliveryOrder, DeliveryProvider
from services import delivery as delivery_svc
from services import forecast as forecast_svc
from models.hr import EmployeeSchedule
from models.timeclock import TimeClockEntry
from services import scheduling as sched_svc
from services import customer_display as cd_svc
from services import kiosk as kiosk_svc
from models.kiosk import KioskSession
from services import purchase_orders as po_svc

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
    Employee, MenuItem, Menu, MenuItemAssignment, MenuVersion, Node, Heartbeat,
    NodeEvent, SyncLog, DeviceConfig, MasterDevice, CloudLink,
    SyncApproval, DeviceToken, SignalEvent,
    Supplier, PurchaseOrder, PurchaseOrderItem,
    KitchenStation, KitchenTicket, SupportTicket, Payroll, EmployeeSchedule, TaxReport,
    Note, Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
    ClientCategory, LoyaltyTransaction, UserSettings, ApiKey,
    Coupon, DeliveryType, DeliveryZone, Shift,
    GamingStation, GamingToken, GamingSession, GamingQueueEntry,
    GiftCard, GiftCardTransaction,
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

def _ser_station(station: KitchenStation | None) -> dict | None:
    """Serialize a kitchen station (or None) for KDS payloads."""
    if station is None:
        return None
    return {
        "id": station.id,
        "name": station.name,
        "slug": station.slug,
        "station_type": station.station_type,
        "sort_order": station.sort_order,
        "is_active": station.is_active,
    }


def _ser_kds_ticket(ticket: KitchenTicket) -> dict:
    """Serialize a kitchen ticket with sale + station enrichment."""
    data = _ser_model(ticket)
    if "sale_id" not in data:
        data["sale_id"] = ticket.sale_id
    sale = ticket.sale
    data["order_type"] = getattr(sale, "order_type", "dine-in")
    data["table_number"] = getattr(sale, "table_number", None)
    data["delivery_address"] = getattr(sale, "delivery_address", None)
    data["total_amount"] = (
        float(sale.total_amount) if hasattr(sale, "total_amount") and sale.total_amount else None
    )
    data["station"] = _ser_station(ticket.station)
    return data


def kds_list_tickets(request: HttpRequest) -> JsonResponse:
    status_filter = request.GET.get("status", "").strip() or None
    station_filter = request.GET.get("station", "").strip() or None
    qs = KitchenTicket.objects.select_related("sale", "station").all()
    if status_filter and status_filter != "all":
        qs = qs.filter(status=status_filter)
    if station_filter and station_filter != "all":
        qs = qs.filter(station__slug=station_filter)
    qs = qs.order_by("-priority", "created_at")[:200]
    return _json([_ser_kds_ticket(t) for t in qs])


def kds_get_ticket(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        ticket = KitchenTicket.objects.select_related("sale", "station").get(id=pk)
    except KitchenTicket.DoesNotExist:
        return _error(404, "Ticket not found")
    return _json(_ser_kds_ticket(ticket))


def kds_update_ticket(request: HttpRequest, pk: int) -> JsonResponse:
    try:
        ticket = KitchenTicket.objects.select_related("sale", "station").get(id=pk)
    except KitchenTicket.DoesNotExist:
        return _error(404, "Ticket not found")
    body = json.loads(request.body) if request.body else {}
    now = datetime.now(timezone.utc)
    if "status" in body:
        ticket.status = body["status"]
        if body["status"] == "preparing" and not ticket.started_at:
            ticket.started_at = now
        if body["status"] == "ready" and not ticket.ready_at:
            ticket.ready_at = now
        if body["status"] == "delivered" and not ticket.completed_at:
            ticket.completed_at = now
    if "notes" in body:
        ticket.notes = body["notes"]
    if "priority" in body:
        ticket.priority = body["priority"]
    if "prepare_time_minutes" in body:
        ticket.prepare_time_minutes = body["prepare_time_minutes"]
    if "station_id" in body or "station" in body:
        station_id = body.get("station_id") or body.get("station")
        if station_id is None:
            ticket.station = None
        else:
            try:
                ticket.station = KitchenStation.objects.get(id=int(station_id))
            except (TypeError, ValueError, KitchenStation.DoesNotExist):
                return _error(400, f"Unknown station id: {station_id}")
    ticket.save()
    return _json(_ser_kds_ticket(ticket))


def kds_list_stations(request: HttpRequest) -> JsonResponse:
    qs = KitchenStation.objects.all().order_by("sort_order", "name")
    return _json([_ser_station(s) for s in qs])


def kds_create_station(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    name = (body.get("name") or "").strip()
    if not name:
        return _error(400, "Station name is required")
    slug = (body.get("slug") or "").strip()
    if not slug:
        from django.utils.text import slugify
        slug = slugify(name)
    if KitchenStation.objects.filter(slug=slug).exists():
        return _error(409, f"Station slug '{slug}' already exists")
    station = KitchenStation.objects.create(
        name=name,
        slug=slug,
        station_type=body.get("station_type", "expedite"),
        category_keywords=body.get("category_keywords", ""),
        sort_order=body.get("sort_order", 0),
        is_active=body.get("is_active", True),
    )
    return _json(_ser_station(station))


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
# QR Menu routes — versioned, localized, publishable menus + QR
# ═══════════════════════════════════════════════════════════════════════════

def _ser_menu_version(v: MenuVersion) -> dict:
    return {
        "id": v.id,
        "menu_id": v.menu_id,
        "menu_name": v.menu.name,
        "menu_slug": v.menu.slug,
        "version": v.version,
        "locale": v.locale,
        "status": v.status,
        "published_at": v.published_at.isoformat() if v.published_at else None,
        "preview_token": v.preview_token or None,
    }


def _ser_menu_with_items(menu: Menu) -> dict:
    """Serialize a menu grouped by category for public display."""
    categories: dict[str, list[dict]] = {}
    assignments = menu.menuitemassignment_set.select_related("item__category").order_by(
        "display_order", "item__display_order", "item__name"
    )
    for assignment in assignments:
        item = assignment.item
        if not item.is_available:
            continue
        cat = item.category.name if item.category else "Other"
        categories.setdefault(cat, []).append({
            "id": item.id,
            "name": item.name,
            "slug": item.slug,
            "description": item.description,
            "price": float(assignment.override_price or item.price),
            "currency": item.currency,
            "is_featured": item.is_featured,
            "preparation_time": item.preparation_time,
            "allergens": item.allergens,
            "calories": item.calories,
        })
    return {
        "id": menu.id,
        "name": menu.name,
        "slug": menu.slug,
        "description": menu.description,
        "categories": [{"name": k, "items": v} for k, v in categories.items()],
    }


def menu_list_published(request: HttpRequest) -> JsonResponse:
    locale = request.GET.get("locale", "").strip() or None
    versions = MenuVersion.objects.select_related("menu").filter(status="published")
    if locale:
        versions = versions.filter(locale=locale)
    return _json([_ser_menu_version(v) for v in versions.order_by("-published_at")])


def menu_publish(request: HttpRequest, menu_id: int) -> JsonResponse:
    body = json.loads(request.body) if request.body else {}
    locale = (body.get("locale") or "en").strip()
    try:
        menu = Menu.objects.get(id=menu_id)
    except Menu.DoesNotExist:
        return _error(404, "Menu not found")
    version = publish_menu_version(menu, locale)
    return _json(_ser_menu_version(version))


def menu_preview(request: HttpRequest, menu_id: int) -> JsonResponse:
    try:
        menu = Menu.objects.get(id=menu_id)
    except Menu.DoesNotExist:
        return _error(404, "Menu not found")
    locale = request.GET.get("locale", "en")
    token = request.GET.get("token", "")
    draft = MenuVersion.objects.filter(menu=menu, locale=locale, status="draft").order_by("-version").first()
    if draft is not None:
        if draft.preview_token and draft.preview_token != token:
            return _error(403, "Invalid preview token")
        return _json(_ser_menu_with_items(menu))
    published = MenuVersion.objects.filter(menu=menu, locale=locale, status="published").order_by("-version").first()
    if published is None:
        return _error(404, "No menu version available")
    return _json(_ser_menu_with_items(menu))


def _get_menu_by_slug(slug: str) -> Menu | None:
    try:
        return Menu.objects.get(slug=slug)
    except Menu.DoesNotExist:
        return None


def menu_public(request: HttpRequest, slug: str) -> JsonResponse:
    """Public, slug-keyed menu for a scanned QR link."""
    menu = _get_menu_by_slug(slug)
    if menu is None:
        return _error(404, "Menu not found")
    locale = request.GET.get("locale", "en")
    published = MenuVersion.objects.filter(
        menu=menu, locale=locale, status="published",
    ).order_by("-version").first()
    if published is None:
        return _error(404, "No published menu version for this locale")
    data = _ser_menu_with_items(menu)
    data["version"] = _ser_menu_version(published)
    return _json(data)


def menu_qr(request: HttpRequest, slug: str) -> HttpResponse:
    """Return an SVG QR code pointing at a menu's public page."""
    menu = _get_menu_by_slug(slug)
    if menu is None:
        return _error(404, "Menu not found")
    branch = request.GET.get("branch", "").strip()
    table = request.GET.get("table", "").strip()
    locale = request.GET.get("locale", "en")
    url = f"/menu/{menu.slug}/?locale={locale}"
    if branch:
        url += f"&branch={branch}"
    if table:
        url += f"&table={table}"
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        return _error(501, "QR code generation is unavailable (install 'qrcode')")
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage)
    import io
    buf = io.StringIO()
    img.save(buf)
    return HttpResponse(buf.getvalue(), content_type="image/svg+xml")


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
            # Route to a station: explicit override wins, else category match,
            # else the default expedite station.
            station = None
            if body.get("kitchen_station_id"):
                try:
                    station = KitchenStation.objects.get(id=int(body["kitchen_station_id"]))
                except (TypeError, ValueError, KitchenStation.DoesNotExist):
                    station = None
            if station is None:
                station = route_station_for_sale(sale)

            kitchen_ticket = KitchenTicket.objects.create(
                sale=sale,
                station=station,
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


# ── Mobile Waiter P1 — split / merge bill ─────────────────────────────

def _ser_group(group) -> dict:
    return {
        "id": group.id,
        "group_key": group.group_key,
        "name": group.name,
        "table_number": group.table_number,
        "order_type": group.order_type,
        "status": group.status,
        "total": float(group.total),
        "created_at": group.created_at.isoformat() if group.created_at else None,
        "closed_at": group.closed_at.isoformat() if group.closed_at else None,
        "sale_ids": list(group.sales.values_list("id", flat=True)),
    }


def sale_split(request: HttpRequest) -> JsonResponse:
    """POST /sales/split — split a sale's items into child sales under a group.

    Body::

        {
            "sale_id": 10,
            "name": "Table 7",
            "table_number": "7",
            "order_type": "dine-in",
            "splits": [
                {"item_ids": [1, 2], "customer_id": 5, "payment_method": "card"},
                {"item_ids": [3], "payment_method": "cash"}
            ]
        }
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    sale_id = body.get("sale_id")
    splits = body.get("splits")
    if not sale_id or not isinstance(splits, list) or not splits:
        return _error(400, "sale_id and a non-empty splits list are required")

    try:
        group, parent, children = split_sale(
            sale_id=int(sale_id),
            splits=splits,
            name=body.get("name", ""),
            table_number=str(body.get("table_number", "")),
            order_type=body.get("order_type", "dine-in"),
        )
    except SplitMergeError as exc:
        return _error(400, str(exc))
    except Sale.DoesNotExist:
        return _error(404, f"Sale {sale_id} not found")

    return _json({
        "group": _ser_group(group),
        "parent_sale_id": parent.id,
        "children": [{"sale_id": c.id, "total": float(c.total)} for c in children],
    }, status=201)


def sale_merge(request: HttpRequest) -> JsonResponse:
    """POST /sales/merge — merge a split child back into its parent.

    Body: ``{"sale_id": 42}`` or ``{"group_key": "split-10-..."}``.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    try:
        if body.get("group_key"):
            group, parents = merge_group(str(body["group_key"]))
            return _json({
                "group": _ser_group(group),
                "merged_sale_ids": [p.id for p in parents],
            })
        if body.get("sale_id"):
            parent, group = merge_sale(int(body["sale_id"]))
            return _json({
                "parent_sale_id": parent.id,
                "group": _ser_group(group) if group else None,
            })
    except SplitMergeError as exc:
        return _error(400, str(exc))
    except Sale.DoesNotExist:
        return _error(404, "Sale not found")

    return _error(400, "sale_id or group_key is required")


def sale_group_list(request: HttpRequest) -> JsonResponse:
    """GET /sale-groups/ — list split-bill groups (newest first)."""
    groups = SaleGroup.objects.prefetch_related("sales").all()
    return _json({"groups": [_ser_group(g) for g in groups], "count": groups.count()})


def sale_group_detail(request: HttpRequest, group_key: str) -> JsonResponse:
    """GET /sale-groups/<group_key>/ — one group with its sales."""
    try:
        group = SaleGroup.objects.prefetch_related("sales").get(group_key=group_key)
    except SaleGroup.DoesNotExist:
        return _error(404, f"Group {group_key} not found")
    sales = [{
        "sale_id": s.id,
        "total": float(s.total),
        "parent_sale_id": s.parent_sale_id,
        "payment_method": s.payment_method,
        "status": s.status,
    } for s in group.sales.all()]
    data = _ser_group(group)
    data["sales"] = sales
    return _json(data)


def sync_changes(request: HttpRequest) -> JsonResponse:
    """GET /sync/changes/ — pending (unsynced) rows across sync-tracked models.

    Query params: ``entity_type`` (optional) filters to one entity;
    ``types`` (optional, ``?types=1``) returns the tracked entity-type list.
    """
    if request.GET.get("types"):
        return _json({"entity_types": entity_types()})

    entity_type = request.GET.get("entity_type") or None
    try:
        limit = min(int(request.GET.get("limit", "1000")), 5000)
    except ValueError:
        return _error(400, "limit must be an integer")

    collector = SyncChangeCollector()
    return _json(collector.collect(entity_type=entity_type, limit=limit))


def sync_ack(request: HttpRequest) -> JsonResponse:
    """POST /sync/ack/ — mark rows as synced after a peer confirms receipt.

    Body: ``{"entity_type": "product", "ids": [1, 2, 3]}``.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    entity_type = body.get("entity_type")
    ids = body.get("ids")
    if not entity_type or not isinstance(ids, list):
        return _error(400, "entity_type and an ids list are required")

    collector = SyncChangeCollector()
    result = collector.acknowledge(entity_type, [int(i) for i in ids])
    if "error" in result:
        return _error(400, result["error"])
    return _json(result)


def sync_trigger(request: HttpRequest) -> JsonResponse:
    """POST /sync/trigger — broadcast a sync_request so connected terminals pull.

    Real-time half of the multi-terminal contract: notifies every peer on the
    entities channel to call ``GET /sync/changes/``. The request itself does
    not transfer data (peers pull), so this is safe to call from any terminal.
    """
    from consumers import broadcast_entities

    broadcast_entities({
        "type": "sync_request",
        "entity": "sync",
        "action": "pull",
    })
    return _json({"triggered": True, "mechanism": "websocket", "channel": "pos_entities"})


# ── Offline Queue (P1) — queue transactions offline, flush when back online ──

def _ser_outbox(item) -> dict:
    return {
        "id": item.id,
        "node_id": item.node_id,
        "entity_type": item.entity_type,
        "entity_id": item.entity_id,
        "action": item.action,
        "status": item.status,
        "retry_count": item.retry_count,
        "max_retries": item.max_retries,
        "last_error": item.last_error,
        "available_at": item.available_at.isoformat() if item.available_at else None,
        "last_attempt_at": item.last_attempt_at.isoformat() if item.last_attempt_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def offline_queue_list(request: HttpRequest) -> JsonResponse:
    """GET /offline-queue/ — queue health + recent pending/failed entries."""
    from models.outbox import OutboxQueue

    svc = OfflineQueueService()
    recent = list(
        OutboxQueue.objects.filter(status__in=["pending", "failed", "dead"])
        .order_by("-created_at")[:50]
    )
    data = svc.stats()
    data["entries"] = [_ser_outbox(i) for i in recent]
    return _json(data)


def offline_queue_enqueue(request: HttpRequest) -> JsonResponse:
    """POST /offline-queue/enqueue — queue an outbound operation.

    Body: ``{"entity_type": "sale", "entity_id": "42", "action": "push",
    "payload": {...}, "node_id": "till-1"}``.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    entity_type = body.get("entity_type")
    if not entity_type:
        return _error(400, "entity_type is required")

    svc = OfflineQueueService()
    item = svc.enqueue(
        entity_type=entity_type,
        entity_id=str(body.get("entity_id", "")),
        action=body.get("action", "push"),
        payload=body.get("payload") or {},
        node_id=body.get("node_id", ""),
        max_retries=int(body.get("max_retries", 10)),
    )
    return _json({"queued": _ser_outbox(item)}, status=201)


def offline_queue_flush(request: HttpRequest) -> JsonResponse:
    """POST /offline-queue/flush — attempt to push due entries now."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    svc = OfflineQueueService()
    result = svc.flush(
        limit=int(body.get("limit", 100)),
        node_id=body.get("node_id") or None,
    )
    result["stats"] = svc.stats()
    return _json(result)


def offline_queue_requeue(request: HttpRequest) -> JsonResponse:
    """POST /offline-queue/requeue — re-arm dead-lettered entries."""
    svc = OfflineQueueService()
    count = svc.requeue_dead()
    return _json({"requeued": count})


# ═══════════════════════════════════════════════════════════════════════════
# Barcode Scanner P1 — resolve a scanned code + render a label
# ═══════════════════════════════════════════════════════════════════════════

def barcode_resolve(request: HttpRequest, value: str) -> JsonResponse:
    """GET /barcode/<value> — resolve a scanned barcode to a product.

    Exact ``barcode`` match wins; falls back to ``sku`` for legacy labels
    that stored the EAN/UPC in the SKU field. 404 when nothing matches.
    """
    product = resolve_product(value)
    if product is None:
        return _error(404, f"No product matches barcode '{value}'")
    return _json(_ser_model(product))


def barcode_label(request: HttpRequest, value: str) -> HttpResponse:
    """GET /barcode/<value>/label — render a Code128 SVG label for a value.

    Useful for printing shelf/item labels from the same value the scanner
    will later read. Returns 501 when ``python-barcode`` is unavailable.
    """
    try:
        svg = barcode_label_svg(value)
    except ImportError:
        return _error(501, "Barcode label rendering is unavailable (install 'python-barcode')")
    return HttpResponse(svg, content_type="image/svg+xml")


# ═══════════════════════════════════════════════════════════════════════════
# POS-KO Gaming Center P0 — stations, tokens, sessions, queue
# ═══════════════════════════════════════════════════════════════════════════

def _ser_gaming_session(session: GamingSession) -> dict:
    """Serialize a gaming session, reporting live elapsed seconds."""
    data = _ser_model(session)
    data["active_seconds"] = _elapsed_seconds(session)
    return data


def _ser_queue_entry(entry: GamingQueueEntry) -> dict:
    """Serialize a queue entry with its waitlist position + estimate."""
    data = _ser_model(entry)
    data["estimated_wait_minutes"] = estimated_wait_minutes(entry)
    return data


def gaming_stations(request: HttpRequest) -> JsonResponse:
    """GET /gaming/stations — list stations. POST — create a station."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")

        name = (body.get("name") or "").strip()
        if not name:
            return _error(400, "Station name is required")

        from django.utils.text import slugify
        slug = body.get("slug") or slugify(name)
        if not slug:
            return _error(400, "Could not derive a slug from the station name")
        if GamingStation.objects.filter(slug=slug).exists():
            return _error(409, f"Station slug '{slug}' already exists")

        station = GamingStation.objects.create(
            name=name,
            slug=slug,
            station_type=body.get("station_type", "pc"),
            hourly_rate=body.get("hourly_rate", 0),
        )
        return _json(_ser_model(station), status=201)

    stations = GamingStation.objects.filter(is_active=True).order_by("name")
    return _json({"stations": [_ser_model(s) for s in stations]})


def gaming_station_detail(request: HttpRequest, pk: int) -> JsonResponse:
    """GET /gaming/stations/<pk> — station detail + active session."""
    try:
        station = GamingStation.objects.get(id=pk)
    except GamingStation.DoesNotExist:
        return _error(404, f"Station {pk} not found")
    data = _ser_model(station)
    active = station.sessions.filter(status="active").first()
    data["active_session"] = _ser_gaming_session(active) if active else None
    return _json(data)


def gaming_tokens(request: HttpRequest) -> JsonResponse:
    """GET /gaming/tokens — list tokens. POST — purchase a time token."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")

        name = (body.get("name") or "").strip()
        if not name:
            return _error(400, "Token name is required")
        try:
            minutes = int(body.get("minutes", 0))
        except (TypeError, ValueError):
            return _error(400, "minutes must be an integer")
        if minutes <= 0:
            return _error(400, "minutes must be positive")

        token = GamingToken.objects.create(
            name=name,
            minutes=minutes,
            remaining_minutes=minutes,
            price=body.get("price", 0),
        )
        return _json(_ser_model(token), status=201)

    tokens = GamingToken.objects.all().order_by("-sold_at")
    return _json({"tokens": [_ser_model(t) for t in tokens]})


def gaming_sessions(request: HttpRequest) -> JsonResponse:
    """GET /gaming/sessions — list sessions (optionally filtered by status)."""
    status_filter = request.GET.get("status", "").strip()
    qs = GamingSession.objects.select_related("station", "token").order_by("-started_at")
    if status_filter:
        qs = qs.filter(status=status_filter)
    return _json({"sessions": [_ser_gaming_session(s) for s in qs[:200]]})


def gaming_session_start(request: HttpRequest) -> JsonResponse:
    """POST /gaming/sessions/start — begin a session on a station.

    Body: ``{"station_id": 1, "token_id": 5, "customer_id": 9}``
    (``token_id`` / ``customer_id`` optional).
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    station_id = body.get("station_id")
    if not station_id:
        return _error(400, "station_id is required")
    try:
        session = start_session(
            station_id=int(station_id),
            token_id=body.get("token_id") or None,
            customer_id=body.get("customer_id") or None,
        )
    except GamingError as exc:
        return _error(400, str(exc))
    return _json({"session": _ser_gaming_session(session)}, status=201)


def gaming_session_pause(request: HttpRequest) -> JsonResponse:
    """POST /gaming/sessions/pause — body: ``{"session_id": 1}``."""
    return _gaming_session_action(request, pause_session, "session_id")


def gaming_session_resume(request: HttpRequest) -> JsonResponse:
    """POST /gaming/sessions/resume — body: ``{"session_id": 1}``."""
    return _gaming_session_action(request, resume_session, "session_id")


def gaming_session_stop(request: HttpRequest) -> JsonResponse:
    """POST /gaming/sessions/stop — body: ``{"session_id": 1, "cancelled": false}``."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    session_id = body.get("session_id")
    if not session_id:
        return _error(400, "session_id is required")
    try:
        session = stop_session(int(session_id), cancelled=bool(body.get("cancelled")))
    except GamingError as exc:
        return _error(400, str(exc))
    return _json({"session": _ser_gaming_session(session)})


def _gaming_session_action(request: HttpRequest, fn, key: str) -> JsonResponse:
    """Shared handler for pause/resume (id-keyed session mutations)."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    session_id = body.get(key)
    if not session_id:
        return _error(400, f"{key} is required")
    try:
        session = fn(int(session_id))
    except GamingError as exc:
        return _error(400, str(exc))
    return _json({"session": _ser_gaming_session(session)})


def gaming_queue(request: HttpRequest) -> JsonResponse:
    """GET /gaming/queue — list waitlist. POST — enqueue a customer."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")

        customer_name = body.get("customer_name") or ""
        try:
            entry = enqueue(
                customer_name,
                requested_minutes=int(body.get("requested_minutes", 60)),
            )
        except GamingError as exc:
            return _error(400, str(exc))
        except (TypeError, ValueError):
            return _error(400, "requested_minutes must be an integer")
        return _json({"entry": _ser_queue_entry(entry)}, status=201)

    entries = GamingQueueEntry.objects.order_by("created_at")
    return _json({"queue": [_ser_queue_entry(e) for e in entries]})


def gaming_queue_assign(request: HttpRequest) -> JsonResponse:
    """POST /gaming/queue/assign — assign the next entry (optionally to a station).

    Body: ``{"station_id": 2}`` (optional — defaults to the first free station).
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    station = None
    if body.get("station_id"):
        try:
            station = GamingStation.objects.get(id=int(body["station_id"]))
        except (GamingStation.DoesNotExist, TypeError, ValueError):
            return _error(404, f"Station {body.get('station_id')} not found")
    entry = assign_next(station)
    if entry is None:
        return _json({"assigned": None, "note": "No waiting entry or free station"})
    return _json({"assigned": _ser_queue_entry(entry)})


def gaming_queue_cancel(request: HttpRequest) -> JsonResponse:
    """POST /gaming/queue/cancel — body: ``{"entry_id": 1}``."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    entry_id = body.get("entry_id")
    if not entry_id:
        return _error(400, "entry_id is required")
    try:
        entry = cancel_queue_entry(int(entry_id))
    except GamingError as exc:
        return _error(400, str(exc))
    return _json({"entry": _ser_queue_entry(entry)})


# ═══════════════════════════════════════════════════════════════════════════
# Gift Cards P2 — issue / balance / redeem / reload / disable
# ═══════════════════════════════════════════════════════════════════════════

def gift_cards(request: HttpRequest) -> JsonResponse:
    """GET /gift-cards — list cards. POST — issue a new card."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")

        if not body.get("initial_balance"):
            return _error(400, "initial_balance is required")
        try:
            card = giftcard_issue(
                initial_balance=body["initial_balance"],
                currency=body.get("currency", "USD"),
                recipient_name=body.get("recipient_name", ""),
                recipient_email=body.get("recipient_email", ""),
                notes=body.get("notes", ""),
            )
        except GiftCardError as exc:
            return _error(400, str(exc))
        return _json(_ser_model(card), status=201)

    cards = GiftCard.objects.all().order_by("-issued_at")
    return _json({"gift_cards": [_ser_model(c) for c in cards]})


def gift_card_detail(request: HttpRequest, code: str) -> JsonResponse:
    """GET /gift-cards/<code> — card detail + balance."""
    card = giftcard_get(code)
    if card is None:
        return _error(404, f"Gift card '{code}' not found")
    return _json(_ser_model(card))


def gift_card_transactions(request: HttpRequest, code: str) -> JsonResponse:
    """GET /gift-cards/<code>/transactions — the card's ledger."""
    card = giftcard_get(code)
    if card is None:
        return _error(404, f"Gift card '{code}' not found")
    txs = GiftCardTransaction.objects.filter(gift_card=card).order_by("-created_at")
    return _json({"transactions": [_ser_model(t) for t in txs]})


def gift_card_redeem(request: HttpRequest) -> JsonResponse:
    """POST /gift-cards/redeem — body: ``{"code": "GC-…", "amount": 10, "sale_id": 9}``."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    code = body.get("code")
    if not code or not body.get("amount"):
        return _error(400, "code and amount are required")
    try:
        card = giftcard_redeem(code, body["amount"], sale_id=body.get("sale_id"))
    except GiftCardError as exc:
        return _error(400, str(exc))
    return _json(_ser_model(card))


def gift_card_reload(request: HttpRequest) -> JsonResponse:
    """POST /gift-cards/reload — body: ``{"code": "GC-…", "amount": 20}``."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    code = body.get("code")
    if not code or not body.get("amount"):
        return _error(400, "code and amount are required")
    try:
        card = giftcard_reload(code, body["amount"])
    except GiftCardError as exc:
        return _error(400, str(exc))
    return _json(_ser_model(card))


def gift_card_disable(request: HttpRequest) -> JsonResponse:
    """POST /gift-cards/disable — body: ``{"code": "GC-…"}``."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")

    code = body.get("code")
    if not code:
        return _error(400, "code is required")
    try:
        card = giftcard_disable(code)
    except GiftCardError as exc:
        return _error(400, str(exc))
    return _json(_ser_model(card))


# ═══════════════════════════════════════════════════════════════════════════
# Table Management P2 — floor layouts + order tracking + reservations
# ═══════════════════════════════════════════════════════════════════════════

def _ser_table(table: RestaurantTable) -> dict:
    data = _ser_model(table)
    if table.current_sale_id:
        data["current_sale_total"] = float(table.current_sale.total or 0)
    return data


def _ser_reservation(reservation: TableReservation) -> dict:
    data = _ser_model(reservation)
    data["display_name"] = reservation.display_name
    return data


def tables(request: HttpRequest) -> JsonResponse:
    """GET /tables — list the floor plan. POST — create a table."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")
        try:
            table = tables_svc.create_table(
                name=body.get("name", ""),
                section=body.get("section", "main"),
                capacity=int(body.get("capacity", 2)),
                shape=body.get("shape", "rect"),
                pos_x=int(body.get("pos_x", 0)),
                pos_y=int(body.get("pos_y", 0)),
                width=int(body.get("width", 1)),
                height=int(body.get("height", 1)),
                notes=body.get("notes", ""),
            )
        except tables_svc.TableError as exc:
            return _error(400, str(exc))
        return _json(_ser_table(table), status=201)

    tables = RestaurantTable.objects.all()
    return _json({"tables": [_ser_table(t) for t in tables]})


def table_detail(request: HttpRequest, pk: int) -> JsonResponse:
    """GET /tables/<pk> — a single table + its reservations."""
    table = tables_svc.get_table(pk)
    if table is None:
        return _error(404, f"Table #{pk} not found")
    data = _ser_table(table)
    data["reservations"] = [
        _ser_reservation(r) for r in table.reservations.all()[:10]
    ]
    return _json(data)


def table_status(request: HttpRequest, pk: int) -> JsonResponse:
    """POST /tables/<pk>/status — body: ``{"status": "free|cleaning|closed"}``."""
    table = tables_svc.get_table(pk)
    if table is None:
        return _error(404, f"Table #{pk} not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    try:
        table = tables_svc.update_status(table, body.get("status", ""))
    except tables_svc.TableError as exc:
        return _error(400, str(exc))
    return _json(_ser_table(table))


def table_occupy(request: HttpRequest, pk: int) -> JsonResponse:
    """POST /tables/<pk>/occupy — body: ``{"sale_id": 42}``."""
    table = tables_svc.get_table(pk)
    if table is None:
        return _error(404, f"Table #{pk} not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    sale = Sale.objects.filter(pk=body.get("sale_id")).first()
    if sale is None:
        return _error(404, "sale not found")
    try:
        table = tables_svc.occupy_table(table, sale)
    except tables_svc.TableError as exc:
        return _error(400, str(exc))
    return _json(_ser_table(table))


def table_clear(request: HttpRequest, pk: int) -> JsonResponse:
    """POST /tables/<pk>/clear — body: ``{"close_sale": true}``."""
    table = tables_svc.get_table(pk)
    if table is None:
        return _error(404, f"Table #{pk} not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}
    try:
        table = tables_svc.clear_table(table, close_sale=bool(body.get("close_sale")))
    except tables_svc.TableError as exc:
        return _error(400, str(exc))
    return _json(_ser_table(table))


def tables_floor(request: HttpRequest) -> JsonResponse:
    """GET /tables/floor — occupancy summary across the floor plan."""
    return _json(tables_svc.floor_summary())


def reservations(request: HttpRequest) -> JsonResponse:
    """GET /reservations — list bookings (filter ?status=). POST — create one."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")

        table = tables_svc.get_table(body.get("table_id"))
        if table is None:
            return _error(404, "table not found")
        try:
            from django.utils.dateparse import parse_datetime
            reservation_time = body.get("reservation_time")
            parsed = parse_datetime(reservation_time) if reservation_time else None
            if parsed is None and reservation_time:
                return _error(400, "reservation_time must be ISO 8601")
            reservation = tables_svc.create_reservation(
                table=table,
                reservation_time=parsed or dj_timezone.now(),
                party_size=int(body.get("party_size", 1)),
                customer=Customer.objects.filter(
                    pk=body.get("customer_id")
                ).first() if body.get("customer_id") else None,
                customer_name=body.get("customer_name", ""),
                notes=body.get("notes", ""),
            )
        except tables_svc.TableError as exc:
            return _error(400, str(exc))
        except (TypeError, ValueError) as exc:
            return _error(400, f"invalid party_size: {exc}")
        return _json(_ser_reservation(reservation), status=201)

    qs = TableReservation.objects.all()
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    return _json({"reservations": [_ser_reservation(r) for r in qs]})


def reservation_action(request: HttpRequest, pk: int, action: str) -> JsonResponse:
    """POST /reservations/<pk>/<action> — cancel | seat | complete | no-show."""
    reservation = tables_svc.get_reservation(pk)
    if reservation is None:
        return _error(404, f"Reservation #{pk} not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    try:
        if action == "cancel":
            reservation = tables_svc.cancel_reservation(reservation)
        elif action == "seat":
            sale = None
            if body.get("sale_id"):
                sale = Sale.objects.filter(pk=body["sale_id"]).first()
                if sale is None:
                    return _error(404, "sale not found")
            reservation = tables_svc.seat_reservation(reservation, sale=sale)
        elif action == "complete":
            reservation = tables_svc.complete_reservation(reservation)
        elif action == "no-show":
            reservation = tables_svc.no_show_reservation(reservation)
        else:
            return _error(404, f"unknown action '{action}'")
    except tables_svc.TableError as exc:
        return _error(400, str(exc))
    return _json(_ser_reservation(reservation))


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


# ═══════════════════════════════════════════════════════════════════════════
# Delivery Integration P2 — providers + delivery orders + webhooks
# ═══════════════════════════════════════════════════════════════════════════

def delivery_providers(request: HttpRequest) -> JsonResponse:
    """GET /deliveries/providers — list connectors. POST — register one."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")
        try:
            provider = delivery_svc.create_provider(
                name=body.get("name", ""),
                provider_type=body.get("provider_type", "manual"),
                base_url=body.get("base_url", ""),
                api_key=body.get("api_key", ""),
                commission_rate=body.get("commission_rate", 0),
                is_active=bool(body.get("is_active", True)),
            )
        except delivery_svc.DeliveryError as exc:
            return _error(400, str(exc))
        return _json(_ser_model(provider), status=201)
    return _json({"providers": [_ser_model(p) for p in delivery_svc.list_providers()]})


def deliveries(request: HttpRequest) -> JsonResponse:
    """GET /deliveries — list orders (filter ?status=). POST — dispatch one."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")

        sale = None
        if body.get("sale_id"):
            sale = Sale.objects.filter(pk=body["sale_id"]).first()
            if sale is None:
                return _error(404, "sale not found")
        provider = None
        if body.get("provider_id"):
            provider = delivery_svc.get_provider(body["provider_id"])
            if provider is None:
                return _error(404, "provider not found")
        zone = None
        if body.get("delivery_zone_id"):
            zone = DeliveryZone.objects.filter(pk=body["delivery_zone_id"]).first()
            if zone is None:
                return _error(404, "delivery zone not found")
        delivery_type = None
        if body.get("delivery_type_id"):
            delivery_type = DeliveryType.objects.filter(pk=body["delivery_type_id"]).first()

        try:
            order = delivery_svc.create_delivery_order(
                sale=sale,
                provider=provider,
                customer_name=body.get("customer_name", ""),
                customer_phone=body.get("customer_phone", ""),
                delivery_address=body.get("delivery_address", ""),
                distance_km=body.get("distance_km", 0),
                delivery_zone=zone,
                delivery_type=delivery_type,
                subtotal=body.get("subtotal"),
                total=body.get("total"),
                notes=body.get("notes", ""),
            )
        except delivery_svc.DeliveryError as exc:
            return _error(400, str(exc))
        return _json(_ser_model(order), status=201)

    qs = DeliveryOrder.objects.all()
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    return _json({"deliveries": [_ser_model(o) for o in qs]})


def delivery_detail(request: HttpRequest, pk: int) -> JsonResponse:
    """GET /deliveries/<pk> — a single delivery order."""
    order = delivery_svc.get_delivery_order(pk)
    if order is None:
        return _error(404, f"Delivery order #{pk} not found")
    return _json(_ser_model(order))


def delivery_status(request: HttpRequest, pk: int) -> JsonResponse:
    """POST /deliveries/<pk>/status — body: ``{"status": "accepted"}``."""
    order = delivery_svc.get_delivery_order(pk)
    if order is None:
        return _error(404, f"Delivery order #{pk} not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    try:
        order = delivery_svc.update_status(order, body.get("status", ""))
    except delivery_svc.DeliveryError as exc:
        return _error(400, str(exc))
    return _json(_ser_model(order))


def delivery_cancel(request: HttpRequest, pk: int) -> JsonResponse:
    """POST /deliveries/<pk>/cancel — cancel a delivery order."""
    order = delivery_svc.get_delivery_order(pk)
    if order is None:
        return _error(404, f"Delivery order #{pk} not found")
    try:
        order = delivery_svc.cancel_order(order)
    except delivery_svc.DeliveryError as exc:
        return _error(400, str(exc))
    return _json(_ser_model(order))


def delivery_stats(request: HttpRequest) -> JsonResponse:
    """GET /deliveries/stats — delivery KPIs."""
    return _json(delivery_svc.delivery_stats())


def delivery_webhook(request: HttpRequest, provider: str) -> JsonResponse:
    """POST /deliveries/webhook/<provider> — provider status callback.

    Body: ``{"order_id": "DLV-…", "status": "accepted"}``. The provider
    slug in the URL is informational; matching is on ``order_id``.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    order_id = body.get("order_id")
    if not order_id or not body.get("status"):
        return _error(400, "order_id and status are required")
    order = delivery_svc.ingest_provider_webhook(order_id, body["status"])
    if order is None:
        return _error(404, f"no delivery order with id '{order_id}'")
    return _json({"status": "ok", "order": _ser_model(order)})


# ═══════════════════════════════════════════════════════════════════════════
# AI Forecasting P2 — advisory demand / stock / waste / insights (read-only)
# ═══════════════════════════════════════════════════════════════════════════

def _qs_int(request: HttpRequest, key: str, default: int) -> int:
    try:
        return int(request.GET.get(key, default))
    except (ValueError, TypeError):
        return default


def forecast_demand(request: HttpRequest) -> JsonResponse:
    """GET /forecast/demand — per-product demand projection.

    Query params: ``days`` (horizon, default 14), ``lookback`` (default 28).
    """
    return _json(forecast_svc.demand_forecast(
        days=_qs_int(request, "days", 14),
        lookback=_qs_int(request, "lookback", 28),
    ))


def forecast_stock(request: HttpRequest) -> JsonResponse:
    """GET /forecast/stock — reorder recommendations.

    Query params: ``days`` (default 14), ``lead_time_days`` (default 3).
    """
    return _json(forecast_svc.stock_advisory(
        days=_qs_int(request, "days", 14),
        lead_time_days=_qs_int(request, "lead_time_days", 3),
    ))


def forecast_waste(request: HttpRequest) -> JsonResponse:
    """GET /forecast/waste — waste/disposal aggregation (``?days=30``)."""
    return _json(forecast_svc.waste_analysis(
        days=_qs_int(request, "days", 30),
    ))


def forecast_insights(request: HttpRequest) -> JsonResponse:
    """GET /forecast/insights — movers, growth, recommendations (``?days=30``)."""
    return _json(forecast_svc.sales_insights(
        days=_qs_int(request, "days", 30),
    ))


def forecast_report(request: HttpRequest) -> JsonResponse:
    """GET /forecast/report — combined advisory envelope (``?days=14``)."""
    return _json(forecast_svc.full_report(
        days=_qs_int(request, "days", 14),
    ))


def forecast_inventory(request: HttpRequest) -> JsonResponse:
    """GET /forecast/inventory — reorder-point / safety-stock / stock-out plan.

    Superset of ``/forecast/stock``. Query params: ``days`` (14),
    ``lead_time_days`` (3), ``safety_factor`` (0.5). Advisory/read-only.
    """
    return _json(forecast_svc.inventory_plan(
        days=_qs_int(request, "days", 14),
        lead_time_days=_qs_int(request, "lead_time_days", 3),
        safety_factor=float(request.GET.get("safety_factor", 0.5)),
    ))


def forecast_reorder_orders(request: HttpRequest) -> JsonResponse:
    """POST /forecast/inventory/reorder — create draft purchase orders.

    Operator action: materializes the advisory plan into ``PurchaseOrder``
    drafts (no stock movement until ordered/received). Body options:
    ``supplier_id``, ``days``, ``lead_time_days``, ``safety_factor``.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    try:
        result = forecast_svc.generate_reorder_orders(
            days=_qs_int(request, "days", 14) or int(body.get("days", 14)),
            lead_time_days=_qs_int(request, "lead_time_days", 3)
            or int(body.get("lead_time_days", 3)),
            safety_factor=float(request.GET.get("safety_factor", body.get("safety_factor", 0.5))),
            supplier_id=body.get("supplier_id") or None,
        )
    except ValueError as exc:
        return _error(400, str(exc))
    return _json(result, status=201)


# ═══════════════════════════════════════════════════════════════════════════
# Employee Scheduling P3 — shift planning + time clock
# ═══════════════════════════════════════════════════════════════════════════

def _get_employee(request, body) -> tuple | JsonResponse:
    emp_id = body.get("employee_id")
    if not emp_id:
        return None, _error(400, "employee_id is required")
    employee = Employee.objects.filter(pk=emp_id).first()
    if employee is None:
        return None, _error(404, "employee not found")
    return employee, None


def scheduling_shifts(request: HttpRequest) -> JsonResponse:
    """GET /scheduling/shifts — list shifts. POST — create/update one.

    POST body: ``{"employee_id", "day_of_week", "start_time": "09:00",
    "end_time": "17:00", "status"?, "notes"?}``.
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")
        employee, err = _get_employee(request, body)
        if err is not None:
            return err
        from django.utils.dateparse import parse_time
        start = parse_time(body.get("start_time", ""))
        end = parse_time(body.get("end_time", ""))
        try:
            shift = sched_svc.upsert_shift(
                employee=employee,
                day_of_week=body.get("day_of_week", ""),
                start_time=start,
                end_time=end,
                status=body.get("status", "scheduled"),
                notes=body.get("notes", ""),
            )
        except sched_svc.SchedulingError as exc:
            return _error(400, str(exc))
        return _json(_ser_model(shift), status=201)

    shifts = sched_svc.list_shifts(
        employee_id=request.GET.get("employee_id"),
        day_of_week=request.GET.get("day_of_week"),
    )
    return _json({"shifts": [_ser_model(s) for s in shifts]})


def scheduling_week(request: HttpRequest) -> JsonResponse:
    """GET /scheduling/week?week_start=YYYY-MM-DD — concrete week roster."""
    from django.utils.dateparse import parse_date
    week_start = parse_date(request.GET.get("week_start", "")) or dj_timezone.localdate()
    return _json(sched_svc.week_schedule(week_start))


def scheduling_coverage(request: HttpRequest) -> JsonResponse:
    """GET /scheduling/coverage?day_of_week=monday — staffing coverage."""
    try:
        return _json(sched_svc.coverage(request.GET.get("day_of_week")))
    except sched_svc.SchedulingError as exc:
        return _error(400, str(exc))


def scheduling_timeclock(request: HttpRequest) -> JsonResponse:
    """GET /scheduling/timeclock — recent punches + active staff.
    POST — clock in: body ``{"employee_id", "note"?}``.
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")
        employee, err = _get_employee(request, body)
        if err is not None:
            return err
        try:
            entry = sched_svc.clock_in(employee, note=body.get("note", ""))
        except sched_svc.SchedulingError as exc:
            return _error(400, str(exc))
        return _json(_ser_model(entry), status=201)

    return _json(sched_svc.timeclock_summary(
        days=_qs_int(request, "days", 7),
    ))


def scheduling_timeclock_action(request: HttpRequest, action: str) -> JsonResponse:
    """POST /scheduling/timeclock/<action> — out | break.

    Body: ``{"employee_id"}``. ``break`` toggles start/end on the active
    punch; ``out`` closes it.
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    employee, err = _get_employee(request, body)
    if err is not None:
        return err
    try:
        if action == "out":
            entry = sched_svc.clock_out(employee)
        elif action == "break":
            entry = sched_svc.toggle_break(employee)
        else:
            return _error(404, f"unknown action '{action}'")
    except sched_svc.SchedulingError as exc:
        return _error(400, str(exc))
    return _json(_ser_model(entry))


def scheduling_hours(request: HttpRequest) -> JsonResponse:
    """GET /scheduling/hours?employee_id=&start=YYYY-MM-DD&end=YYYY-MM-DD
    — worked hours, overtime, and pay estimate.
    """
    emp_id = request.GET.get("employee_id")
    if not emp_id:
        return _error(400, "employee_id is required")
    employee = Employee.objects.filter(pk=emp_id).first()
    if employee is None:
        return _error(404, "employee not found")
    from django.utils.dateparse import parse_date
    start = parse_date(request.GET.get("start", ""))
    end = parse_date(request.GET.get("end", ""))
    if start is None or end is None:
        return _error(400, "start and end dates are required (YYYY-MM-DD)")
    if start > end:
        return _error(400, "start must be before end")
    return _json(sched_svc.worked_hours(employee, start, end))


# ═══════════════════════════════════════════════════════════════════════════
# Customer Display (P3) — read-only order-confirmation screen
# ═══════════════════════════════════════════════════════════════════════════

def customer_display_order(request: HttpRequest, sale_id: int) -> JsonResponse:
    """GET /customer-display/<sale_id>
    — display envelope for one order (order confirmation screen).
    """
    display = cd_svc.order_display(sale_id)
    if display is None:
        return _error(404, "Sale not found")
    return _json(display)


def customer_display_board(request: HttpRequest) -> JsonResponse:
    """GET /customer-display/board
    — active orders feed for a wall/cycle display.
    """
    limit = request.GET.get("limit", 20)
    try:
        limit = max(1, min(int(limit), 50))
    except (TypeError, ValueError):
        limit = 20
    return _json(cd_svc.active_board(limit=limit))


# ═══════════════════════════════════════════════════════════════════════════
# Self-checkout Kiosk (P3) — self-service kiosk mode
# ═══════════════════════════════════════════════════════════════════════════

def _kiosk_session(session_key: str) -> KioskSession | None:
    return kiosk_svc.get_session(session_key)


def kiosk_catalog(request: HttpRequest) -> JsonResponse:
    """GET /kiosk/catalog?category=<slug>
    — active products grouped by category for the touchscreen.
    """
    return _json(kiosk_svc.catalog(category_slug=request.GET.get("category", "")))


def kiosk_sessions(request: HttpRequest) -> JsonResponse:
    """GET/POST /kiosk/sessions — list sessions / start a new one."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")
        session = kiosk_svc.start_session(
            session_key=body.get("session_key", ""),
            name=body.get("name", ""),
        )
        return _json({
            "session_key": session.session_key,
            "name": session.name,
            "status": session.status,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }, status=201)
    qs = KioskSession.objects.order_by("-created_at")[:50]
    return _json([{
        "session_key": s.session_key,
        "name": s.name,
        "status": s.status,
        "sale_id": s.sale_id,
        "payment_method": s.payment_method,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "closed_at": s.closed_at.isoformat() if s.closed_at else None,
        "item_count": sum(
            i.quantity for i in s.cart_items.all()
        ) if s.status == "open" else 0,
    } for s in qs])


def kiosk_session_detail(request: HttpRequest, session_key: str) -> JsonResponse:
    """GET /kiosk/sessions/<session_key> — session + cart summary."""
    session = _kiosk_session(session_key)
    if session is None:
        return _error(404, "Session not found")
    summary = kiosk_svc.cart_summary(session)
    summary["name"] = session.name
    summary["status"] = session.status
    summary["sale_id"] = session.sale_id
    summary["payment_method"] = session.payment_method
    return _json(summary)


def kiosk_cart(request: HttpRequest, session_key: str) -> JsonResponse:
    """POST /kiosk/sessions/<session_key>/cart — add a product."""
    session = _kiosk_session(session_key)
    if session is None:
        return _error(404, "Session not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    try:
        product_id = int(body.get("product_id", 0))
    except (TypeError, ValueError):
        return _error(400, "product_id is required")
    try:
        quantity = int(body.get("quantity", 1))
    except (TypeError, ValueError):
        return _error(400, "quantity must be an integer")
    try:
        item = kiosk_svc.add_item(session, product_id, quantity)
    except kiosk_svc.KioskError as exc:
        return _error(400, str(exc))
    return _json({
        "product_id": item.product_id,
        "product_name": item.product_name,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price),
        "line_total": round(float(item.unit_price) * item.quantity, 2),
        "cart": kiosk_svc.cart_summary(session),
    }, status=201)


def kiosk_cart_line(request: HttpRequest, session_key: str, product_id: int) -> JsonResponse:
    """PATCH/DELETE /kiosk/sessions/<session_key>/cart/<product_id>
    — set quantity (0 removes) / remove the line.
    """
    session = _kiosk_session(session_key)
    if session is None:
        return _error(404, "Session not found")
    if request.method == "DELETE":
        kiosk_svc.remove_item(session, product_id)
        return _json({"removed": product_id, "cart": kiosk_svc.cart_summary(session)})
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return _error(400, "Invalid JSON")
    try:
        quantity = int(body.get("quantity", 0))
    except (TypeError, ValueError):
        return _error(400, "quantity must be an integer")
    try:
        item = kiosk_svc.set_quantity(session, product_id, quantity)
    except kiosk_svc.KioskError as exc:
        return _error(400, str(exc))
    return _json({
        "product_id": item.product_id,
        "quantity": item.quantity,
        "cart": kiosk_svc.cart_summary(session),
    })


def kiosk_cart_clear(request: HttpRequest, session_key: str) -> JsonResponse:
    """POST /kiosk/sessions/<session_key>/cart/clear — empty the cart."""
    session = _kiosk_session(session_key)
    if session is None:
        return _error(404, "Session not found")
    kiosk_svc.clear_cart(session)
    return _json({"cleared": True, "cart": kiosk_svc.cart_summary(session)})


def kiosk_checkout(request: HttpRequest, session_key: str) -> JsonResponse:
    """POST /kiosk/sessions/<session_key>/checkout — check the cart out."""
    session = _kiosk_session(session_key)
    if session is None:
        return _error(404, "Session not found")
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}
    try:
        result = kiosk_svc.checkout(
            session, payment_method=body.get("payment_method", "card")
        )
    except kiosk_svc.KioskError as exc:
        return _error(400, str(exc))
    return _json(result, status=201)


def kiosk_session_cancel(request: HttpRequest, session_key: str) -> JsonResponse:
    """POST /kiosk/sessions/<session_key>/cancel — abandon the session."""
    session = _kiosk_session(session_key)
    if session is None:
        return _error(404, "Session not found")
    try:
        kiosk_svc.cancel_session(session)
    except kiosk_svc.KioskError as exc:
        return _error(400, str(exc))
    return _json({"session_key": session_key, "status": "cancelled"})


def kiosk_stats(request: HttpRequest) -> JsonResponse:
    """GET /kiosk/stats — session/checkout stats."""
    return _json(kiosk_svc.kiosk_stats())


# ═══════════════════════════════════════════════════════════════════════════
# Purchase Order workflow (Reorder Workflow follow-up)
# ═══════════════════════════════════════════════════════════════════════════

def purchase_orders(request: HttpRequest) -> JsonResponse:
    """GET/POST /purchase-orders — list (filter ?status=) / create a draft."""
    if request.method == "POST":
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return _error(400, "Invalid JSON")
        try:
            po = po_svc.create_purchase_order(
                supplier_id=body.get("supplier_id"),
                items=body.get("items") or [],
                expected_date=body.get("expected_date"),
                notes=body.get("notes", ""),
            )
        except po_svc.PurchaseOrderError as exc:
            return _error(400, str(exc))
        return _json(po_svc.purchase_order_detail(po.id), status=201)
    return _json(po_svc.list_purchase_orders(status=request.GET.get("status", "")))


def purchase_order_detail(request: HttpRequest, pk: int) -> JsonResponse:
    """GET /purchase-orders/<pk> — PO detail with line items."""
    detail = po_svc.purchase_order_detail(pk)
    if detail is None:
        return _error(404, "Purchase order not found")
    return _json(detail)


def purchase_order_action(request: HttpRequest, pk: int, action: str) -> JsonResponse:
    """POST /purchase-orders/<pk>/<action> — order · receive · cancel."""
    try:
        if action == "order":
            po = po_svc.mark_ordered(pk)
            return _json(po_svc.purchase_order_detail(po.id))
        if action == "receive":
            try:
                body = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                body = {}
            quantities = body.get("quantities") if isinstance(body.get("quantities"), dict) else None
            return _json(po_svc.receive_purchase_order(pk, quantities=quantities))
        if action == "cancel":
            po = po_svc.cancel_purchase_order(pk)
            return _json(po_svc.purchase_order_detail(po.id))
        return _error(404, f"unknown action '{action}'")
    except po_svc.PurchaseOrderError as exc:
        return _error(400, str(exc))


def purchase_order_alerts(request: HttpRequest) -> JsonResponse:
    """GET /purchase-orders/alerts — reorder alerts + open drafts."""
    lead = _qs_int(request, "lead_time_days", 3)
    try:
        safety = float(request.GET.get("safety_factor", 0.5))
    except (TypeError, ValueError):
        safety = 0.5
    return _json(po_svc.reorder_alerts(lead_time_days=lead, safety_factor=safety))


def purchase_order_stats(request: HttpRequest) -> JsonResponse:
    """GET /purchase-orders/stats — counts by status + outstanding value."""
    return _json(po_svc.purchase_order_stats())
