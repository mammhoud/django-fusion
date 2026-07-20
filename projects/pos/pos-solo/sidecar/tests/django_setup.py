"""
Standalone Django bootstrap for POS Solo test suites.

Bootstraps Django ORM with an in-memory SQLite database and imports all
15 unified models. Decouples tests from importing server.py at module level.

Usage:
    from tests.django_setup import (
        _DJANGO_READY, Category, Product, Customer, Sale, SaleItem,
        InventoryTransaction, Employee, MenuItem, Menu, MenuItemAssignment,
        Node, Heartbeat, NodeEvent, SyncLog,
    )
    assert _DJANGO_READY, "Django ORM bootstrap failed"
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

_DJANGO_READY: bool = False

# Clear any pre-existing Django settings to avoid conflicts
os.environ.pop("DJANGO_SETTINGS_MODULE", None)

try:
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=["django.contrib.contenttypes"],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY="test-secret-key",
    )
    django.setup()

    from django.db import connection, ProgrammingError

    # Import all 15 unified models
    from models.pos import (
        Category, Product, Customer, Sale, SaleItem,
        InventoryTransaction, Employee,
    )
    from models.menu import MenuItem, Menu, MenuItemAssignment
    from models.node import Node, Heartbeat, NodeEvent
    from models.sync import SyncLog

    _ALL_MODELS = [
        Category, Customer, Employee, Heartbeat, InventoryTransaction,
        Menu, MenuItem, MenuItemAssignment, Node, NodeEvent,
        Product, Sale, SaleItem, SyncLog,
    ]

    with connection.schema_editor() as se:
        for m in _ALL_MODELS:
            try:
                se.create_model(m)
            except ProgrammingError:
                pass

    _DJANGO_READY = True
    logger.info("Django ORM ready (in-memory, %d models)", len(_ALL_MODELS))

except Exception as exc:
    logger.critical("Django bootstrap failed: %s", exc)
