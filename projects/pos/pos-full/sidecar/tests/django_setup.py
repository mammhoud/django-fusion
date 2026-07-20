"""
Standalone Django bootstrap for test suites.

Decouples tests from importing server.py at module level. Only bootstraps
Django ORM with the shared database and registers signal handlers — no
Robyn app creation, middleware, CRUD registration, or route wiring.

Usage:
    from tests.django_setup import _DJANGO_READY
    assert _DJANGO_READY, "Django ORM bootstrap failed"

    # Shared modules are already importable after this:
    from shared.models.audit import SignalEvent
    from shared.signals import fire_config_changed, ...
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Path setup — mirror server.py to make shared/ importable
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent  # tests/
_SIDECAR = _HERE.parent                   # sidecar/
_POS_FULL = _SIDECAR.parent               # pos-full/
_POS = _POS_FULL.parent                   # pos/  <-- shared module lives here

if str(_POS) not in sys.path:
    sys.path.insert(0, str(_POS))

# ---------------------------------------------------------------------------
# Django ORM bootstrap
# ---------------------------------------------------------------------------

_DJANGO_READY: bool = False

try:
    import django
    from django.conf import settings

    # Shared database with Rust backend (pos-full/restaurant.db)
    DB_PATH = _POS_FULL / "restaurant.db"

    if not settings.configured:
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
                "django.contrib.auth",
            ],
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            USE_TZ=True,
            SECRET_KEY=os.environ.get(
                "DJANGO_SECRET_KEY", "pos-full-server-dev-key"
            ),
        )
    django.setup()

    from django.db import connection

    # ── Import all shared models used by webhook tests ──
    from shared.models.audit import SignalEvent
    from shared.models.token import DeviceToken
    from shared.models.approval import SyncApproval

    # ── Import local registry models ──
    from models.node import Node, Heartbeat, NodeEvent
    from models.config import DeviceConfig, MasterDevice, CloudLink
    from models.sync import SyncLog

    # ── Create managed tables ──
    # NOTE: These are Django-managed tables (full_* prefix). When the
    # Rust DB exists at restaurant.db, these create_model() calls may
    # attempt writes against tables the Rust app owns. This is harmless
    # because (1) managed models use full_* table names distinct from
    # Rust posapp tables, and (2) any collision is caught by the
    # except (ProgrammingError, OperationalError) handler below.
    _REGISTRY_MODELS = [
        Node, Heartbeat, NodeEvent, SyncLog,
        DeviceConfig, MasterDevice, CloudLink,
        SyncApproval, DeviceToken, SignalEvent,
    ]
    existing_tables = []
    try:
        existing_tables = connection.introspection.table_names()
    except Exception:
        pass
    with connection.schema_editor() as schema_editor:
        for model in _REGISTRY_MODELS:
            if model._meta.db_table in existing_tables:
                continue
            try:
                schema_editor.create_model(model)
            except Exception:
                pass

    # ── Import signal handlers (side-effect: registers @receiver handlers) ──
    import shared.handlers.signal  # noqa: F401
    from shared.handlers.signal import WEBHOOK_URLS, _send_webhook

    # ── Import signal fire functions ──
    from shared.signals import (  # noqa: F401 — re-exported via __all__
        fire_config_changed,
        fire_device_status_changed,
        fire_config_synced,
        fire_master_device_changed,
        fire_cloud_link_changed,
    )

    _DJANGO_READY = True
    logger.info("Django ORM ready (db: %s)", DB_PATH)

except Exception as exc:
    logger.critical("Django bootstrap failed: %s", exc)
