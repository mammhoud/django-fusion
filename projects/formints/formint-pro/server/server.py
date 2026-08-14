# -*- coding: utf-8 -*-
"""
POS Full Server - Robyn + Django ORM (Cloud Master Edition).

Single entry point serving both backends:
* Django management CLI — when launched as the bundled ``formint-backend``
  binary with Django subcommands (``runserver``, ``migrate``, …), it delegates
  to Django's management CLI (this replaces the former ``sidecar.py`` entry).
* Robyn async server — the default, providing all REST + WebSocket APIs using
  Django ORM for database access. Route handlers live in the routes/ package.

Architecture:
    server.py  (thin entry point: bootstrap, middleware, init_state, register_all)
        └── routes/__init__.py  (register_all -> routes/)
            ├── routes/info.py       (/, /health, /stats)
            ├── routes/nodes.py      (nodes, node config, WS /ws/nodes)
            ├── routes/config.py     (device config, master, cloud links, WS /ws/config)
            ├── routes/sync.py       (sync status, trigger, push/receive, cloud push)
            ├── routes/approvals.py  (approve, reject, stats)
            └── routes/webhooks.py   (receive, list, stats)

Database:  full_portal.db
Framework: Robyn (async) + Django ORM (database)

Usage:
    python server.py --port 8766               # Default: port 8766
    python server.py --port 8766 --verbose      # Dev mode
    python server.py --version                  # Show version
    pos-full-server --port 8766                 # Via pyproject.toml entry point

Full docs: projects/formints/docs/POS_ARCHITECTURE.md
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Path setup — ensure server dir is importable
_PATH = Path(__file__).resolve().parent
if str(_PATH) not in sys.path:
    sys.path.insert(0, str(_PATH))

# Version metadata. Module-scope import so PyInstaller bundles it (PyInstaller's
# modulegraph silently drops dunder-named modules, so this is ``about``).
import about  # noqa: F401  (used below and by routes/info, fragments/about)

# Fast-path: --version does not require Django bootstrap
if "--version" in sys.argv:
    print(f"{about.__title_full__} v{about.__version__}")
    sys.exit(0)

# ── Django management entry (merged from the former sidecar.py, 2026-08) ───
# The Tauri shell / PyInstaller ``formint-backend`` binary is launched with
# Django management arguments (``runserver``, ``migrate``, …). Detect that
# case and delegate to Django's CLI before the Robyn bootstrap so one entry
# point serves the Django admin/HTMX backend and the Robyn API server.
_DJANGO_MANAGEMENT_SUBCOMMANDS = frozenset({
    "runserver",
    "migrate",
    "makemigrations",
    "check",
    "shell",
    "collectstatic",
    "createsuperuser",
    "seed_demo",
})


def manage() -> None:
    """Run Django's management CLI (the former ``sidecar.py`` entry point)."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
    from django.core.management import execute_from_command_line

    execute_from_command_line(["formint-backend", *sys.argv[1:]])


if __name__ == "__main__" and sys.argv[1:] and sys.argv[1] in _DJANGO_MANAGEMENT_SUBCOMMANDS:
    manage()
    sys.exit(0)

from robyn import Robyn, Response, Request

# ---------------------------------------------------------------------------
# Django ORM bootstrap - shared database (full_portal.db)
# ---------------------------------------------------------------------------

_DJANGO_READY: bool = False

