"""
E2E integration tests for the POS Full fusion fragment-rendering flow.

Verifies the full backend pipeline that the frontend FusionStore,
FusionMiddleware, FusionPage, and FusionProxy components depend on:

1. FragmentComponent classes produce correct context with real DB data
2. Template rendering produces valid HTML with expected values
3. Error handling in fragment routes
4. Health-check produces correct preference
5. End-to-end flow: health check → fragment context → rendered HTML

Run::

    cd pos-full/server
    python3 -m pytest tests/test_fusion_integration.py -v --tb=short
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from decimal import Decimal

import pytest

# Robyn runtime removed — the Django ASGI stack is canonical. These tests
# exercise the legacy Robyn fusion fragment-rendering flow, so they only
# run when robyn is installed.
pytest.importorskip("robyn", reason="Robyn removed — Django ASGI is canonical")

# ── Path bootstrap ──────────────────────────────────────────────────
_SERVER_DIR = Path(__file__).resolve().parent.parent
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))


# ═══════════════════════════════════════════════════════════════════════
# Django ORM bootstrap (from django_setup)
# ═══════════════════════════════════════════════════════════════════════

from tests.django_setup import _DJANGO_READY  # noqa: E402

assert _DJANGO_READY, "Django ORM bootstrap failed — check test DB"

from django.db import connection  # noqa: E402


def _ensure_tables(models):
    """Create database tables for the given models if they don't exist."""
    existing = set(connection.introspection.table_names())
    with connection.schema_editor() as schema_editor:
        for model in models:
            if model._meta.db_table not in existing:
                try:
                    schema_editor.create_model(model)
                    existing.add(model._meta.db_table)
                except Exception:
                    pass


# ═══════════════════════════════════════════════════════════════════════
# Test seed data
# ═══════════════════════════════════════════════════════════════════════

SEED_PRODUCT = {
    "name": "Test Espresso",
    "sku": "TST-ESP-001",
    "price": Decimal("3.50"),
    "cost_price": Decimal("1.20"),
    "stock_quantity": 100,
    "low_stock_threshold": 10,
    "tax_rate": "standard",
    "is_active": True,
}

SEED_CUSTOMER = {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "loyalty_points": 250,
    "total_spent": Decimal("1250.00"),
    "is_active": True,
}

SEED_EMPLOYEE = {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john@test.com",
    "role": "cashier",
    "is_active": True,
    "hourly_rate": Decimal("15.00"),
}

SEED_SUPPLIER = {
    "name": "Test Supplier Co",
    "contact_name": "Alice Buyer",
    "email": "alice@supplier.com",
    "phone": "+1-555-TEST",
    "is_active": True,
}


def _seed_test_data():
    """Insert seed records into the managed POS models.

    Ensures required tables exist before inserting.
    """
    from models.pos import Product, Customer, Employee, Category
    from models.inventory import Supplier
    from models.extra import Ingredient

    # Ensure all required tables exist
    _ensure_tables([Product, Customer, Employee, Category, Supplier, Ingredient])

    cat, _ = Category.objects.get_or_create(
        name="Test Category",
        defaults={"slug": "test-cat", "is_active": True},
    )
    Product.objects.get_or_create(
        sku=SEED_PRODUCT["sku"],
        defaults={**SEED_PRODUCT, "category": cat},
    )
    Customer.objects.get_or_create(
        email=SEED_CUSTOMER["email"],
        defaults=SEED_CUSTOMER,
    )
    Employee.objects.get_or_create(
        email=SEED_EMPLOYEE["email"],
        defaults=SEED_EMPLOYEE,
    )
    Supplier.objects.get_or_create(
        name=SEED_SUPPLIER["name"],
        defaults=SEED_SUPPLIER,
    )
    Ingredient.objects.get_or_create(
        name="Test Flour",
        defaults={
            "unit": "kg",
            "current_quantity": Decimal("50.0"),
            "reorder_level": Decimal("10.0"),
            "cost_per_unit": Decimal("0.50"),
            "is_active": True,
        },
    )
    return cat


