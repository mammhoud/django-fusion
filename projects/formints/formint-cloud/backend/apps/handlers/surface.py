"""POS Cloud — Django-native surface mirroring the removed Robyn sidecar.

The Astro frontend's dev proxy sends these root paths to ``:8767``
(``/organizations``, ``/branches``, ``/leads``, ``/contacts``, ``/deals``,
``/inventory-reports``, ``/branch-reports``, ``/device-tokens``,
``/conflicts``, ``/queue``, ``/fusion``, ``/api``, ``/stats``,
``/health``).  Previously the Robyn sidecar served them from the shared
Django ORM; now Django serves them directly so the frontend URL contract
is unchanged and the sidecar can be removed.

This module provides:

* Generic JSON CRUD at the root paths (``GET/POST /{collection}/`` and
  ``GET/PATCH/DELETE /{collection}/{pk}/``) — same ``{count, items}``
  shape the Robyn sidecar returned, now gated by an authenticated
  session (anonymous callers get a JSON ``401``, not a redirect).
* ``bridge_sales`` / ``bridge_products`` / ``bridge_settings`` — the
  Community-UI data bridges (wired at ``/api/*`` in ``apps/core/urls.py``).
* ``stats`` — the sidecar's ``/stats`` counts payload.

Sensitive ``DeviceToken`` fields (``token_hash``, ``token_prefix``,
``capabilities``, ``allowed_entities``) are excluded from both
serialization and writes; ``role`` / ``is_active`` writes are restricted
to staff.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from django.db import models
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.core.models import (
    BackupRun, Branch, BranchInventory, BranchProduct, BranchReport,
    BranchSale, BranchSyncLog, Contact, Deal, DeviceToken,
    InventoryReport, Lead, Organization, SyncConflict, SyncQueueItem,
)

# Fields never serialized or writable through the generic surface.
_SENSITIVE_FIELDS = {
    "token_hash",
    "token_prefix",
    "capabilities",
    "allowed_entities",
}
# Fields only staff may write (role escalation / token lifecycle).
_STAFF_ONLY_FIELDS = {"role", "is_active"}


def _is_staff(request: HttpRequest) -> bool:
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated and user.is_staff)


# ── JSON-safe serialization ────────────────────────────────────────────────

def _json_ready(value: Any) -> Any:
    """Convert model field values to JSON-serialisable primitives."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, models.Model):
        return value.pk
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    return str(value)


def _serialize(instance: models.Model) -> dict[str, Any]:
    """Serialize a model instance to a flat JSON dict (sidecar style).

    Sensitive fields are omitted.
    """
    data: dict[str, Any] = {}
    for field in instance._meta.concrete_fields:
        if field.name in _SENSITIVE_FIELDS:
            continue
        if isinstance(field, models.ForeignKey):
            fk = getattr(instance, field.name, None)
            data[field.name + "_id"] = fk.pk if fk is not None else None
            data[field.name] = str(fk) if fk is not None else None
        else:
            data[field.name] = _json_ready(getattr(instance, field.name))
    return data


# ── Generic JSON CRUD (sidecar /{collection} contract, auth-gated) ────────

def _writable_fields(
    model: type[models.Model],
    *,
    is_staff: bool,
) -> dict[str, models.Field]:
    """Fields a client may set on create/update.

    Excludes pk, auto fields, sensitive fields, and (for non-staff) the
    staff-only token lifecycle fields.
    """
    fields: dict[str, models.Field] = {}
    for field in model._meta.concrete_fields:
        if field.name in ("id", "created_at", "updated_at"):
            continue
        if isinstance(field, models.AutoField):
            continue
        if field.name in _SENSITIVE_FIELDS:
            continue
        if not is_staff and field.name in _STAFF_ONLY_FIELDS:
            continue
        auto_now = getattr(field, "auto_now", False)
        auto_now_add = getattr(field, "auto_now_add", False)
        if auto_now or auto_now_add:
            continue
        fields[field.name] = field
    return fields