try:
    import django
    from django.conf import settings
    from django.db import connection

    BASE_DIR = Path(__file__).resolve().parent
    # Shared database with Rust backend (pos-full/restaurant.db)
    DB_PATH = BASE_DIR.parent / "restaurant.db"

    if not settings.configured:
        # Import centralized config (configs/__init__.py)
        from configs import (
            DEBUG, DATABASES, INSTALLED_APPS, MIDDLEWARE,
            TEMPLATES, ROOT_URLCONF, SECRET_KEY,
            DEFAULT_AUTO_FIELD, USE_TZ, STATIC_URL, STATIC_ROOT,
            UNFOLD,
        )
        settings.configure(
            DEBUG=DEBUG,
            DATABASES=DATABASES,
            INSTALLED_APPS=INSTALLED_APPS,
            MIDDLEWARE=MIDDLEWARE,
            TEMPLATES=TEMPLATES,
            ROOT_URLCONF=ROOT_URLCONF,
            SECRET_KEY=SECRET_KEY,
            DEFAULT_AUTO_FIELD=DEFAULT_AUTO_FIELD,
            USE_TZ=USE_TZ,
            STATIC_URL=STATIC_URL,
            STATIC_ROOT=STATIC_ROOT,
            # Unfold admin theme config (sidebar, dashboard callback, login, colors)
            UNFOLD=UNFOLD,
        )
        # Import admin registration AFTER settings but before setup()
        # (admin.py registers models which requires app registry ready after setup)
    django.setup()
    # Import admin registration AFTER django.setup() (requires app registry)
    import formint.admin  # noqa: F401 — side-effect: registers admin models (canonical)

    # ── Django-managed node registry models ──
    from models.pos import (
        Category, Product, Customer, Sale, SaleItem,
        InventoryTransaction, Employee,
    )
    from models.menu import MenuItem, Menu, MenuItemAssignment
    from models.node import Node, Heartbeat, NodeEvent
    from models.config import DeviceConfig, MasterDevice, CloudLink
    from models.sync import SyncLog
    from models.inventory import Supplier, PurchaseOrder, PurchaseOrderItem
    from models.ops import KitchenTicket, SupportTicket
    from models.hr import Payroll, EmployeeSchedule, TaxReport
    from models.notes import Note

    # ── Extra managed models (Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment) ──
    from models.extra import Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment

    # ── Loyalty & client settings models ──
    from models.loyalty import ClientCategory, LoyaltyTransaction, UserSettings

    # ── API Key model ──
    from models.apikey import ApiKey

    # ── Local shared-style models ──
    from models.approval import SyncApproval
    from services.sync import ProductSyncEngine
    from models.token import DeviceToken
    from models.audit import SignalEvent

    # Registry models (managed=True)
    _REGISTRY_MODELS = [
        Category, Product, Customer, Sale, SaleItem,
        InventoryTransaction, Employee,
        MenuItem, Menu, MenuItemAssignment,
        Node, Heartbeat, NodeEvent, SyncLog,
        DeviceConfig, MasterDevice, CloudLink,
        SyncApproval,
        DeviceToken,
        SignalEvent,
        Supplier, PurchaseOrder, PurchaseOrderItem,
        KitchenTicket, SupportTicket,
        Payroll, EmployeeSchedule, TaxReport,
        Note,
        # ── Extra managed models (added 2026-07-22) ──
        Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
        # ── Loyalty & client settings (added 2026-08-04) ──
        ClientCategory, LoyaltyTransaction, UserSettings,
        # ── API Key model (added 2026-08-05) ──
        ApiKey,
    ]

    # Config models for dedicated CRUD
    _CONFIG_MODELS = [
        DeviceConfig, MasterDevice, CloudLink,
    ]

    _ALL_MODELS = _REGISTRY_MODELS

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
    logging.info("POS Full Server - Django ORM ready (db: %s)", DB_PATH)

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
logger = logging.getLogger("pos_full_server")