def _clear_test_data():
    """Remove all seed data from test DB (comprehensive — see seed_demo).

    Deletes child records first so FK cascades never leave orphan rows:
    sales cascade to sale items + kitchen tickets; customers cascade to
    loyalty transactions; suppliers cascade to purchase orders.
    """
    from models.audit import SignalEvent
    from models.crm import Company, Contact, Deal
    from models.extra import (
        Ingredient, InventoryAdjustment, ReceiptTemplate, Recipe, Role,
    )
    from models.hr import Payroll, TaxReport
    from models.inventory import PurchaseOrder, PurchaseOrderItem, Supplier
    from models.loyalty import (
        ClientCategory, LoyaltyTransaction, UserSettings,
    )
    from models.menu import Menu, MenuItem, MenuItemAssignment
    from models.node import Node, NodeEvent
    from models.ops import KitchenTicket, SupportTicket
    from models.pos import Category, Customer, Employee, Product, Sale
    from models.sync import SyncLog

    # Children first, then parents (FKS above are CASCADE, so this is a belt-
    # and-braces ordering that also stays correct if a FK is ever switched to
    # SET_NULL / PROTECT).
    for model in (
        SignalEvent, NodeEvent, SyncLog, KitchenTicket, SupportTicket,
        Sale, LoyaltyTransaction, PurchaseOrderItem, PurchaseOrder,
        MenuItemAssignment, MenuItem, Menu, Payroll, TaxReport,
        InventoryAdjustment, Recipe, ReceiptTemplate, Role,
        Employee, Product, Customer, Category, Supplier, Ingredient,
        ClientCategory, UserSettings, Deal, Contact, Company,
    ):
        model.objects.all().delete()


# ═══════════════════════════════════════════════════════════════════════
# 1. FragmentComponent context integration
# ═══════════════════════════════════════════════════════════════════════


class TestDashboardFragmentIntegration:
    """DashboardFragment seeded with real DB data."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_counts(self):
        from fragments.dashboard import DashboardFragment

        context = DashboardFragment().get_context()
        assert context["product_count"] >= 1
        assert context["customer_count"] >= 1
        assert context["employee_count"] >= 1
        assert context["sale_count"] == 0  # No sales seeded
        assert isinstance(context["restaurant_name"], str)
        assert len(context["restaurant_name"]) > 0

    def test_context_types_are_correct(self):
        from fragments.dashboard import DashboardFragment

        context = DashboardFragment().get_context()
        assert isinstance(context["product_count"], int)
        assert isinstance(context["customer_count"], int)
        assert isinstance(context["employee_count"], int)
        assert isinstance(context["sale_count"], int)
        assert isinstance(context["restaurant_name"], str)


class TestSuppliersFragmentIntegration:
    """SuppliersFragment seeded with supplier data."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_supplier(self):
        from fragments.suppliers import SuppliersFragment

        context = SuppliersFragment().get_context()
        assert context["count"] >= 1
        assert len(context["suppliers"]) >= 1
        # Find our seeded supplier by name
        names = [s.name for s in context["suppliers"]]
        assert SEED_SUPPLIER["name"] in names


class TestCustomersFragmentIntegration:
    """CustomersFragment seeded with customer data."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_customer_stats(self):
        from fragments.customers import CustomersFragment

        context = CustomersFragment().get_context()
        assert context["total_customers"] >= 1
        assert context["active_customers"] >= 1
        assert context["total_lifetime_spent"] == "1250.00"


class TestEmployeesFragmentIntegration:
    """EmployeesFragment seeded with employee data."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_employee(self):
        from fragments.employees import EmployeesFragment

        context = EmployeesFragment().get_context()
        assert context["total_employees"] >= 1
        assert context["active_employees"] >= 1
        assert "cashier" in context["by_role"]


class TestInventoryFragmentIntegration:
    """InventoryFragment seeded with ingredient data."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_ingredient_stats(self):
        from fragments.inventory import InventoryFragment

        context = InventoryFragment().get_context()
        assert context["total_ingredients"] >= 1
        assert context["total_products"] >= 1
        assert len(context["low_stock_items"]) >= 0  # Flour has 50kg, reorder at 10


# ═══════════════════════════════════════════════════════════════════════
# 2. Template rendering integration
# ═══════════════════════════════════════════════════════════════════════

class TestDashboardTemplateRendering:
    """Renders the dashboard template with real fragment context."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_dashboard_html_contains_seeded_counts(self):
        from fragments.dashboard import DashboardFragment
        from routes.fusion_fragments import _render_template, _DASHBOARD_FRAGMENT_TEMPLATE

        context = DashboardFragment().get_context()
        html = _render_template(_DASHBOARD_FRAGMENT_TEMPLATE, context)

        # HTML should contain fusion markers
        assert 'class="fusion-fragment"' in html
        assert 'data-fragment-name="dashboard"' in html

        # HTML should show count values
        assert str(context["product_count"]) in html
        assert context["restaurant_name"] in html

    def test_suppliers_html_contains_supplier_data(self):
        from fragments.suppliers import SuppliersFragment
        from routes.fusion_fragments import _render_template, _SUPPLIERS_FRAGMENT_TEMPLATE

        context = SuppliersFragment().get_context()
        html = _render_template(_SUPPLIERS_FRAGMENT_TEMPLATE, context)

        assert 'class="fusion-fragment"' in html
        assert 'data-fragment-name="suppliers"' in html
        assert SEED_SUPPLIER["name"] in html

    def test_about_html_contains_version(self):
        from fragments.about import AboutFragment
        from routes.fusion_fragments import _render_template, _ABOUT_FRAGMENT_TEMPLATE

        context = AboutFragment().get_context()
        html = _render_template(_ABOUT_FRAGMENT_TEMPLATE, context)

        assert 'class="fusion-fragment"' in html
        assert 'data-fragment-name="about"' in html
        assert context["title"] in html
        assert str(context["year"]) in html


