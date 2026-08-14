"""
Pytest fixtures for real-data cross-ORM tests.

Provides a `rust_db` fixture that connects to an actual Rust-built restaurant.db.
If the DB doesn't exist or lacks the expected Rust tables, tests are skipped
with a clear message (not silently passed).

Usage:
    class TestRealData:
        def test_something(self, rust_db):
            products = rust_db.posapp.Product.objects.all()
            assert products.count() > 0
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)

# ── Expected Rust table set (must match Diesel schema) ──

REQUIRED_RUST_TABLES = frozenset({
    "products", "categories", "customers", "sales", "sale_items",
    "ingredients", "inventory_transactions", "suppliers", "purchase_orders",
    "settings", "employees",
})


def _find_rust_db() -> Path | None:
    """Locate the Rust-built restaurant.db."""
    candidates = [
        Path(os.environ.get("RUST_DB_PATH", "")),
        Path(__file__).parent.parent.parent / "restaurant.db",  # pos-full/restaurant.db
    ]
    for p in candidates:
        if p.is_file():
            return p.resolve()
    return None


def _has_rust_tables(db_path: Path) -> bool:
    """Check if the SQLite file has the expected Rust-managed tables."""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        conn.close()
        return REQUIRED_RUST_TABLES.issubset(tables)
    except Exception:
        return False


class RustDB:
    """Wrapper for cross-ORM reads on a real Rust-built database.

    Provides lazy access to the Django posapp models (managed=False)
    for read-only queries against the Rust-managed tables.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._posapp = None

    @property
    def posapp(self):
        """Lazy import of posapp models."""
        if self._posapp is None:
            from models import posapp as _posapp
            self._posapp = _posapp
        return self._posapp

    def raw_query(self, sql: str, params: tuple = ()) -> list[tuple]:
        """Run a raw SQL query directly against the Rust DB."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        rows = [tuple(r) for r in conn.execute(sql, params)]
        conn.close()
        return rows

    def table_names(self) -> set[str]:
        """Set of all table names in the Rust DB."""
        conn = sqlite3.connect(str(self.db_path))
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        conn.close()
        return tables

    def row_count(self, table: str) -> int:
        """Count rows in a given table."""
        conn = sqlite3.connect(str(self.db_path))
        count = conn.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()[0]
        conn.close()
        return count


# ── Fixture ──


@pytest.fixture(scope="class")
def rust_db() -> RustDB:
    """Fixture that provides a RustDB wrapper for real cross-ORM tests.

    Requires a Rust-built restaurant.db at pos-full/restaurant.db
    (or set RUST_DB_PATH env var). The DB must contain the core
    Rust-managed tables (products, categories, etc.).

    If the DB doesn't exist, pytest.skip() is called with a clear
    message explaining what's needed.
    """
    db_path = _find_rust_db()

    if db_path is None:
        pytest.skip(
            "No Rust-built restaurant.db found. "
            "Build the Rust/Tauri app first (creates pos-full/restaurant.db), "
            "or set RUST_DB_PATH=/path/to/restaurant.db. "
            "Expected location: projects/formints/formint-pro/restaurant.db"
        )

    if not _has_rust_tables(db_path):
        pytest.skip(
            f"Rust DB at {db_path} exists but lacks required tables. "
            f"Expected at least: {sorted(REQUIRED_RUST_TABLES)}. "
            "Rebuild the Rust app with migrations applied."
        )

    # Configure Django to use this DB (read-only for Rust tables)
    # django_setup.py may already be loaded; don't reconfigure if already set
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(db_path),
                }
            },
            INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            USE_TZ=True,
            SECRET_KEY="rust-db-test-key",
        )
        import django
        django.setup()
    else:
        # Verify the configured DB matches what we found
        current = settings.DATABASES["default"]["NAME"]
        if str(db_path) != str(Path(current)):
            pytest.skip(
                f"Django already configured with {current}, "
                f"but Rust DB is at {db_path}. Run this test suite in isolation."
            )

    logger.info("Rust DB ready: %s (%d tables)", db_path, len(RustDB(db_path).table_names()))
    return RustDB(db_path)