HOST: str = os.environ.get("POS_FULL_HOST", "0.0.0.0")
PORT: int = int(os.environ.get("POS_FULL_PORT", "8766"))
API_KEY: str | None = os.environ.get("POS_FULL_API_KEY", None)
_start_time: datetime = datetime.now(timezone.utc)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="POS Full Server - Robyn + Django ORM")
    p.add_argument("--host", default=HOST)
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--api-key", default=API_KEY)
    p.add_argument("--dev", action="store_true")
    p.add_argument("--version", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--migrate", action="store_true", help="Use Django migrations (not schema_editor)")
    p.add_argument("--sync-interval", type=int, default=None,
                   help="Seconds between auto-sync cycles (env: POS_FULL_SYNC_INTERVAL, default: 60)")
    p.add_argument("--sync-node-id", default=None,
                   help="Node ID for scheduled sync (env: POS_FULL_NODE_ID, default: pos-full-auto)")
    p.add_argument("--no-sync", action="store_true",
                   help="Disable scheduled branch sync (env: POS_FULL_SYNC_ENABLED=false)")
    return p.parse_args()


def _ensure_tables(use_migrations: bool) -> None:
    """Create database tables for managed models and add missing columns.

    Called from main() after argparse, so importing server.py (e.g. for tests)
    never triggers migrations or schema changes.

    For existing databases, ``_add_missing_columns()`` runs ``ALTER TABLE``
    for every model field that isn't a relation — this handles model
    changes (e.g. adding ``cashback_amount``) without requiring Django
    migrations or a full database reset.
    """
    if use_migrations:
        from django.core.management import call_command
        call_command("migrate", interactive=False, verbosity=0)
        logger.info("Tables created via Django migrations (--migrate)")
    else:
        table_names = connection.introspection.table_names()
        for model in _REGISTRY_MODELS:
            if model._meta.db_table not in table_names:
                try:
                    with connection.schema_editor() as schema_editor:
                        schema_editor.create_model(model)
                except Exception as e:
                    logger.debug(f"Could not create table for {model._meta.db_table}: {e}")

        # ── Ensure django_content_type table (needed by DataToken.tag_row → ContentType.get_for_model) ──
        if "django_content_type" not in table_names:
            try:
                from django.contrib.contenttypes.models import ContentType
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(ContentType)
                logger.info("Created django_content_type table for DataToken/ContentType lookups")
            except Exception as e:
                logger.warning("Could not create django_content_type table: %s", e)

        # ── Ensure ci_datatoken table (needed by DataToken.objects.create / tag_row) ──
        if "ci_datatoken" not in table_names:
            try:
                from django_fusion.core.models import DataToken
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(DataToken)
                logger.info("Created ci_datatoken table for DataToken sync tracking")
            except Exception as e:
                logger.warning("Could not create ci_datatoken table: %s", e)

        # ── Populate content types so ContentType.objects.get_for_model() doesn't fail on lookup ──
        try:
            from django.contrib.contenttypes.management import create_contenttypes
            from django.apps import apps
            for app_config in apps.get_app_configs():
                create_contenttypes(app_config, interactive=False, verbosity=0)
        except Exception as e:
            logger.debug("Could not auto-populate content types: %s", e)

        # Add missing columns for model fields added after initial creation
        _add_missing_columns(table_names)
        logger.info("Tables ensured via schema_editor + missing columns added (use --migrate for Django migrations)")


def _add_missing_columns(existing_tables: set[str]) -> None:
    """Check each registry model's table for missing columns and ALTER TABLE.

    Iterates over all managed Django model fields.  For each field in a table
    that already exists, checks whether the column exists in SQLite's
    ``PRAGMA table_info``.  If missing, runs ``ALTER TABLE ADD COLUMN`` with
    the field's nullable/default/type definition.

    This keeps schema in sync without requiring Django migrations or
    ``schema_editor.create_model()`` (which only works for new tables).
    """
    from django.db.models import Field

    for model in _REGISTRY_MODELS:
        db_table = model._meta.db_table
        if db_table not in existing_tables:
            continue  # Already created by _ensure_tables above

        # Get existing column names from SQLite pragma
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'PRAGMA table_info("{db_table}")')
                existing_cols = {row[1] for row in cursor.fetchall()}
        except Exception:
            logger.warning("Cannot inspect columns for %s — skipping", db_table)
            continue

        # Check each model field
        for field in model._meta.local_fields:
            col_name = field.column
            if col_name in existing_cols:
                continue
            if field.primary_key or field.is_relation:
                continue

            # Build the ADD COLUMN SQL
            try:
                col_type = field.db_type(connection=connection)
                nullable = "" if field.null else " NOT NULL"
                default = ""
                if field.has_default():
                    default_val = field.get_default()
                    if default_val is not None:
                        if isinstance(default_val, str):
                            default = f" DEFAULT '{default_val}'"
                        elif isinstance(default_val, (int, float)):
                            default = f" DEFAULT {default_val}"
                        elif isinstance(default_val, bool):
                            default = f" DEFAULT {1 if default_val else 0}"

                sql = f'ALTER TABLE "{db_table}" ADD COLUMN "{col_name}" {col_type}{nullable}{default}'
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                logger.info("Added column %s.%s (%s)", db_table, col_name, col_type)
            except Exception as e:
                logger.debug("Could not add column %s.%s: %s", db_table, col_name, e)