def _clean_body(
    model: type[models.Model],
    body: dict[str, Any],
    *,
    is_staff: bool,
) -> dict[str, Any]:
    """Keep only writable keys; accept both ``field`` and ``field_id`` for FKs."""
    cleaned: dict[str, Any] = {}
    fields = _writable_fields(model, is_staff=is_staff)
    for key, value in body.items():
        field = fields.get(key)
        if field is None and key.endswith("_id"):
            fk_name = key[:-3]
            field = fields.get(fk_name)
        if field is None:
            continue
        if isinstance(field, models.ForeignKey):
            target = field.remote_field.model
            cleaned[field.name] = target.objects.get(pk=value)
        else:
            cleaned[field.name] = value
    return cleaned


def _make_crud(
    model: type[models.Model],
) -> Callable[[HttpRequest, Any], JsonResponse]:
    """Build a JSON CRUD view for *model* mounted at ``/{prefix}/``."""

    @require_http_methods(["GET", "POST"])
    def collection(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return JsonResponse({"error": "authentication required"}, status=401)
        is_staff = bool(user.is_staff)
        if request.method == "POST":
            try:
                body = json.loads(request.body or b"{}")
            except json.JSONDecodeError:
                return JsonResponse({"error": "invalid json"}, status=400)
            try:
                instance = model.objects.create(
                    **_clean_body(model, body, is_staff=is_staff)
                )
                return JsonResponse(_serialize(instance), status=201)
            except Exception as exc:  # noqa: BLE001 — surface errors verbatim
                return JsonResponse({"error": str(exc)}, status=400)
        qs = model.objects.all()
        fk_names = {
            f.name for f in model._meta.concrete_fields
            if isinstance(f, models.ForeignKey)
        }
        for rel in ("branch", "organization", "contact"):
            if rel in fk_names:
                qs = qs.select_related(rel)
        items = [_serialize(o) for o in qs]
        return JsonResponse({"count": len(items), "items": items})

    @require_http_methods(["GET", "PATCH", "DELETE"])
    def detail(request: HttpRequest, pk: str, *args: Any, **kwargs: Any) -> JsonResponse:
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return JsonResponse({"error": "authentication required"}, status=401)
        is_staff = bool(user.is_staff)
        try:
            instance = model.objects.get(pk=pk)
        except (model.DoesNotExist, ValueError, TypeError):
            return JsonResponse({"error": "not found"}, status=404)
        if request.method == "GET":
            return JsonResponse(_serialize(instance))
        if request.method == "DELETE":
            instance.delete()
            return JsonResponse({"status": "deleted"})
        try:
            body = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid json"}, status=400)
        try:
            for key, value in _clean_body(model, body, is_staff=is_staff).items():
                setattr(instance, key, value)
            instance.save()
            return JsonResponse(_serialize(instance))
        except Exception as exc:  # noqa: BLE001
            return JsonResponse({"error": str(exc)}, status=400)

    @csrf_exempt
    def dispatch(request: HttpRequest, pk: str | None = None, **kw: Any) -> JsonResponse:
        return detail(request, pk) if pk is not None else collection(request)

    return dispatch


# ── Community-UI bridges (sidecar /api/sales|products|settings contract) ────
# Wired at /api/sales etc. in apps/core/urls.py.

def _ser_sale(s: BranchSale) -> dict[str, Any]:
    return {
        "id": s.id,
        "branch": s.branch.code if s.branch else None,
        "branch_id": s.branch_id,
        "total_amount": float(s.total_amount) if s.total_amount else 0.0,
        "payment_method": s.payment_method,
        "status": s.status,
        "sale_date": s.sale_date.isoformat() if s.sale_date else None,
        "items": [],
    }


def _ser_product(p: BranchProduct) -> dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "price": float(p.price) if p.price else 0.0,
        "stock_quantity": p.stock_quantity,
        "branch": p.branch.code if p.branch else None,
        "branch_id": p.branch_id,
    }


def bridge_sales(request: HttpRequest) -> JsonResponse:
    """GET /api/sales — Community-UI sale list bridge."""
    sales = [_ser_sale(s) for s in BranchSale.objects.all().select_related("branch")]
    return JsonResponse(sales, safe=False)


