"""
Admin Dashboard Routes — POS Full Edition.

Server-side rendered admin dashboard using Jinja2 templates.
Authentication reuses the existing Employee model (admin/manager roles).
All data queries go through Django ORM via sync_to_async.

Pages:
  GET  /admin                    → Login page (or redirect if logged in)
  POST /admin/login               → Authenticate employee (form-encoded)
  GET  /admin/logout              → Clear session
  GET  /admin/dashboard           → Stats, cloud status, recent nodes, sync activity
  GET  /admin/settings            → Cloud sync config, scheduler, database info
  POST /admin/settings/cloud-save → Save cloud config (form-encoded)
  POST /admin/settings/toggle-sync → Enable/disable scheduler
  GET  /admin/devices             → Node list, master devices, device configs
  POST /admin/devices/:id/promote → Promote node to master
  POST /admin/devices/:id/toggle-active → Activate/deactivate node
  GET  /admin/products            → Product list
  GET  /admin/products/add        → Add product form
  GET  /admin/products/:id/edit   → Edit product form
  POST /admin/products/save       → Save product (form-encoded)
  GET  /admin/users               → Employee list
  GET  /admin/users/add           → Add user form
  GET  /admin/users/:id/edit      → Edit user form
  POST /admin/users/save          → Save user (form-encoded)
  GET  /admin/sync-logs           → Sync log viewer with filter
  POST /admin/sync-logs/clear     → Clear all sync logs
"""

from __future__ import annotations

import json
import logging
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from jinja2 import Environment, FileSystemLoader
from robyn import Request, Response

logger = logging.getLogger("pos_full.admin")

# ---------------------------------------------------------------------------
# Template engine
# ---------------------------------------------------------------------------

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)


def _render(template: str, context: dict = None) -> str:
    return _env.get_template(template).render(context or {})


def _html(content: str, status: int = 200) -> Response:
    return Response(status_code=status, headers={"Content-Type": "text/html; charset=utf-8"}, description=content)


def _redirect(location: str) -> Response:
    return Response(status_code=302, headers={"Location": location}, description="")


def _parse_form(request: Request) -> dict:
    """Parse form-encoded or JSON body into a dict."""
    body_bytes = request.body if hasattr(request, 'body') else b""
    if body_bytes:
        try:
            data = json.loads(body_bytes)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        try:
            text = body_bytes.decode("utf-8", errors="replace")
            parsed = parse_qs(text)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except Exception:
            pass
    return {}


# ---------------------------------------------------------------------------
# Session store (in-memory — resets on restart, acceptable for local admin)
# ---------------------------------------------------------------------------

_sessions: Dict[str, Dict[str, Any]] = {}
SESSION_TIMEOUT = 3600


def _create_session(employee_data: dict) -> str:
    token = secrets.token_hex(32)
    _sessions[token] = {"employee": employee_data, "created_at": datetime.now(timezone.utc).timestamp()}
    now = datetime.now(timezone.utc).timestamp()
    expired = [k for k, v in _sessions.items() if now - v["created_at"] > SESSION_TIMEOUT]
    for k in expired:
        del _sessions[k]
    return token


def _get_session(request: Request) -> dict | None:
    cookie = request.headers.get("Cookie", "")
    token = ""
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("admin_token="):
            token = part.split("=", 1)[1]
    if not token or token not in _sessions:
        return None
    session = _sessions[token]
    if datetime.now(timezone.utc).timestamp() - session["created_at"] > SESSION_TIMEOUT:
        del _sessions[token]
        return None
    return session


def _require_admin(request: Request) -> dict | None:
    session = _get_session(request)
    if not session:
        return None
    role = session["employee"].get("role", "")
    if role not in ("admin", "manager"):
        return None
    return session


