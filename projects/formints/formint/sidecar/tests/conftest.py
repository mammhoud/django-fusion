"""
Pytest configuration for pos-solo tests.

Provides shared fixtures, factory fixtures for Django models, mock
request/response helpers for handler testing, and custom markers.

The Django bootstrap is unified here (NOT per test file):

  * One ``settings.configure()`` at conftest import time — before any test
    module is imported — so the per-file ``settings.configure`` blocks in
    test_*.py all become no-ops (they guard on ``if not settings.configured``).
  * A single **file-backed** SQLite database (session temp file) instead of
    ``:memory:``. ``django.test.TestCase.tearDownClass()`` closes every
    initialized connection at the end of each test class (Django
    testcases.py); for ``:memory:`` that destroys the shared database and
    breaks every later test file in the same process. A file-backed DB
    survives connection closes, so the combined suite runs green in one pass.
  * A module-scoped autouse fixture wipes all tables before each test module,
    preserving the old per-file ``:memory:`` isolation semantics.

Usage:
    def test_node_creation(node_factory):
        node = node_factory(node_id="test-01")
        assert node.node_id == "test-01"

    def test_handler(mock_request, mock_response):
        req = mock_request(method="GET", headers={"Authorization": "Bearer xyz"})
        data = await req.json_body()
"""

from __future__ import annotations

import json as _json
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from typing import Any

import pytest

# ── Ensure sidecar root is on sys.path ──────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_THIS_DIR)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

# Make fixtures.py available (rust_db fixture)
pytest_plugins = ["tests.fixtures"]


# ══════════════════════════════════════════════════════════════════════════
# Unified Django bootstrap — runs ONCE at conftest import, before pytest
# imports any test module. All per-file settings.configure() blocks in the
# test_*.py modules are guarded by `if not settings.configured` and become
# no-ops once this has run.
# ══════════════════════════════════════════════════════════════════════════

_TEST_DB_DIR: str | None = None


def _create_all_tables() -> None:
    """Create tables for every registered pos_full model.

    Only pos_full models are created — matching the original conftest/
    django_setup behaviour. contenttypes/auth tables are left alone: they
    carry auto-created M2M through tables whose inline unique indexes
    conflict when created manually (``index ... already exists``), and no
    test in this suite queries them.

    Idempotent: tables that already exist are skipped.
    """
    import logging

    from django.apps import apps
    from django.db import connection

    logger = logging.getLogger(__name__)
    models_to_create = list(apps.all_models.get("pos_full", {}).values())

    existing = set()
    try:
        existing = set(connection.introspection.table_names())
    except Exception:
        pass

    with connection.schema_editor() as schema_editor:
        for model in models_to_create:
            if model._meta.db_table in existing:
                continue
            try:
                schema_editor.create_model(model)
            except Exception as exc:  # noqa: BLE001 - bootstrap guard
                logger.warning(
                    "Could not create table %r: %s", model._meta.db_table, exc
                )


def _bootstrap_django() -> None:
    """Configure Django once with a shared file-backed test database."""
    global _TEST_DB_DIR

    os.environ.pop("DJANGO_SETTINGS_MODULE", None)

    from django.conf import settings

    if settings.configured:
        return  # another module already bootstrapped — nothing to do

    _TEST_DB_DIR = tempfile.mkdtemp(prefix="pos-sidecar-pytest-")
    _test_db_path = os.path.join(_TEST_DB_DIR, "test.db")

    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": _test_db_path,
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            # POS Full app — required so pos_full models participate in
            # apps.get_models()/relation graph (reverse FKs, cascading
            # deletes, related_objects).
            "models.PosFullConfig",
            # django-bolt tests (test_bolt_api.py) require the app installed.
            "django_bolt",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                    ],
                },
            },
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY="test-key-conftest",
    )

    import django

    django.setup()

    # Register ALL pos_full models (string FK resolution + table creation).
    import models.models  # noqa: F401

    _create_all_tables()