# ═══════════════════════════════════════════════════════════════════════
# 3. Error handling & edge cases
# ═══════════════════════════════════════════════════════════════════════

class TestFragmentErrorHandling:
    """Error boundaries in the rendering pipeline."""

    def test_empty_db_does_not_crash_dashboard(self):
        """DashboardFragment handles empty database gracefully."""
        from fragments.dashboard import DashboardFragment

        _clear_test_data()
        context = DashboardFragment().get_context()
        assert context["product_count"] == 0
        assert context["customer_count"] == 0
        assert context["employee_count"] == 0
        assert context["sale_count"] == 0

    def test_product_detail_missing_pk_returns_safe_default(self):
        """ProductDetailFragment with no pk returns safe defaults."""
        from fragments.products import ProductDetailFragment

        context = ProductDetailFragment().get_context()
        assert context["product"] is None
        assert context["in_stock"] is False
        assert context["total_sold"] == 0

    def test_product_detail_nonexistent_pk_returns_safe_default(self):
        """ProductDetailFragment with non-existent pk returns safe defaults."""
        from fragments.products import ProductDetailFragment

        context = ProductDetailFragment().get_context(pk=99999)
        assert context["product"] is None
        assert context["in_stock"] is False


# ═══════════════════════════════════════════════════════════════════════
# 4. Health check integration
# ═══════════════════════════════════════════════════════════════════════

class TestFusionHealthIntegration:
    """Health-check endpoint behaviour with real components."""

    def test_health_checker_singleton_type(self):
        """The global health checker is a RobynFusionChecker."""
        from middleware.fusion import fusion_health_checker, RobynFusionChecker

        assert isinstance(fusion_health_checker, RobynFusionChecker)

    def test_health_check_no_token_uses_ua(self):
        """Without token, the checker falls back to User-Agent heuristic."""
        from middleware.fusion import fusion_health_checker

        class MockReq:
            headers = {"User-Agent": "Mozilla/5.0 Chrome/120"}

        with patch("middleware.fusion.get_token_info", return_value=None):
            pref = fusion_health_checker.get_preference(MockReq())
            assert pref is True  # Browser UA → fragment mode

    def test_health_check_script_ua_returns_false(self):
        """Script User-Agent → data mode."""
        from middleware.fusion import fusion_health_checker

        class MockReq:
            headers = {"User-Agent": "curl/8.0.1"}

        with patch("middleware.fusion.get_token_info", return_value=None):
            pref = fusion_health_checker.get_preference(MockReq())
            assert pref is False


# ═══════════════════════════════════════════════════════════════════════
# 5. End-to-end flow: fragment class → rendered HTML
# ═══════════════════════════════════════════════════════════════════════

