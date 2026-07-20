# -*- coding: utf-8 -*-
"""
POS Server - Robyn + Django ORM (Standalone Edition).

Single Robyn async server providing all REST + WebSocket APIs using Django ORM
for database access. Route handlers are organized in the routes/ package.

Architecture:
    server.py  (thin entry point: bootstrap, middleware, init_state, register_all)
        └── routes/__init__.py  (register_all -> routes/)
            ├── routes/info.py       (/, /health)
            ├── routes/nodes.py      (node CRUD, register, heartbeat, WS /ws/nodes)
            ├── routes/config.py     (device config, master, cloud links, WS /ws/config)
            ├── routes/sync.py       (sync status, trigger, push/receive, cloud push)
            └── routes/approvals.py  (approve, reject, stats)

Database:  ../unified.db (standalone — no Rust backend sharing)
Framework: Robyn (async) + Django ORM (database)

Usage:
    python server.py                          # Default: port 8765
    python server.py --port 8765 --verbose     # Dev mode
    python server.py --version                 # Show version
    pos-solo-server --port 8765                # Via pyproject.toml entry point

Full docs: projects/pos/docs/POS_ARCHITECTURE.md
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Add shared-portal to Python path (canonical source for 'shared' module)
# Must come BEFORE any shared imports (including --version fast-path)
# ---------------------------------------------------------------------------

_PATH = Path(__file__).resolve().parent
if str(_PATH.parent.parent) not in sys.path:
    sys.path.insert(0, str(_PATH.parent.parent))

# Fast-path: --version does not require Django bootstrap
if "--version" in sys.argv:
    from shared.__about__ import __title_solo__, __version__
    print(f"{__title_solo__} v{__version__}")
    sys.exit(0)

from robyn import Robyn, Response, Request

# ---------------------------------------------------------------------------
# Django ORM bootstrap - standalone database (unified.db, pos-solo does not share with Rust)
# ---------------------------------------------------------------------------

_DJANGO_READY: bool = False

try:
    import django
    from django.conf import settings
    from django.db import connection

    BASE_DIR = Path(__file__).resolve().parent
    # Standalone DB — pos-solo uses managed=True models, no Rust backend
    DB_PATH = BASE_DIR.parent / "unified.db"

    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(DB_PATH),
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "models.PosSoloConfig",     # Managed models (pos_unified) — migrations + CRUD
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY", "pos-server-dev-key"),
    )
    django.setup()

    from models.pos import (
        Category, Product, Customer, Sale, SaleItem,
        InventoryTransaction, Employee,
    )
    from models.menu import MenuItem, Menu, MenuItemAssignment
    from models.node import Node, Heartbeat, NodeEvent
    from models.config import DeviceConfig, MasterDevice, CloudLink
    from models.sync import SyncLog

    # ── Shared models ──
    from shared.models.approval import SyncApproval
    from shared.services.sync import ProductSyncEngine
    from shared.models.token import DeviceToken
    from shared.models.audit import SignalEvent

    _ALL_MODELS = [
        Category, Product, Customer, Sale, SaleItem,
        InventoryTransaction, Employee,
        MenuItem, Menu, MenuItemAssignment,
        Node, Heartbeat, NodeEvent, SyncLog,
        DeviceConfig, MasterDevice, CloudLink,
        SyncApproval,
        DeviceToken,
        SignalEvent,
    ]

    _CONFIG_MODELS = [
        DeviceConfig, MasterDevice, CloudLink,
    ]

    # Product sync engine
    sync_engine = ProductSyncEngine(
        sync_log_model=SyncLog,
        node_model=Node,
        device_config_model=DeviceConfig,
        node_event_model=NodeEvent,
        sync_approval_model=SyncApproval,
        cloud_link_model=CloudLink,
    )

    # Table creation is deferred to main() — controlled by --migrate flag.
    # This avoids running migrations/calls when server.py is imported by tests.

    _DJANGO_READY = True
    logging.info("POS Server - Django ORM ready (db: %s)", DB_PATH)

except Exception as exc:
    logging.critical("Django ORM bootstrap failed: %s", exc)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Logging & Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pos_server")

HOST: str = os.environ.get("POS_HOST", "0.0.0.0")
PORT: int = int(os.environ.get("POS_PORT", "8765"))
API_KEY: str | None = os.environ.get("POS_API_KEY", None)
CLOUD_CRM_URL: str = os.environ.get("CLOUD_CRM_URL", "http://127.0.0.1:8767")
CLOUD_API_KEY: str | None = os.environ.get("CLOUD_API_KEY", None)
_start_time: datetime = datetime.now(timezone.utc)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="POS Server - Robyn + Django ORM")
    p.add_argument("--host", default=HOST)
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--api-key", default=API_KEY)
    p.add_argument("--cloud-url", default=CLOUD_CRM_URL)
    p.add_argument("--cloud-key", default=CLOUD_API_KEY)
    p.add_argument("--dev", action="store_true")
    p.add_argument("--version", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--migrate", action="store_true", help="Use Django migrations (not schema_editor)")
    return p.parse_args()


def _ensure_tables(use_migrations: bool) -> None:
    """Create database tables for managed models.

    Called from main() after argparse, so importing server.py (e.g. for tests)
    never triggers migrations or schema changes.
    """
    if use_migrations:
        from django.core.management import call_command
        call_command("migrate", verbosity=0)
        logger.info("Tables created via Django migrations (--migrate)")
    else:
        with connection.schema_editor() as schema_editor:
            for model in _ALL_MODELS:
                try:
                    schema_editor.create_model(model)
                except Exception:
                    pass
        logger.info("Tables ensured via schema_editor (use --migrate for Django migrations)")


# ---------------------------------------------------------------------------
# Pydantic validation (optional)
# ---------------------------------------------------------------------------

_PYDANTIC_READY: bool = False
try:
    from pydantic import BaseModel, Field, ValidationError

    class ProductCreate(BaseModel):
        name: str = Field(min_length=1, max_length=200)
        price: float = Field(gt=0)
        sku: str | None = None
        category_id: int | None = None
        stock_quantity: int = 0
        description: str = ""
        model_config = {"extra": "allow"}

    class CustomerCreate(BaseModel):
        first_name: str = Field(min_length=1)
        last_name: str = ""
        email: str | None = None
        phone: str = ""
        model_config = {"extra": "allow"}

    class SaleCreate(BaseModel):
        customer_id: int | None = None
        payment_method: str = "cash"
        items: list[dict] = Field(min_length=1)
        model_config = {"extra": "allow"}

    class NodeRegisterRequest(BaseModel):
        node_id: str | None = None
        hostname: str | None = None
        node_type: str = "pos-solo"
        version: str = "unknown"
        api_version: str = "1.0"
        status: str = "online"
        product_count: int = Field(default=0, ge=0)
        transaction_count: int = Field(default=0, ge=0)
        customer_count: int = Field(default=0, ge=0)
        ip_address: str | None = None
        port: int | None = None
        capabilities: dict = Field(default_factory=dict)
        metadata: dict = Field(default_factory=dict)
        model_config = {"extra": "allow"}

    class HeartbeatRequest(BaseModel):
        node_id: str = Field(min_length=1)
        status: str = "online"
        version: str | None = None
        product_count: int | None = Field(default=None, ge=0)
        transaction_count: int | None = Field(default=None, ge=0)
        model_config = {"extra": "allow"}

    _PYDANTIC_READY = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Imports from shared modules
# ---------------------------------------------------------------------------

# ── Signals ──
from shared.signals import (
    fire_config_changed,
    fire_config_synced,
    fire_device_status_changed,
)

# ── Token Authentication ──
from shared.models.token import DeviceToken
from shared.middleware.auth import create_auth_middleware, register_auth_routes, get_token_info

# ── Signal Handlers (logging, webhooks, audit) ──
import shared.handlers.signal  # noqa: F401 - registers @receiver handlers
import shared.sync_signals  # noqa: F401 - registers sync tracking receivers


# ===========================================================================
# Initialize shared state for route modules
# ===========================================================================

from routes.state import init_state

init_state(
    _DJANGO_READY=_DJANGO_READY,
    _PYDANTIC_READY=_PYDANTIC_READY,
    _ALL_MODELS=_ALL_MODELS,
    _CONFIG_MODELS=_CONFIG_MODELS,
    Category=Category,
    Product=Product,
    Customer=Customer,
    Sale=Sale,
    SaleItem=SaleItem,
    InventoryTransaction=InventoryTransaction,
    Employee=Employee,
    MenuItem=MenuItem,
    Menu=Menu,
    MenuItemAssignment=MenuItemAssignment,
    Node=Node,
    Heartbeat=Heartbeat,
    NodeEvent=NodeEvent,
    SyncLog=SyncLog,
    DeviceConfig=DeviceConfig,
    MasterDevice=MasterDevice,
    CloudLink=CloudLink,
    SyncApproval=SyncApproval,
    DeviceToken=DeviceToken,
    SignalEvent=SignalEvent,
    sync_engine=sync_engine,
    DB_PATH=DB_PATH,
    CLOUD_CRM_URL=CLOUD_CRM_URL,
    CLOUD_API_KEY=CLOUD_API_KEY,
    SYNC_STATE_PATH=BASE_DIR / "sync_state.json",
    _start_time=_start_time,
    BASE_DIR=BASE_DIR,
    fire_config_changed=fire_config_changed,
    fire_config_synced=fire_config_synced,
    fire_device_status_changed=fire_device_status_changed,
    NodeRegisterRequest=NodeRegisterRequest if _PYDANTIC_READY else None,
    HeartbeatRequest=HeartbeatRequest if _PYDANTIC_READY else None,
)


# ===========================================================================
# Robyn app
# ===========================================================================

app = Robyn(__file__)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


@app.before_request()
async def log_req(request: Request):
    logger.info("%s %s", request.method, request.url)
    return request


@app.before_request()
async def cors_preflight(request: Request):
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


# ── Token-based authentication middleware ──
app.before_request()(create_auth_middleware(
    token_model=DeviceToken,
    api_key=API_KEY,
    public_paths={"/", "/health"},
))


# ===========================================================================
# Generic CRUD router factory (imported from routes.state)
# ===========================================================================

from routes.state import _register_crud

# Register all CRUD endpoints
_register_crud(app, "products", Product, "Product")
_register_crud(app, "customers", Customer, "Customer")
_register_crud(app, "sales", Sale, "Sale")
_register_crud(app, "sale-items", SaleItem, "SaleItem")
_register_crud(app, "inventory", InventoryTransaction, "Inventory")
_register_crud(app, "employees", Employee, "Employee")
_register_crud(app, "categories", Category, "Category")
_register_crud(app, "menu-items", MenuItem, "MenuItem")
_register_crud(app, "menus", Menu, "Menu")
_register_crud(app, "menu-assignments", MenuItemAssignment, "MenuItemAssignment")
_register_crud(app, "nodes", Node, "Node")
_register_crud(app, "heartbeats", Heartbeat, "Heartbeat")
_register_crud(app, "sync-logs", SyncLog, "SyncLog")

# ── Configuration CRUD ──
_register_crud(app, "config/devices", DeviceConfig, "DeviceConfig")
_register_crud(app, "config/master", MasterDevice, "MasterDevice")
_register_crud(app, "config/cloud-links", CloudLink, "CloudLink")
_register_crud(app, "approvals", SyncApproval, "SyncApproval")

# ===========================================================================
# WebSocket: Entity event stream (real-time CRUD notifications for Redux)
# ===========================================================================

from streams import _entity_ws_clients

@app.websocket("/ws/entities")
async def entity_stream(websocket):
    """WebSocket endpoint for entity change events.
    Client connects to receive real-time notifications when any entity
    (Product, Customer, Sale, etc.) is created, updated, or deleted.
    The Redux middleware uses this to invalidate RTK Query caches."""
    client_id = id(websocket)
    _entity_ws_clients.add(websocket)
    try:
        import json as _json
        from datetime import datetime as _dt, timezone as _tz
        await websocket.send_text(_json.dumps({
            "type": "connected",
            "message": "Connected to entity event stream",
            "client_id": client_id,
            "timestamp": _dt.now(_tz.utc).isoformat(),
        }))
        while True:
            msg = await websocket.receive_text()
    except Exception:
        pass
    finally:
        _entity_ws_clients.discard(websocket)


# ===========================================================================
# Register all custom route handlers from routes/ package
# ===========================================================================

from routes import register_all
register_all(app)


# ===========================================================================
# Entry point
# ===========================================================================


def main():
    """Start the POS Server.

    Entry point for `pos-solo-server` console script (via pyproject.toml).
    Also called by `if __name__ == "__main__":` when run directly.
    """
    args = _parse_args()

    if args.version:
        from shared.__about__ import __title_solo__, __version__
        print(f"{__title_solo__} v{__version__}")
        return

    if not _DJANGO_READY:
        logger.error("Django ORM bootstrap failed, cannot start")
        sys.exit(1)

    # Create/ensure database tables (migrations or schema_editor)
    _ensure_tables(args.migrate)

    if args.verbose:
        logging.getLogger("pos_server").setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("POS Server starting on %s:%s", args.host, args.port)
    logger.info("Database: %s", DB_PATH)
    logger.info("Django ORM: %s | Pydantic: %s", _DJANGO_READY, _PYDANTIC_READY)
    logger.info("Models loaded: %d total", len(_ALL_MODELS))
    logger.info("=" * 60)

    # Register auth routes
    register_auth_routes(app, token_model=DeviceToken)

    # Log available endpoints
    logger.info("── Available API Endpoints ──")
    logger.info("  CRUD:   /products, /customers, /sales, /inventory, ...")
    logger.info("  Nodes:  POST /nodes/register, POST /nodes/heartbeat, PATCH/DELETE /nodes/:node_id")
    logger.info("  Config: GET/POST/DELETE /nodes/:node_id/config, /config/*")
    logger.info("  Sync:   GET /sync/status | POST /sync/trigger | POST /cloud/push/:type")
    logger.info("  Auth:   POST /auth/token | POST /auth/refresh | GET /auth/verify")
    logger.info("  WS:     /ws/config (config events)")
    logger.info("  Info:   GET /, /health, /stats")
    logger.info("  Approvals: POST /approvals/:pk/approve|reject, GET /approvals/stats")
    logger.info("  Sync Push: POST /sync/receive/sales|reports|inventory")
    logger.info("─" * 60)

    app.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