_bootstrap_django()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Remove the shared temp test database at session end."""
    global _TEST_DB_DIR
    if _TEST_DB_DIR:
        shutil.rmtree(_TEST_DB_DIR, ignore_errors=True)
        _TEST_DB_DIR = None


# ══════════════════════════════════════════════════════════════════════════
# Django session fixture — dependency marker for factory fixtures
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def django_bootstrap() -> None:
    """Session-scoped Django bootstrap.

    Configuration and table creation already happened at conftest import
    time; this fixture exists so factory fixtures can request it to
    guarantee ordering. Tables are wiped per-module by the autouse
    ``_isolate_db_per_module`` fixture.
    """
    return None


@pytest.fixture(scope="module", autouse=True)
def _isolate_db_per_module(django_bootstrap) -> None:
    """Wipe all tables before each test module.

    Replicates the old per-file ``:memory:`` isolation: every test module
    (file) starts with a clean database, while the shared file-backed DB
    survives connection closes between modules.
    """
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF")
        tables = connection.introspection.table_names()
        for table in tables:
            try:
                cursor.execute(f'DELETE FROM "{table}"')
            except Exception:
                pass  # table may not exist in this bootstrap
        try:
            cursor.execute("DELETE FROM sqlite_sequence")
        except Exception:
            pass  # no AUTOINCREMENT tables / not supported
        cursor.execute("PRAGMA foreign_keys = ON")
    yield


# ══════════════════════════════════════════════════════════════════════════
# Custom pytest markers
# ══════════════════════════════════════════════════════════════════════════

def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers to suppress pytest warnings."""
    config.addinivalue_line("markers", "unit: Test that does not require a database.")
    config.addinivalue_line("markers", "integration: Test that requires a database or external service.")
    config.addinivalue_line("markers", "slow: Test that takes longer than a few seconds.")
    config.addinivalue_line("markers", "rust_db: Test that requires a real Rust-built restaurant.db.")


# ══════════════════════════════════════════════════════════════════════════
# Async helper
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def async_to_sync():
    """Wrap an async function so it can be called from sync test code.

    Usage:
        result = async_to_sync(some_async_fn)(arg1, arg2)
    """
    from asgiref.sync import async_to_sync as _ats
    return lambda fn, *a, **kw: _ats(fn)(*a, **kw)


# ══════════════════════════════════════════════════════════════════════════
# Mock request / response helpers
# ══════════════════════════════════════════════════════════════════════════

class MockResponse:
    """Captures status_code and body for test assertions.

    Usage:
        resp = MockResponse()
        await handler(request, resp)
        assert resp.status_code == 200
        data = resp.json()
    """

    def __init__(self):
        self.status_code = 200
        self._body = ""
        self._headers: dict[str, str] = {}

    def set_status(self, code: int) -> None:
        self.status_code = code

    def set_header(self, key: str, value: str) -> None:
        self._headers[key] = value

    async def respond(self, body: str | bytes, status_code: int | None = None) -> None:
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        self._body = body
        if status_code is not None:
            self.status_code = status_code

    def json(self) -> Any:
        return _json.loads(self._body)

    @property
    def body(self) -> str:
        return self._body


@pytest.fixture
def mock_response():
    """Return a MockResponse factory.

    Usage:
        resp = mock_response()
        await handler(req, resp)
        assert resp.status_code == 200
        data = resp.json()
    """
    return MockResponse


class MockRequest:
    """Simulates a Request for testing handlers in isolation."""

    def __init__(
        self,
        method: str = "GET",
        body: str = "",
        headers: dict[str, str] | None = None,
        query: dict[str, str] | None = None,
        path: str = "/",
    ):
        self.method = method
        self._body = body
        self.headers = headers or {}
        self.query_params = query or {}
        self.path = path

    def json_body(self) -> dict | list:
        return _json.loads(self._body) if self._body else {}

    def text_body(self) -> str:
        return self._body


@pytest.fixture
def mock_request():
    """Return a MockRequest factory.

    Usage:
        req = mock_request(method="POST", body='{"key": "val"}')
    """
    return MockRequest


# ══════════════════════════════════════════════════════════════════════════
# Model factory fixtures
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def node_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Node model instances with sensible defaults.

    Usage:
        node = node_factory(node_id="my-node", status="online")
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.node import Node
        defaults = {
            "node_id": kwargs.pop("node_id", f"test-node-{_counter[0]}"),
            "hostname": f"host-{_counter[0]}",
            "node_type": "pos-solo",
            "version": "1.0.0",
            "status": "online",
            "product_count": 0,
            "transaction_count": 0,
            "customer_count": 0,
        }
        defaults.update(kwargs)
        return Node.objects.create(**defaults)

    return _create