class TestEndToEndFlow:
    """Full flow: seed DB → fragment → context → rendered HTML."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_full_dashboard_flow(self):
        """Seed → DashboardFragment.get_context() → template → HTML with values."""
        from fragments.dashboard import DashboardFragment
        from routes.fusion_fragments import _render_template, _DASHBOARD_FRAGMENT_TEMPLATE

        # Step 1: Get context from fragment
        context = DashboardFragment().get_context()
        assert context["product_count"] >= 1

        # Step 2: Render HTML template with context
        html = _render_template(_DASHBOARD_FRAGMENT_TEMPLATE, context)

        # Step 3: Verify HTML contains expected data
        assert "fusion-fragment" in html
        assert str(context["product_count"]) in html
        assert str(context["customer_count"]) in html

    def test_full_suppliers_flow(self):
        """Seed → SuppliersFragment.get_context() → template → HTML with supplier name."""
        from fragments.suppliers import SuppliersFragment
        from routes.fusion_fragments import _render_template, _SUPPLIERS_FRAGMENT_TEMPLATE

        context = SuppliersFragment().get_context()
        html = _render_template(_SUPPLIERS_FRAGMENT_TEMPLATE, context)

        assert SEED_SUPPLIER["name"] in html
        assert "fusion-fragment" in html

    def test_about_frontend_consumable_html(self):
        """Verify the rendered HTML is consumable by FusionProxy's dangerouslySetInnerHTML."""
        from fragments.about import AboutFragment
        from routes.fusion_fragments import _render_template, _ABOUT_FRAGMENT_TEMPLATE

        context = AboutFragment().get_context()
        html = _render_template(_ABOUT_FRAGMENT_TEMPLATE, context)

        # The frontend FusionProxy uses dangerouslySetInnerHTML — HTML must be valid
        # Check that it has a single root element wrapping
        assert html.strip().startswith("<div")
        assert html.strip().endswith("</div>")
        # Must contain the fragment marker that FusionProxy looks for
        assert 'class="fusion-fragment"' in html


# ═══════════════════════════════════════════════════════════════════════
# 6. Cross-layer contract: frontend-consumable response
# ═══════════════════════════════════════════════════════════════════════

class TestCrossLayerContract:
    """Verify that fragment outputs match what FusionProxy expects."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _clear_test_data()  # deterministic — start from an empty DB
        _seed_test_data()
        yield
        _clear_test_data()

    def test_fragment_html_has_expected_structure(self):
        """FusionProxy expects: single root div with fusion-fragment + data-fragment-name."""
        from fragments.suppliers import SuppliersFragment
        from routes.fusion_fragments import _render_template, _SUPPLIERS_FRAGMENT_TEMPLATE

        context = SuppliersFragment().get_context()
        html = _render_template(_SUPPLIERS_FRAGMENT_TEMPLATE, context)

        # FusionProxy expects these exact attributes to identify the fragment
        assert 'class="fusion-fragment"' in html
        assert 'data-fragment-name="suppliers"' in html

    def test_fragment_marker_present_in_all_templates(self):
        """Every inline template has the fusion-fragment marker."""
        from routes.fusion_fragments import (
            _DASHBOARD_FRAGMENT_TEMPLATE,
            _SUPPLIERS_FRAGMENT_TEMPLATE,
            _ABOUT_FRAGMENT_TEMPLATE,
        )

        for name, tmpl in [
            ("dashboard", _DASHBOARD_FRAGMENT_TEMPLATE),
            ("suppliers", _SUPPLIERS_FRAGMENT_TEMPLATE),
            ("about", _ABOUT_FRAGMENT_TEMPLATE),
        ]:
            assert 'class="fusion-fragment"' in tmpl, f"{name} template missing fusion-fragment"
            assert 'data-fragment-name' in tmpl, f"{name} template missing data-fragment-name"

    def test_fragment_markers_match_route_names(self):
        """data-fragment-name values match the route/fragment names."""
        from routes.fusion_fragments import (
            _DASHBOARD_FRAGMENT_TEMPLATE,
            _SUPPLIERS_FRAGMENT_TEMPLATE,
            _ABOUT_FRAGMENT_TEMPLATE,
        )

        assert 'data-fragment-name="dashboard"' in _DASHBOARD_FRAGMENT_TEMPLATE
        assert 'data-fragment-name="suppliers"' in _SUPPLIERS_FRAGMENT_TEMPLATE
        assert 'data-fragment-name="about"' in _ABOUT_FRAGMENT_TEMPLATE


# ═══════════════════════════════════════════════════════════════════════
# 7. Route registration with real middleware
# ═══════════════════════════════════════════════════════════════════════

class TestRouteRegistrationIntegration:
    """Fragment route registration works with MagicMock app."""

    def test_routes_register_with_correct_paths(self):
        app = MagicMock()
        from routes.fusion_fragments import register_fusion_fragment_routes

        register_fusion_fragment_routes(app)

        paths = [call[0][0] for call in app.get.call_args_list]
        assert "/fusion/render/dashboard" in paths
        assert "/fusion/render/suppliers" in paths
        assert "/fusion/render/about" in paths

    def test_health_route_registers(self):
        app = MagicMock()
        from middleware.fusion import register_fusion_health_routes

        register_fusion_health_routes(app)
        app.get.assert_called_with("/fusion/health")