# ---------------------------------------------------------------------------
# Pydantic validation (optional)
# ---------------------------------------------------------------------------

_PYDANTIC_READY: bool = False
try:
    from pydantic import BaseModel, Field, ValidationError

    class NodeRegisterRequest(BaseModel):
        node_id: str | None = None
        hostname: str | None = None
        node_type: str = "pos-full"
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
from signals import (
    fire_config_changed,
    fire_config_synced,
    fire_device_status_changed,
)

# ── Token Authentication ──
from models.token import DeviceToken
from middleware.auth import create_auth_middleware, register_auth_routes, get_token_info

# ── Fusion Health Check ──
from middleware.fusion import register_fusion_health_routes

# ── Signal Handlers (logging, webhooks, audit) ──
import signal_handlers  # noqa: F401 - registers @receiver handlers
import sync_signals  # noqa: F401 - registers sync tracking receivers
import ws_sync_signals  # noqa: F401 - registers real-time cloud sync receivers

# ── Cloud WebSocket sync client ──
from ws_client import start_client as _start_cloud_ws_client

# ── Signal Models (audit trail) ──
from models.audit import SignalEvent


# ===========================================================================
# Initialize shared state for route modules
# ===========================================================================

from routes.state import init_state

init_state(
    _DJANGO_READY=_DJANGO_READY,
    _PYDANTIC_READY=_PYDANTIC_READY,
    _ALL_MODELS=_ALL_MODELS,
    _REGISTRY_MODELS=_REGISTRY_MODELS,
    _CONFIG_MODELS=_CONFIG_MODELS,
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
    ClientCategory=ClientCategory,
    LoyaltyTransaction=LoyaltyTransaction,
    UserSettings=UserSettings,
    sync_engine=sync_engine,
    DB_PATH=DB_PATH,
    CLOUD_CRM_URL=os.environ.get("CLOUD_CRM_URL", ""),
    CLOUD_API_KEY=os.environ.get("CLOUD_API_KEY", None),
    SYNC_STATE_PATH=BASE_DIR / "sync_state.json",
    _start_time=_start_time,
    BASE_DIR=BASE_DIR,
    fire_config_changed=fire_config_changed,
    fire_config_synced=fire_config_synced,
    fire_device_status_changed=fire_device_status_changed,
    NodeRegisterRequest=NodeRegisterRequest if _PYDANTIC_READY else None,
    HeartbeatRequest=HeartbeatRequest if _PYDANTIC_READY else None,
    sync_scheduler=None,  # set in main() after scheduler is created
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
    public_paths={"/", "/health", "/auth/token", "/auth/verify", "/docs", "/openapi.json", "/fusion/health", "/fusion/render/dashboard", "/fusion/render/suppliers", "/fusion/render/about", "/api-keys", "/api-keys/", "/api-keys/scopes"},
))


# ── Scoped API key middleware (enforces X-API-Key on /api/v1/ paths) ──
from middleware.apikey_scoped import create_scoped_api_key_middleware
app.before_request()(create_scoped_api_key_middleware(
    public_paths={"/", "/health", "/auth/token", "/auth/verify", "/docs", "/openapi.json", "/fusion/health", "/api/v1/docs", "/api/v1/docs/", "/api/v1/docs/swagger", "/api/v1/docs/redoc", "/api/v1/openapi.json", "/api-keys/", "/api-keys/scopes"},
))


# ===========================================================================
# Generic CRUD router factory (imported from routes.state)
# ===========================================================================

from routes.state import _register_crud

# ── POS Core CRUD with DataToken sync tagging ──
# Read node_id from env (same variable used by --sync-node-id CLI flag)
_DATA_TOKEN_NODE_ID = os.environ.get("POS_FULL_NODE_ID", "pos-full-auto")
_tag_sync = dict(tag_for_sync=True, node_id=_DATA_TOKEN_NODE_ID, token_prefix="pos_full")