@pytest.fixture
def product_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Product model instances.

    Usage:
        product = product_factory(name="Espresso", price=3.50)
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.pos import Product
        defaults = {
            "name": kwargs.pop("name", f"Product-{_counter[0]}"),
            "price": kwargs.pop("price", 9.99),
            "stock_quantity": 100,
            "sku": kwargs.pop("sku", None),  # None = model default (blank+null)
            "is_active": True,
            "category": None,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)

    return _create


@pytest.fixture
def customer_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Customer model instances."""
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.pos import Customer
        defaults = {
            "first_name": kwargs.pop("first_name", f"Customer-{_counter[0]}"),
            "last_name": kwargs.pop("last_name", "Test"),
            "email": f"customer{_counter[0]}@test.com",
            "phone": f"555-{_counter[0]:04d}",
            "is_active": True,
        }
        defaults.update(kwargs)
        return Customer.objects.create(**defaults)

    return _create


@pytest.fixture
def sale_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Sale model instances.

    Requires a customer_factory or explicit customer= kwarg.
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.pos import Sale, Customer
        if "customer" not in kwargs:
            kwargs["customer"] = Customer.objects.create(
                first_name=f"SaleCustomer-{_counter[0]}",
                last_name="Test",
                email=f"salecust{_counter[0]}@test.com",
            )
        defaults = {
            "subtotal": kwargs.pop("subtotal", 19.99),
            "total": kwargs.pop("total", 23.99),
            "tax_amount": 2.00,
            "status": "completed",
            "payment_method": "cash",
        }
        defaults.update(kwargs)
        return Sale.objects.create(**defaults)

    return _create


@pytest.fixture
def employee_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Employee model instances."""
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.pos import Employee
        defaults = {
            "first_name": kwargs.pop("first_name", f"Emp-{_counter[0]}"),
            "last_name": kwargs.pop("last_name", "Test"),
            "email": f"emp{_counter[0]}@test.com",
            "role": "cashier",
            "pin_code": "1234",
            "is_active": True,
            "hourly_rate": 15.00,
        }
        defaults.update(kwargs)
        return Employee.objects.create(**defaults)

    return _create


@pytest.fixture
def sale_item_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for SaleItem model instances.

    Requires a ``sale_factory``/``sale=`` and ``product_factory``/``product=`` kwarg.
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.pos import SaleItem, Product, Sale, Customer
        if "sale" not in kwargs:
            kwargs["sale"] = Sale.objects.create(
                customer=Customer.objects.create(
                    first_name=f"SI-Cust-{_counter[0]}", last_name="T",
                    email=f"sic{_counter[0]}@t.com",
                ),
                subtotal=9.99, total=11.99, tax_amount=2.00,
            )
        if "product" not in kwargs:
            kwargs["product"] = Product.objects.create(
                name=f"SI-Product-{_counter[0]}", price=5.99,
            )
        defaults = {
            "product_name": kwargs.pop("product_name", f"Item-{_counter[0]}"),
            "quantity": kwargs.pop("quantity", 1),
            "unit_price": kwargs.pop("unit_price", 5.99),
            "line_total": kwargs.pop("line_total", 5.99),
        }
        defaults.update(kwargs)
        return SaleItem.objects.create(**defaults)

    return _create


@pytest.fixture
def inventory_transaction_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for InventoryTransaction model instances.

    Requires a ``product_factory`` or explicit ``product=`` kwarg.
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.pos import InventoryTransaction, Product
        if "product" not in kwargs:
            kwargs["product"] = Product.objects.create(
                name=f"InvTxnProduct-{_counter[0]}", price=4.99,
            )
        defaults = {
            "transaction_type": kwargs.pop("transaction_type", "in"),
            "quantity": kwargs.pop("quantity", 10),
            "notes": "Test transaction",
            "inventory_id": "main",
        }
        defaults.update(kwargs)
        return InventoryTransaction.objects.create(**defaults)

    return _create


