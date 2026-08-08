# -*- coding: utf-8 -*-
"""POS Cloud Sidecar — Robyn + Django ORM (Cloud Master Edition).

Single Robyn async server providing the REST + WebSocket API surface for
the pos-cloud SaaS. Uses the pos-cloud Django ORM (backend/apps.core) for
database access — the same models, migrations and admin as the Django
backend, served through a fast async sidecar.

Architecture:
    server.py       (bootstrap: Django ORM, state, middleware, CRUD registration)
    └── routes/     (feature route modules: info, orgs, crm, reports, sync, fusion)

Database:  pos_cloud.db (shared with the Django backend)
Framework: Robyn (async) + Django ORM (database)

Usage:
    python server.py --port 8767               # Default: port 8767
    python server.py --port 8767 --migrate      # Run Django migrations first
    pos-cloud-sidecar --port 8767               # Via pyproject.toml entry point
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Path setup — ensure sidecar dir and backend dir are importable
_PATH = Path(__file__).resolve().parent
_BACKEND = _PATH.parent / "backend"
for _p in (str(_PATH), str(_BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Version metadata (dunder-free so PyInstaller bundles it)
import about  # noqa: F401

if "--version" in sys.argv:
    print(f"{about.__title_full__} v{about.__version__}")
    sys.exit(0)

from robyn import Robyn, Response  # noqa: E402

# ---------------------------------------------------------------------------
# Django ORM bootstrap — shared database with the pos-cloud backend
# ---------------------------------------------------------------------------

_DJANGO_READY: bool = False

try:
    import django
    from django.conf import settings

    if not settings.configured:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
        django.setup()

    from django.db import connection  # noqa: F401

    # ── pos-cloud models (backend/apps.core) ──
    from apps.core.models import (  # noqa: E402
        Organization, Branch, Lead, Contact, Deal,
        InventoryReport, BranchReport, BranchSyncLog,
        BranchProduct, BranchSale, BranchInventory,
        DeviceToken, SyncConflict, SyncQueueItem,
    )

    _ALL_MODELS = [
        Organization, Branch, Lead, Contact, Deal,
        InventoryReport, BranchReport, BranchSyncLog,
        BranchProduct, BranchSale, BranchInventory,
        DeviceToken, SyncConflict, SyncQueueItem,
    ]

    _DJANGO_READY = True
    logging.info("POS Cloud Sidecar — Django ORM ready")
except Exception as exc:  # noqa: BLE001
    logging.critical("Django ORM bootstrap failed: %s", exc)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Logging & configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pos_cloud_sidecar")

HOST: str = os.environ.get("POS_CLOUD_HOST", "0.0.0.0")
PORT: int = int(os.environ.get("POS_CLOUD_PORT", "8767"))
API_KEY: str | None = os.environ.get("POS_CLOUD_API_KEY", None)
_start_time: datetime = datetime.now(timezone.utc)
DB_PATH = _BACKEND / "pos_cloud.db"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="POS Cloud Sidecar - Robyn + Django ORM")
    p.add_argument("--host", default=HOST)
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--api-key", default=API_KEY)
    p.add_argument("--dev", action="store_true")
    p.add_argument("--version", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--migrate", action="store_true", help="Run Django migrations before serving")
    return p.parse_args()


def _ensure_tables() -> None:
    """Create any missing tables for the registry models (idempotent)."""
    from django.core.management import call_command
    call_command("migrate", interactive=False, verbosity=0)
    logger.info("Tables ensured via Django migrations")


# ===========================================================================
# Robyn app + middleware
# ===========================================================================

app = Robyn(__file__)


@app.before_request()
async def log_req(request):
    logger.info("%s %s", request.method, request.url)
    return request


@app.before_request()
async def cors_preflight(request):
    if request.method.upper() == "OPTIONS":
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, X-API-Key, Authorization",
                "Access-Control-Max-Age": "86400",
            },
            description="",
        )
    return request


@app.after_request()
def add_cors(response: Response):
    if "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# ===========================================================================
# Routes
# ===========================================================================

from robyn import jsonify  # noqa: E402
from handlers import _register_crud, _count  # noqa: E402


@app.get("/")
async def index(request):
    counts = {}
    for m in _ALL_MODELS:
        try:
            counts[m.__name__] = await _count(m)
        except Exception:  # noqa: BLE001
            counts[m.__name__] = -1
    return jsonify({
        "service": about.__service_desc_full__,
        "version": about.__version__,
        "database": str(DB_PATH),
        "django_orm": _DJANGO_READY,
        "num_models": len(_ALL_MODELS),
        "counts": counts,
    })


@app.get("/health")
async def health(request):
    return jsonify({
        "status": "healthy",
        "service": about.__service_name_full__,
        "version": about.__version__,
        "uptime": (datetime.now(timezone.utc) - _start_time).total_seconds(),
        "django_orm": _DJANGO_READY,
        "database": str(DB_PATH),
    })


@app.get("/stats")
async def stats_endpoint(request):
    counts = {}
    for m in _ALL_MODELS:
        try:
            counts[m.__name__] = await _count(m)
        except Exception:  # noqa: BLE001
            counts[m.__name__] = -1
    return jsonify({"counts": counts, "models": [m.__name__ for m in _ALL_MODELS]})


# ── Organization & branches ──
_register_crud(app, "organizations", Organization, "Organization")
_register_crud(app, "branches", Branch, "Branch")

# ── CRM ──
_register_crud(app, "leads", Lead, "Lead")
_register_crud(app, "contacts", Contact, "Contact")
_register_crud(app, "deals", Deal, "Deal")

# ── Reports ──
_register_crud(app, "inventory-reports", InventoryReport, "InventoryReport")
_register_crud(app, "branch-reports", BranchReport, "BranchReport")

# ── Branch sync data ──
_register_crud(app, "sync/logs", BranchSyncLog, "BranchSyncLog")
_register_crud(app, "sync/products", BranchProduct, "BranchProduct")
_register_crud(app, "sync/sales", BranchSale, "BranchSale")
_register_crud(app, "sync/inventory", BranchInventory, "BranchInventory")

# ── System ──
_register_crud(app, "device-tokens", DeviceToken, "DeviceToken")
_register_crud(app, "conflicts", SyncConflict, "SyncConflict")
_register_crud(app, "queue", SyncQueueItem, "SyncQueueItem")


# ── Fusion feature routes ──
from routes.fusion import register_fusion_routes  # noqa: E402
register_fusion_routes(app)


# ===========================================================================
# main()
# ===========================================================================

def main() -> None:
    args = _parse_args()
    if args.migrate:
        _ensure_tables()
    logger.info("POS Cloud Sidecar listening on %s:%s", args.host, args.port)
    app.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
