"""
E2E integration tests for the POS Solo fusion fragment-rendering flow.

Mirrors ``pos-full/sidecar/tests/test_fusion_integration.py`` but adapted
for the solo's single-restaurant database and standalone operation.

Verifies:
1. FragmentComponent classes produce correct context with real DB data
2. Template rendering produces valid HTML with expected values
3. Error handling in fragment routes
4. Health-check produces correct preference
5. End-to-end flow: health check → fragment context → rendered HTML

Run::

    cd pos-solo/sidecar
    python3 -m pytest tests/test_fusion_integration.py -v --tb=short
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from decimal import Decimal

import pytest

# ── Path bootstrap ──────────────────────────────────────────────────
_SIDECAR_DIR = Path(__file__).resolve().parent.parent
if str(_SIDECAR_DIR) not in sys.path:
    sys.path.insert(0, str(_SIDECAR_DIR))


# ═══════════════════════════════════════════════════════════════════════
# Django ORM bootstrap
# ═══════════════════════════════════════════════════════════════════════

from tests.django_setup import _DJANGO_READY  # noqa: E402

assert _DJANGO_READY, "Django ORM bootstrap failed"

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
    "name": "Solo Latte",
    "sku": "SOLO-LAT-001",
    "price": Decimal("4.50"),
    "cost_price": Decimal("1.80"),
    "stock_quantity": 50,
    "low_stock_threshold": 5,
    "tax_rate": "standard",
    "is_active": True,
}

SEED_CUSTOMER = {
    "first_name": "Bob",
    "last_name": "Test",
    "email": "bob@solotest.com",
    "loyalty_points": 100,
    "total_spent": Decimal("500.00"),
    "is_active": True,
}

SEED_EMPLOYEE = {
    "first_name": "Alice",
    "last_name": "Worker",
    "email": "alice@solotest.com",
    "role": "server",
    "is_active": True,
    "hourly_rate": Decimal("14.00"),
}

SEED_SUPPLIER = {
    "name": "Solo Supply Co",
    "contact_name": "Bob Vendor",
    "email": "bob@solo-supply.com",
    "phone": "+1-555-SOLO",
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
        name="Solo Category",
        defaults={"slug": "solo-cat", "is_active": True},
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
        name="Solo Sugar",
        defaults={
            "unit": "kg",
            "current_quantity": Decimal("20.0"),
            "reorder_level": Decimal("5.0"),
            "cost_per_unit": Decimal("0.30"),
            "is_active": True,
        },
    )
    return cat


def _clear_test_data():
    """Remove all seed data from test DB."""
    from models.pos import Product, Customer, Employee, Category
    from models.inventory import Supplier
    from models.extra import Ingredient

    for model in (Product, Customer, Employee, Supplier, Category, Ingredient):
        model.objects.all().delete()


# ═══════════════════════════════════════════════════════════════════════
# 1. FragmentComponent context integration
# ═══════════════════════════════════════════════════════════════════════


class TestDashboardFragmentIntegration:
    """DashboardFragment seeded with real DB data."""

    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_counts(self):
        from fragments.dashboard import DashboardFragment

        context = DashboardFragment().get_context()
        assert context["product_count"] >= 1
        assert context["customer_count"] >= 1
        assert context["employee_count"] >= 1
        assert context["restaurant_name"] == "Forge Solo"

    def test_context_types_are_correct(self):
        from fragments.dashboard import DashboardFragment

        context = DashboardFragment().get_context()
        assert isinstance(context["product_count"], int)
        assert isinstance(context["customer_count"], int)
        assert isinstance(context["employee_count"], int)
        assert isinstance(context["sale_count"], int)
        assert isinstance(context["restaurant_name"], str)


class TestSuppliersFragmentIntegration:
    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_supplier(self):
        from fragments.suppliers import SuppliersFragment

        context = SuppliersFragment().get_context()
        assert context["count"] >= 1
        names = [s.name for s in context["suppliers"]]
        assert SEED_SUPPLIER["name"] in names


class TestCustomersFragmentIntegration:
    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_customer_stats(self):
        from fragments.customers import CustomersFragment

        context = CustomersFragment().get_context()
        assert context["total_customers"] >= 1
        assert context["active_customers"] >= 1


class TestEmployeesFragmentIntegration:
    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_context_contains_seeded_employee(self):
        from fragments.employees import EmployeesFragment

        context = EmployeesFragment().get_context()
        assert context["total_employees"] >= 1
        assert context["active_employees"] >= 1
        assert "server" in context["by_role"]


# ═══════════════════════════════════════════════════════════════════════
# 2. Template rendering integration
# ═══════════════════════════════════════════════════════════════════════

class TestDashboardTemplateRendering:
    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_dashboard_html_contains_seeded_counts(self):
        from fragments.dashboard import DashboardFragment
        from routes.fusion_fragments import _render_template, _DASHBOARD_FRAGMENT_TEMPLATE

        context = DashboardFragment().get_context()
        html = _render_template(_DASHBOARD_FRAGMENT_TEMPLATE, context)

        assert 'class="fusion-fragment"' in html
        assert 'data-fragment-name="dashboard"' in html
        assert str(context["product_count"]) in html

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
    def test_empty_db_does_not_crash_dashboard(self):
        from fragments.dashboard import DashboardFragment

        _clear_test_data()
        context = DashboardFragment().get_context()
        assert context["product_count"] == 0

    def test_product_detail_missing_pk_returns_safe_default(self):
        from fragments.products import ProductDetailFragment

        context = ProductDetailFragment().get_context()
        assert context["product"] is None
        assert context["in_stock"] is False

    def test_product_detail_nonexistent_pk_returns_safe_default(self):
        from fragments.products import ProductDetailFragment

        context = ProductDetailFragment().get_context(pk=99999)
        assert context["product"] is None


# ═══════════════════════════════════════════════════════════════════════
# 4. Health check integration
# ═══════════════════════════════════════════════════════════════════════

class TestFusionHealthIntegration:
    def test_health_checker_singleton_type(self):
        from middleware.fusion import fusion_health_checker, RobynFusionChecker
        assert isinstance(fusion_health_checker, RobynFusionChecker)

    def test_health_check_browser_ua_returns_true(self):
        from middleware.fusion import fusion_health_checker

        class MockReq:
            headers = {"User-Agent": "Mozilla/5.0 Chrome/120"}

        with patch("middleware.fusion.get_token_info", return_value=None):
            assert fusion_health_checker.get_preference(MockReq()) is True

    def test_health_check_script_ua_returns_false(self):
        from middleware.fusion import fusion_health_checker

        class MockReq:
            headers = {"User-Agent": "curl/8.0.1"}

        with patch("middleware.fusion.get_token_info", return_value=None):
            assert fusion_health_checker.get_preference(MockReq()) is False


# ═══════════════════════════════════════════════════════════════════════
# 5. End-to-end flow
# ═══════════════════════════════════════════════════════════════════════

class TestEndToEndFlow:
    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_full_dashboard_flow(self):
        from fragments.dashboard import DashboardFragment
        from routes.fusion_fragments import _render_template, _DASHBOARD_FRAGMENT_TEMPLATE

        context = DashboardFragment().get_context()
        html = _render_template(_DASHBOARD_FRAGMENT_TEMPLATE, context)

        assert "fusion-fragment" in html
        assert str(context["product_count"]) in html

    def test_full_suppliers_flow(self):
        from fragments.suppliers import SuppliersFragment
        from routes.fusion_fragments import _render_template, _SUPPLIERS_FRAGMENT_TEMPLATE

        context = SuppliersFragment().get_context()
        html = _render_template(_SUPPLIERS_FRAGMENT_TEMPLATE, context)

        assert SEED_SUPPLIER["name"] in html
        assert "fusion-fragment" in html


# ═══════════════════════════════════════════════════════════════════════
# 6. Cross-layer contract
# ═══════════════════════════════════════════════════════════════════════

class TestCrossLayerContract:
    @pytest.fixture(autouse=True)
    def _seed_and_cleanup(self):
        _seed_test_data()
        yield
        _clear_test_data()

    def test_fragment_html_has_expected_structure(self):
        from fragments.suppliers import SuppliersFragment
        from routes.fusion_fragments import _render_template, _SUPPLIERS_FRAGMENT_TEMPLATE

        context = SuppliersFragment().get_context()
        html = _render_template(_SUPPLIERS_FRAGMENT_TEMPLATE, context)

        assert 'class="fusion-fragment"' in html
        assert 'data-fragment-name="suppliers"' in html

    def test_fragment_markers_match_route_names(self):
        from routes.fusion_fragments import (
            _DASHBOARD_FRAGMENT_TEMPLATE,
            _SUPPLIERS_FRAGMENT_TEMPLATE,
            _ABOUT_FRAGMENT_TEMPLATE,
        )
        assert 'data-fragment-name="dashboard"' in _DASHBOARD_FRAGMENT_TEMPLATE
        assert 'data-fragment-name="suppliers"' in _SUPPLIERS_FRAGMENT_TEMPLATE
        assert 'data-fragment-name="about"' in _ABOUT_FRAGMENT_TEMPLATE


# ═══════════════════════════════════════════════════════════════════════
# 7. Route registration
# ═══════════════════════════════════════════════════════════════════════

class TestRouteRegistrationIntegration:
    def test_routes_register_with_correct_paths(self):
        app = MagicMock()
        from routes.fusion_fragments import register_fusion_fragment_routes

        register_fusion_fragment_routes(app)
        paths = [call[0][0] for call in app.get.call_args_list]
        assert "/fusion/render/dashboard" in paths
        assert "/fusion/render/suppliers" in paths
        assert "/fusion/render/about" in paths