@pytest.fixture
def ingredient_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Ingredient model instances."""
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.extra import Ingredient
        defaults = {
            "name": kwargs.pop("name", f"Ingredient-{_counter[0]}"),
            "unit": "kg",
            "current_quantity": 10.0,
            "cost_per_unit": 5.00,
            "is_active": True,
        }
        defaults.update(kwargs)
        return Ingredient.objects.create(**defaults)

    return _create


@pytest.fixture
def role_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Role model instances. Name is unique=True so each
    factory call uses a random suffix to avoid cross-test collisions.
    """
    import uuid as _uuid

    def _create(**kwargs) -> Any:
        from models.extra import Role
        uid = _uuid.uuid4().hex[:6]
        defaults = {
            "name": kwargs.pop("name", f"Role-{uid}"),
            "description": "Auto-generated test role",
            "permissions": {"can_manage_products": True},
            "is_active": True,
        }
        defaults.update(kwargs)
        return Role.objects.create(**defaults)

    return _create


@pytest.fixture
def category_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Category model instances. Slug is unique=True so each
    factory call uses a random suffix to avoid cross-test collisions.
    """
    import uuid as _uuid

    def _create(**kwargs) -> Any:
        from models.pos import Category
        uid = _uuid.uuid4().hex[:6]
        defaults = {
            "name": kwargs.pop("name", f"Category-{uid}"),
            "slug": kwargs.pop("slug", f"cat-{uid}"),
            "is_active": True,
            "display_order": 0,
        }
        defaults.update(kwargs)
        return Category.objects.create(**defaults)

    return _create


@pytest.fixture
def sync_log_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for SyncLog model instances."""
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.sync import SyncLog
        defaults = {
            "node_id": kwargs.pop("node_id", f"node-{_counter[0]}"),
            "entity_type": "product",
            "direction": "push",
            "status": "success",
        }
        defaults.update(kwargs)
        return SyncLog.objects.create(**defaults)

    return _create


@pytest.fixture
def recipe_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for Recipe model instances.

    Requires a ``product_factory`` or explicit ``product=`` kwarg.
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.extra import Recipe
        from models.pos import Product
        if "product" not in kwargs:
            kwargs["product"] = Product.objects.create(
                name=f"RecipeProduct-{_counter[0]}", price=5.99,
            )
        defaults = {
            "name": kwargs.pop("name", f"Recipe-{_counter[0]}"),
            "instructions": "Mix and serve.",
            "yield_quantity": 1,
            "is_active": True,
        }
        defaults.update(kwargs)
        return Recipe.objects.create(**defaults)

    return _create


@pytest.fixture
def receipt_template_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for ReceiptTemplate model instances. Name is unique=True
    so each factory call uses a random suffix.
    """
    import uuid as _uuid

    def _create(**kwargs) -> Any:
        from models.extra import ReceiptTemplate
        uid = _uuid.uuid4().hex[:6]
        defaults = {
            "name": kwargs.pop("name", f"Template-{uid}"),
            "description": "Default receipt layout",
            "template_html": "<h1>{{restaurant_name}}</h1>",
            "is_default": False,
            "is_active": True,
        }
        defaults.update(kwargs)
        return ReceiptTemplate.objects.create(**defaults)

    return _create


@pytest.fixture
def inventory_adjustment_factory(django_bootstrap) -> Callable[..., Any]:
    """Factory for InventoryAdjustment model instances.

    Requires an ``ingredient_factory`` or explicit ``ingredient=`` kwarg.
    The custom ``save()`` method auto-populates ``previous_quantity``
    from the ingredient and updates ``current_quantity``.
    """
    _counter = [0]

    def _create(**kwargs) -> Any:
        _counter[0] += 1
        from models.extra import InventoryAdjustment, Ingredient
        if "ingredient" not in kwargs:
            kwargs["ingredient"] = Ingredient.objects.create(
                name=f"AdjIngredient-{_counter[0]}", unit="kg",
                current_quantity=50.0,
            )
        defaults = {
            "quantity": kwargs.pop("quantity", 5),
            "adjustment_type": "addition",
            "reason": "correction",
            "notes": "Test adjustment",
        }
        defaults.update(kwargs)
        return InventoryAdjustment.objects.create(**defaults)

    return _create