def bridge_products(request: HttpRequest) -> JsonResponse:
    """GET /api/products — Community-UI product list bridge."""
    products = [
        _ser_product(p) for p in BranchProduct.objects.all().select_related("branch")
    ]
    return JsonResponse(products, safe=False)


def bridge_settings(request: HttpRequest) -> JsonResponse:
    """GET /api/settings — Community-UI settings bridge."""
    return JsonResponse({
        "restaurant_name": "POS Cloud",
        "organizations": Organization.objects.count(),
        "branches": Branch.objects.count(),
        "sync": True,
    })


# ── /stats ─────────────────────────────────────────────────────────────────

def _models():
    return [
        Organization, Branch, Lead, Contact, Deal,
        InventoryReport, BranchReport,
        BranchSyncLog, BranchProduct, BranchSale, BranchInventory,
        DeviceToken, SyncConflict, SyncQueueItem,
    ]


def stats(request: HttpRequest) -> JsonResponse:
    """GET /stats — counts for every core model (sidecar contract)."""
    models_ = _models()
    counts = {m.__name__: m.objects.count() for m in models_}
    return JsonResponse({
        "counts": counts,
        "models": [m.__name__ for m in models_],
    })


def monitor_status(request: HttpRequest) -> JsonResponse:
    """GET /monitor/status — health summary for the cloud master.

    Returns database reachability, most recent backup status, and
    pending sync-queue depth so operators get one glanceable answer
    to "is the master alive and backed up?".
    """
    # ── Database reachability ──────────────────────────────────
    database = "ok"
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001 — surface the error text
        database = "error"

    # ── Last backup ────────────────────────────────────────────
    latest = BackupRun.objects.order_by("-started_at").first()
    last_backup = None
    if latest is not None:
        last_backup = {
            "filename": latest.filename,
            "status": latest.status,
            "size_bytes": latest.size_bytes,
            "started_at": latest.started_at.isoformat(),
        }

    # ── Sync queue depth ───────────────────────────────────────
    sync_queue_depth = SyncQueueItem.objects.count()

    return JsonResponse({
        "database": database,
        "last_backup": last_backup,
        "sync_queue_depth": sync_queue_depth,
    })


def fusion_monitor(request: HttpRequest) -> HttpResponse:
    """GET /fusion/monitor — render the django-fusion monitor tile fragment.

    Renders the ``core.monitor.tile`` fragment component (latest backup +
    sync queue depth) so the Astro frontend can embed it via the fusion
    render-mode contract.  Mirrors the ``/fusion/*`` sidecar surface:
    returns rendered fragment HTML, not JSON.
    """
    from apps.handlers.fragments.monitor import MonitorTileView

    view = MonitorTileView()
    view.setup(request)
    context = view.get_fragment_context()
    return view.render_fragment_response(context)


# ── Routes ─────────────────────────────────────────────────────────────────

def _crud(model: type[models.Model], prefix: str) -> list:
    """URLs for a generic JSON CRUD collection at ``/{prefix}/``."""
    view = _make_crud(model)
    return [
        path(f"{prefix}/", view, name=f"{prefix}_list"),
        path(f"{prefix}/<pk>/", view, name=f"{prefix}_detail"),
    ]


urlpatterns = [
    *(_crud(Organization, "organizations")),
    *(_crud(Branch, "branches")),
    *(_crud(Lead, "leads")),
    *(_crud(Contact, "contacts")),
    *(_crud(Deal, "deals")),
    *(_crud(InventoryReport, "inventory-reports")),
    *(_crud(BranchReport, "branch-reports")),
    *(_crud(BranchSyncLog, "sync/logs")),
    *(_crud(BranchProduct, "sync/products")),
    *(_crud(BranchSale, "sync/sales")),
    *(_crud(BranchInventory, "sync/inventory")),
    *(_crud(DeviceToken, "device-tokens")),
    *(_crud(SyncConflict, "conflicts")),
    *(_crud(SyncQueueItem, "queue")),
]