_register_crud(app, "products", Product, "Product", **_tag_sync)
_register_crud(app, "categories", Category, "Category", **_tag_sync)
_register_crud(app, "customers", Customer, "Customer", **_tag_sync)
_register_crud(app, "sales", Sale, "Sale", **_tag_sync)
_register_crud(app, "sale-items", SaleItem, "SaleItem", **_tag_sync)
_register_crud(app, "employees", Employee, "Employee", **_tag_sync)
_register_crud(app, "inventory", InventoryTransaction, "InventoryTransaction", **_tag_sync)

# ── Managed POS Core CRUD (models/ package, full_* tables) ──
_register_crud(app, "managed/categories", Category, "Category", **_tag_sync)
_register_crud(app, "managed/products", Product, "Product", **_tag_sync)
_register_crud(app, "managed/customers", Customer, "Customer", **_tag_sync)
_register_crud(app, "managed/sales", Sale, "Sale", **_tag_sync)
_register_crud(app, "managed/sale-items", SaleItem, "SaleItem", **_tag_sync)
_register_crud(app, "managed/employees", Employee, "Employee", **_tag_sync)
_register_crud(app, "managed/inventory", InventoryTransaction, "InventoryTransaction", **_tag_sync)
_register_crud(app, "managed/menu-items", MenuItem, "MenuItem", **_tag_sync)
_register_crud(app, "managed/menus", Menu, "Menu", **_tag_sync)
_register_crud(app, "managed/menu-assignments", MenuItemAssignment, "MenuItemAssignment", **_tag_sync)

# ── Suppliers & Procurement ──
_register_crud(app, "suppliers", Supplier, "Supplier", **_tag_sync)
_register_crud(app, "purchase-orders", PurchaseOrder, "PurchaseOrder", **_tag_sync)
_register_crud(app, "purchase-order-items", PurchaseOrderItem, "PurchaseOrderItem", **_tag_sync)

# ── Kitchen & Support ──
_register_crud(app, "kitchen-tickets", KitchenTicket, "KitchenTicket", **_tag_sync)
_register_crud(app, "support-tickets", SupportTicket, "SupportTicket", **_tag_sync)

# ── Registry CRUD ──
_register_crud(app, "heartbeats", Heartbeat, "Heartbeat", **_tag_sync)
_register_crud(app, "sync-logs", SyncLog, "SyncLog", **_tag_sync)

# ── Configuration CRUD ──
_register_crud(app, "config/devices", DeviceConfig, "DeviceConfig", **_tag_sync)
_register_crud(app, "config/master", MasterDevice, "MasterDevice", **_tag_sync)
_register_crud(app, "config/cloud-links", CloudLink, "CloudLink", **_tag_sync)

# ── Approval workflow CRUD ──
_register_crud(app, "approvals", SyncApproval, "SyncApproval", **_tag_sync)

# ── HR / Payroll CRUD ──
_register_crud(app, "payroll", Payroll, "Payroll", **_tag_sync)
_register_crud(app, "employee-schedules", EmployeeSchedule, "EmployeeSchedule", **_tag_sync)
_register_crud(app, "tax-reports", TaxReport, "TaxReport", **_tag_sync)

# ── Notes CRUD ──
_register_crud(app, "notes", Note, "Note", **_tag_sync)

# ── Extra managed CRUD (added 2026-07-22) with DataToken auto-tagging ──
_register_crud(app, "ingredients", Ingredient, "Ingredient", **_tag_sync)
_register_crud(app, "recipes", Recipe, "Recipe", **_tag_sync)
_register_crud(app, "receipt-templates", ReceiptTemplate, "ReceiptTemplate", **_tag_sync)
_register_crud(app, "roles", Role, "Role", **_tag_sync)
_register_crud(app, "inventory-adjustments", InventoryAdjustment, "InventoryAdjustment", **_tag_sync)