def _base_context(request: Request, page: str, title: str) -> dict:
    session = _get_session(request)
    return {
        "app_name": "POS Full Admin",
        "page": page,
        "page_title": title,
        "user_name": session["employee"]["name"] if session else "Guest",
        "user_role": session["employee"]["role"] if session else "",
        "version": _get_version(),
        "flash_message": "",
        "flash_type": "success",
    }


def _get_version() -> str:
    try:
        from __about__ import __version__
        return __version__
    except ImportError:
        return "unknown"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_sync_state() -> dict:
    try:
        from routes.state import _load_sync_state as _load
        return _load()
    except Exception:
        return {}


def _save_sync_state(state: dict) -> None:
    try:
        from routes.state import _save_sync_state as _save
        _save(state)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------


def register_admin_routes(app):
    """Register all admin dashboard routes."""

    # ── Login page ──

    @app.get("/admin")
    @app.get("/admin/login")
    async def admin_login(request: Request):
        if _require_admin(request):
            return _redirect("/admin/dashboard")
        return _html(_render("admin/login.html", {"app_name": "POS Full Admin", "error": ""}))

    @app.get("/admin/logout")
    async def admin_logout(request: Request):
        cookie = request.headers.get("Cookie", "")
        token = ""
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith("admin_token="):
                token = part.split("=", 1)[1]
        if token in _sessions:
            del _sessions[token]
        resp = _redirect("/admin")
        resp.headers["Set-Cookie"] = "admin_token=; Path=/; Max-Age=0; HttpOnly"
        return resp

    @app.post("/admin/login")
    async def admin_login_post(request: Request):
        body = _parse_form(request)
        pin = body.get("pin", "").strip()

        from routes import state as S

        @sync_to_async
        def _auth():
            if not pin:
                return None
            try:
                emp = S.Employee.objects.get(pin_code=pin, is_active=True)
            except S.Employee.DoesNotExist:
                return None
            if emp.role not in ("admin", "manager"):
                return None
            return {
                "id": emp.id,
                "name": f"{emp.first_name} {emp.last_name}".strip(),
                "role": emp.role,
                "email": emp.email or "",
            }

        emp_data = await _auth()
        if not emp_data:
            return _html(_render("admin/login.html", {
                "app_name": "POS Full Admin",
                "error": "Invalid PIN or insufficient permissions. Admin/Manager role required.",
            }))

        token = _create_session(emp_data)
        resp = _redirect("/admin/dashboard")
        resp.headers["Set-Cookie"] = f"admin_token={token}; Path=/; Max-Age={SESSION_TIMEOUT}; HttpOnly"
        return resp

    # ── Dashboard ──

    @app.get("/admin/dashboard")
    async def admin_dashboard(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")

        from routes import state as S

        @sync_to_async
        def _data():
            return {
                "products": S.Product.objects.filter(is_active=True).count(),
                "sales": S.Sale.objects.count(),
                "nodes_online": S.Node.objects.filter(status="online").count(),
            }

        @sync_to_async
        def _nodes():
            return [
                {"node_id": n.node_id, "node_type": n.node_type,
                 "status": n.status, "last_seen": n.last_seen.strftime("%Y-%m-%d %H:%M") if n.last_seen else "-"}
                for n in S.Node.objects.all().order_by("-last_seen")[:5]
            ]

        @sync_to_async
        def _sync_logs():
            return [
                {"node_id": log.node_id, "entity_type": log.entity_type,
                 "direction": log.direction, "status": log.status,
                 "created_at": log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "-"}
                for log in S.SyncLog.objects.all().order_by("-created_at")[:10]
            ]

        stats = await _data()
        nodes = await _nodes()
        sync_logs = await _sync_logs()

        cloud_data = _load_sync_state()
        cloud = {
            "url": cloud_data.get("cloud_url", os.environ.get("CLOUD_CRM_URL", "")),
            "status": cloud_data.get("status", "idle"),
            "last_sync": cloud_data.get("last_sync", None),
            "enabled": cloud_data.get("enabled", True),
        }

        ctx = _base_context(request, "dashboard", "Dashboard")
        ctx.update({"stats": stats, "nodes": nodes, "sync_logs": sync_logs, "cloud": cloud})
        return _html(_render("admin/dashboard.html", ctx))

    # ── Settings ──

    @app.get("/admin/settings")
    async def admin_settings(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")

        from routes import state as S
        cloud_data = _load_sync_state()
        sched = getattr(S, 'sync_scheduler', None)

        ctx = _base_context(request, "settings", "Settings")
        ctx.update({
            "cloud": {
                "url": cloud_data.get("cloud_url", os.environ.get("CLOUD_CRM_URL", "")),
                "api_key": cloud_data.get("api_key", "") or "",
                "sync_interval": cloud_data.get("sync_interval", 60),
                "enabled": cloud_data.get("enabled", True),
                "node_id": cloud_data.get("node_id", "pos-full-auto"),
            },
            "db_path": str(S.DB_PATH),
            "sync_state_path": str(S.SYNC_STATE_PATH),
            "scheduler": sched.stats if sched else {"running": False, "enabled": False, "interval_s": 0, "sync_count": 0, "error_count": 0, "node_id": "-", "last_sync_at": None},
            "version": _get_version(),
            "uptime": int((datetime.now(timezone.utc) - S._start_time).total_seconds()),
            "model_count": len(S._ALL_MODELS),
        })
        return _html(_render("admin/settings.html", ctx))

    @app.post("/admin/settings/cloud-save")
    async def admin_save_cloud(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        body = _parse_form(request)
        state = _load_sync_state()
        if "cloud_url" in body: state["cloud_url"] = body["cloud_url"]
        if "api_key" in body: state["api_key"] = body["api_key"]
        if "sync_interval" in body: state["sync_interval"] = int(body["sync_interval"])
        state["enabled"] = body.get("enabled") in (True, "1", 1, "true", "on")
        if "node_id" in body: state["node_id"] = body["node_id"]
        _save_sync_state(state)
        return _redirect("/admin/settings")

    @app.get("/admin/settings/test-cloud")
    async def admin_test_cloud(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        cloud_data = _load_sync_state()
        url = cloud_data.get("cloud_url", os.environ.get("CLOUD_CRM_URL", ""))
        if not url:
            return _redirect("/admin/settings")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{url.rstrip('/')}/health")
                if resp.status_code == 200:
                    cloud_data["status"] = "connected"
                else:
                    cloud_data["status"] = "error"
        except Exception:
            cloud_data["status"] = "disconnected"
        _save_sync_state(cloud_data)
        return _redirect("/admin/settings")

    @app.post("/admin/settings/toggle-sync")
    async def admin_toggle_sync(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        from routes import state as S
        sched = getattr(S, 'sync_scheduler', None)
        if sched:
            await sched.toggle(not sched._enabled)
        return _redirect("/admin/settings")

    # ── Devices ──

    @app.get("/admin/devices")
    async def admin_devices(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")

        from routes import state as S
        node_filter = request.query_params.get("node_filter", "")

        @sync_to_async
        def _nodes():
            return [
                {"node_id": n.node_id, "hostname": n.hostname, "node_type": n.node_type,
                 "status": n.status, "product_count": n.product_count, "is_active": n.is_active,
                 "last_seen": n.last_seen.strftime("%Y-%m-%d %H:%M") if n.last_seen else "-"}
                for n in S.Node.objects.all().order_by("-last_seen")
            ]

        @sync_to_async
        def _masters():
            return [
                {"name": m.name, "device_id": m.device_id, "device_type": m.device_type,
                 "status": m.status, "managed_node_ids": m.managed_node_ids or [],
                 "synced_at": m.synced_at.strftime("%Y-%m-%d %H:%M") if m.synced_at else "Never"}
                for m in S.MasterDevice.objects.filter(is_active=True)
            ]

        @sync_to_async
        def _configs():
            qs = S.DeviceConfig.objects.filter(is_active=True)
            if node_filter:
                qs = qs.filter(node_id__icontains=node_filter)
            return [
                {"node_id": dc.node_id, "config_key": dc.config_key,
                 "config_value": json.dumps(dc.config_value)[:80],
                 "category": dc.category, "version": dc.version}
                for dc in qs.order_by("node_id", "config_key")[:50]
            ]

        ctx = _base_context(request, "devices", "Devices")
        ctx["nodes"] = await _nodes()
        ctx["masters"] = await _masters()
        ctx["device_configs"] = await _configs()
        ctx["node_filter"] = node_filter
        return _html(_render("admin/devices.html", ctx))

    @app.post("/admin/devices/:node_id/promote")
    async def admin_promote_node(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        from routes import state as S
        node_id = request.path_params.get("node_id", "")

        @sync_to_async
        def _promote():
            try:
                node = S.Node.objects.get(node_id=node_id)
            except S.Node.DoesNotExist:
                return
            S.MasterDevice.objects.update_or_create(
                device_id=node_id,
                defaults={
                    "name": f"Master - {node.hostname or node_id}",
                    "node_id": node_id,
                    "device_type": "master_node",
                    "status": node.status,
                    "managed_node_ids": [],
                },
            )
        await _promote()
        return _redirect("/admin/devices")

    @app.post("/admin/devices/:node_id/toggle-active")
    async def admin_toggle_node(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        from routes import state as S
        node_id = request.path_params.get("node_id", "")

        @sync_to_async
        def _toggle():
            try:
                n = S.Node.objects.get(node_id=node_id)
                n.is_active = not n.is_active
                n.save(update_fields=["is_active", "updated_at"])
            except S.Node.DoesNotExist:
                pass
        await _toggle()
        return _redirect("/admin/devices")

    # ── Products ──

    @app.get("/admin/products")
    async def admin_products(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S

        @sync_to_async
        def _data():
            return [
                {"id": p.id, "name": str(p.name), "category": str(p.category.name) if p.category else "-",
                 "price": float(p.price), "stock": p.stock_quantity or 0, "active": p.is_active}
                for p in S.Product.objects.select_related("category").all().order_by("name")
            ]

        @sync_to_async
        def _cats():
            return [{"id": c.id, "name": c.name} for c in S.Category.objects.filter(is_active=True)]

        ctx = _base_context(request, "products", "Products")
        ctx["products"] = await _data()
        ctx["categories"] = await _cats()
        ctx["edit_product"] = None
        return _html(_render("admin/products.html", ctx))

    @app.get("/admin/products/add")
    async def admin_products_add(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S

        @sync_to_async
        def _data():
            return [
                {"id": p.id, "name": str(p.name), "category": str(p.category.name) if p.category else "-",
                 "price": float(p.price), "stock": p.stock_quantity or 0, "active": p.is_active}
                for p in S.Product.objects.select_related("category").all().order_by("name")
            ]

        @sync_to_async
        def _cats():
            return [{"id": c.id, "name": c.name} for c in S.Category.objects.filter(is_active=True)]

        ctx = _base_context(request, "products", "Products")
        ctx["products"] = await _data()
        ctx["categories"] = await _cats()
        ctx["edit_product"] = {"name": "", "sku": "", "price": "", "stock": 0, "description": "", "active": True, "category_id": None}
        return _html(_render("admin/products.html", ctx))

    @app.get("/admin/products/:product_id/edit")
    async def admin_products_edit(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S
        product_id = int(request.path_params.get("product_id", "0"))

        @sync_to_async
        def _data():
            return [
                {"id": p.id, "name": str(p.name), "category": str(p.category.name) if p.category else "-",
                 "price": float(p.price), "stock": p.stock_quantity or 0, "active": p.is_active}
                for p in S.Product.objects.select_related("category").all().order_by("name")
            ]

        @sync_to_async
        def _cats():
            return [{"id": c.id, "name": c.name} for c in S.Category.objects.filter(is_active=True)]

        @sync_to_async
        def _product():
            try:
                p = S.Product.objects.get(id=product_id)
                return {
                    "id": p.id, "name": p.name, "sku": p.sku or "",
                    "price": float(p.price), "stock": p.stock_quantity or 0,
                    "description": p.description or "", "active": p.is_active,
                    "category_id": p.category_id,
                }
            except S.Product.DoesNotExist:
                return None

        edit = await _product()
        if not edit:
            return _redirect("/admin/products")

        ctx = _base_context(request, "products", "Products")
        ctx["products"] = await _data()
        ctx["categories"] = await _cats()
        ctx["edit_product"] = edit
        return _html(_render("admin/products.html", ctx))

    @app.post("/admin/products/save")
    async def admin_save_product(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        from routes import state as S
        body = _parse_form(request)
        product_id = body.get("id")

        @sync_to_async
        def _save():
            defaults = {
                "name": body.get("name", ""),
                "sku": body.get("sku", None),
                "price": float(body.get("price", 0)),
                "stock_quantity": int(body.get("stock_quantity", 0)),
                "description": body.get("description", ""),
                "is_active": body.get("is_active") in (True, "1", 1, "true", "on"),
            }
            cat_id = body.get("category_id")
            if cat_id:
                try:
                    defaults["category"] = S.Category.objects.get(id=int(cat_id))
                except (S.Category.DoesNotExist, ValueError):
                    pass
            if product_id:
                S.Product.objects.filter(id=int(product_id)).update(**defaults)
            else:
                S.Product.objects.create(**defaults)

        await _save()
        return _redirect("/admin/products")

    # ── Users ──

    @app.get("/admin/users")
    async def admin_users(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S

        @sync_to_async
        def _data():
            return [
                {"id": e.id, "name": f"{e.first_name} {e.last_name}".strip(),
                 "email": e.email or "", "role": e.role, "pin": e.pin_code or "",
                 "active": e.is_active, "hourly_rate": float(e.hourly_rate or 0)}
                for e in S.Employee.objects.all().order_by("first_name")
            ]

        ctx = _base_context(request, "users", "Users")
        ctx["users"] = await _data()
        ctx["roles"] = [
            {"value": "admin", "label": "Administrator"},
            {"value": "manager", "label": "Manager"},
            {"value": "cashier", "label": "Cashier"},
            {"value": "server", "label": "Server"},
            {"value": "kitchen", "label": "Kitchen Staff"},
        ]
        ctx["edit_user"] = None
        return _html(_render("admin/users.html", ctx))

    @app.get("/admin/users/add")
    async def admin_users_add(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S

        @sync_to_async
        def _data():
            return [
                {"id": e.id, "name": f"{e.first_name} {e.last_name}".strip(),
                 "email": e.email or "", "role": e.role, "pin": e.pin_code or "",
                 "active": e.is_active, "hourly_rate": float(e.hourly_rate or 0)}
                for e in S.Employee.objects.all().order_by("first_name")
            ]

        ctx = _base_context(request, "users", "Users")
        ctx["users"] = await _data()
        ctx["roles"] = [
            {"value": "admin", "label": "Administrator"},
            {"value": "manager", "label": "Manager"},
            {"value": "cashier", "label": "Cashier"},
            {"value": "server", "label": "Server"},
            {"value": "kitchen", "label": "Kitchen Staff"},
        ]
        ctx["edit_user"] = {"first_name": "", "last_name": "", "email": "", "phone": "", "role": "cashier", "pin": "", "hourly_rate": 0, "active": True}
        return _html(_render("admin/users.html", ctx))

    @app.get("/admin/users/:user_id/edit")
    async def admin_users_edit(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S
        user_id = int(request.path_params.get("user_id", "0"))

        @sync_to_async
        def _data():
            return [
                {"id": e.id, "name": f"{e.first_name} {e.last_name}".strip(),
                 "email": e.email or "", "role": e.role, "pin": e.pin_code or "",
                 "active": e.is_active, "hourly_rate": float(e.hourly_rate or 0)}
                for e in S.Employee.objects.all().order_by("first_name")
            ]

        @sync_to_async
        def _user():
            try:
                e = S.Employee.objects.get(id=user_id)
                return {
                    "id": e.id, "first_name": e.first_name, "last_name": e.last_name,
                    "email": e.email or "", "phone": e.phone or "", "role": e.role,
                    "pin": e.pin_code or "", "hourly_rate": float(e.hourly_rate or 0),
                    "active": e.is_active,
                }
            except S.Employee.DoesNotExist:
                return None

        edit = await _user()
        if not edit:
            return _redirect("/admin/users")

        ctx = _base_context(request, "users", "Users")
        ctx["users"] = await _data()
        ctx["roles"] = [
            {"value": "admin", "label": "Administrator"},
            {"value": "manager", "label": "Manager"},
            {"value": "cashier", "label": "Cashier"},
            {"value": "server", "label": "Server"},
            {"value": "kitchen", "label": "Kitchen Staff"},
        ]
        ctx["edit_user"] = edit
        return _html(_render("admin/users.html", ctx))

    @app.post("/admin/users/save")
    async def admin_save_user(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        from routes import state as S
        body = _parse_form(request)
        user_id = body.get("id")

        @sync_to_async
        def _save():
            defaults = {
                "first_name": body.get("first_name", ""),
                "last_name": body.get("last_name", ""),
                "email": body.get("email", ""),
                "phone": body.get("phone", ""),
                "role": body.get("role", "cashier"),
                "pin_code": body.get("pin_code", ""),
                "hourly_rate": float(body.get("hourly_rate", 0)),
                "is_active": body.get("is_active") in (True, "1", 1, "true", "on"),
            }
            if user_id:
                S.Employee.objects.filter(id=int(user_id)).update(**defaults)
            else:
                S.Employee.objects.create(**defaults)

        await _save()
        return _redirect("/admin/users")

    # ── Sync Logs ──

    @app.get("/admin/sync-logs")
    async def admin_sync_logs(request: Request):
        session = _require_admin(request)
        if not session:
            return _redirect("/admin")
        from routes import state as S
        status_filter = request.query_params.get("status_filter", "")

        @sync_to_async
        def _logs():
            qs = S.SyncLog.objects.all()
            if status_filter:
                qs = qs.filter(status=status_filter)
            return [
                {"id": log.id, "node_id": log.node_id, "entity_type": log.entity_type,
                 "entity_id": log.entity_id, "direction": log.direction, "status": log.status,
                 "error_message": log.error_message or "",
                 "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "-"}
                for log in qs.order_by("-created_at")[:200]
            ]

        @sync_to_async
        def _summary():
            return {
                "total": S.SyncLog.objects.count(),
                "success": S.SyncLog.objects.filter(status__in=["success", "received", "processed"]).count(),
                "failed": S.SyncLog.objects.filter(status="failed").count(),
            }

        ctx = _base_context(request, "sync-logs", "Sync Logs")
        ctx["logs"] = await _logs()
        ctx["summary"] = await _summary()
        ctx["status_filter"] = status_filter
        return _html(_render("admin/sync-logs.html", ctx))

    @app.post("/admin/sync-logs/clear")
    async def admin_clear_sync_logs(request: Request):
        if not _require_admin(request):
            return _redirect("/admin")
        from routes import state as S

        @sync_to_async
        def _clear():
            S.SyncLog.objects.all().delete()

        await _clear()
        return _redirect("/admin/sync-logs")