# ── Loyalty & Client Settings CRUD ──
_register_crud(app, "client-categories", ClientCategory, "ClientCategory", **_tag_sync)
_register_crud(app, "loyalty-transactions", LoyaltyTransaction, "LoyaltyTransaction", **_tag_sync)
_register_crud(app, "user-settings", UserSettings, "UserSettings", **_tag_sync)

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
# Fusion health-check endpoint
# ===========================================================================

register_fusion_health_routes(app)

# ── Fragment component registration ──
from fragments import register_fragments
register_fragments()


# ===========================================================================
# Entry point
# ===========================================================================


def main():
    """Start the POS Full Server.

    Entry point called by `if __name__ == "__main__":`.
    Handles --migrate flag for Django migration-based table creation.
    """
    args = _parse_args()

    if args.version:
        from about import __title_full__, __version__
        print(f"{__title_full__} v{__version__}")
        return

    if not _DJANGO_READY:
        logger.error("Django ORM bootstrap failed, cannot start")
        sys.exit(1)

    # Create/ensure database tables (migrations or schema_editor)
    _ensure_tables(args.migrate)

    # ── Ensure a default API key exists for development ──
    from middleware.apikey_scoped import ensure_default_api_key
    default_key = ensure_default_api_key()
    if default_key:
        logger.info("Default API key created (save this): %s", default_key)

    # ── Scheduled branch sync to POS Cloud ──
    from services.scheduler import create_scheduler
    sync_scheduler = create_scheduler(
        interval=args.sync_interval,
        enabled=not args.no_sync,
        node_id=args.sync_node_id,
    )

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("POS Full Server starting on %s:%d", args.host or HOST, args.port or PORT)
    logger.info("Database: %s", DB_PATH)
    logger.info("Django ORM: %s | Pydantic: %s", _DJANGO_READY, _PYDANTIC_READY)
    logger.info("Models loaded: %d Registry = %d total",
                len(_REGISTRY_MODELS), len(_ALL_MODELS))
    logger.info("=" * 60)

    # Log available routes for verification
    routes_logged = False
    logger.info("── Available API Endpoints ──")
    logger.info("  CRUD:   /products, /customers, /sales, /inventory, ...")
    logger.info("  Nodes:  GET/POST/DELETE /nodes, /nodes/register, /nodes/heartbeat")
    logger.info("  Config: GET/POST/DELETE /nodes/:node_id/config, /config/*")
    logger.info("  Sync:   GET /sync/status | POST /sync/trigger | POST /api/sync/push/:type")
    logger.info("  Auth:   GET/POST /auth/* (token management)")
    logger.info("  WS:     /ws/nodes (node events) | /ws/config (config events)")
    logger.info("  Info:   GET /, /health, /stats")
    logger.info("  Approvals: POST /approvals/:pk/approve|reject")
    logger.info("  Webhooks:  POST /webhooks/receive/:signal | GET /webhooks/receive")
    logger.info("─" * 60)

    # ── Start scheduled branch sync (daemon thread with own event loop) ──
    if sync_scheduler._enabled:
        import threading
        import asyncio as _asyncio

        async def _run_scheduler(sched):
            await sched.start()
            # Keep the event loop alive while scheduler runs
            while sched._running:
                await _asyncio.sleep(1)

        def _thread_target():
            loop = _asyncio.new_event_loop()
            _asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_run_scheduler(sync_scheduler))
            finally:
                loop.close()

        _sched_thread = threading.Thread(target=_thread_target, daemon=True, name="branch-sync-scheduler")
        _sched_thread.start()
        # Make scheduler stats available to route handlers
        from routes import state as _routes_state
        _routes_state.sync_scheduler = sync_scheduler

    # ── Start cloud WebSocket real-time sync client ──
    try:
        _start_cloud_ws_client()
    except Exception as _ws_exc:
        logger.warning("Cloud WebSocket sync client failed to start: %s", _ws_exc)

    logger.info(
        "Auto-sync: enabled=%s interval=%ds node_id=%s",
        sync_scheduler._enabled, sync_scheduler.interval, sync_scheduler.node_id,
    )

    app.start(host=args.host or HOST, port=args.port or PORT)


if __name__ == "__main__":
    main()
