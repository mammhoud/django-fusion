"""
Cross-ORM data sync tests — verify Rust↔Django ORM parity with real data.

Split into two test classes:

  TestModelParity      — structural checks (table mapping, managed=False)
                         Always runs; does not require a real Rust DB.

  TestRealCrossORM      — actual data access tests (row queries, FK resolution,
                         field reads). Requires a Rust-built restaurant.db.
                         Uses the `rust_db` fixture; gracefully skipped when
                         no Rust DB exists.

Run with:
    DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/test_data_sync.py -v --tb=short
"""

from __future__ import annotations

import pytest

from tests.django_setup import _DJANGO_READY  # noqa: E402
# rust_db fixture registered via conftest.py (pytest_plugins = ["tests.fixtures"])


# ── Rust schema table list (from src-tauri/src/db/schema.rs) ──

RUST_TABLES = {
    # Core POS
    "settings", "categories", "products", "delivery_types", "employee_types",
    "employees", "customers", "sales", "sale_items",
    # Inventory
    "ingredients", "recipe_types", "recipes", "recipe_ingredients",
    "inventory_transactions", "inventory_adjustments", "inventory_alerts",
    # Supply
    "suppliers", "purchase_orders", "purchase_order_items",
    # Operations
    "kitchen_tickets", "loyalty_transactions", "receipt_templates",
    "tax_reports", "employee_schedules", "payrolls",
    # Auth
    "users", "roles", "user_roles",
    # Reports
    "report_metadata",
    # CRM
    "crm_companies", "crm_contacts", "crm_pipelines", "crm_stages", "crm_deals",
    "crm_activities", "crm_notes", "crm_sync_log", "crm_sync_queue", "crm_cloud_config",
}

# ── Must-have tables for meaningful real-data tests ──
MIN_TABLES_FOR_REAL_TEST = {"products", "categories", "customers", "sales"}


# ===========================================================================
# Structural parity tests (always run)
# ===========================================================================


class TestModelParity:
    """Model ↔ table mapping checks. Runs without a real Rust DB."""

    def test_django_ready(self):
        """Django ORM should bootstrap cleanly on shared DB."""
        assert _DJANGO_READY, "Django ORM bootstrap failed"

    def test_all_rust_tables_have_django_models(self):
        """Every Rust Diesel table has a corresponding Django posapp model."""
        from models import posapp as pos_models

        django_tables = {}
        for name in dir(pos_models):
            obj = getattr(pos_models, name)
            if hasattr(obj, "_meta") and hasattr(obj._meta, "db_table"):
                django_tables[obj._meta.db_table] = obj

        missing = RUST_TABLES - set(django_tables.keys())
        assert not missing, (
            f"Missing Django models for Rust tables: {missing}\n"
            f"Django has: {sorted(django_tables.keys())}"
        )

    def test_all_rust_tables_are_unmanaged(self):
        """All Rust-mirror models must have managed=False."""
        from models import posapp as pos_models

        managed_tables = []
        for name in dir(pos_models):
            obj = getattr(pos_models, name)
            if hasattr(obj, "_meta") and hasattr(obj._meta, "db_table"):
                if obj._meta.managed and obj._meta.db_table in RUST_TABLES:
                    managed_tables.append(obj._meta.db_table)

        assert not managed_tables, (
            f"Rust-mirror models should be managed=False, got: {managed_tables}"
        )

    def test_support_ticket_is_managed(self):
        """SupportTicket is the only managed=True model in posapp."""
        from models.ops import SupportTicket
        assert SupportTicket._meta.managed is True
        assert SupportTicket._meta.db_table == "support_tickets"

    def test_db_path_is_unified(self):
        """DB_PATH should be restaurant.db (or env override)."""
        from django.conf import settings

        db_path = str(settings.DATABASES["default"]["NAME"])
        valid = any(x in db_path.lower() for x in ("restaurant", "memory", "test"))
        assert valid, f"DB should be unified (restaurant.db), got {db_path}"


# ===========================================================================
# Real cross-ORM data access tests (requires Rust-built restaurant.db)
# ===========================================================================


@pytest.mark.usefixtures("rust_db")
class TestRealCrossORM:
    """Cross-ORM reads against an actual Rust-built database.

    These tests are only collected and run when a real restaurant.db
    exists with the expected Rust-managed tables. Otherwise, the
    `rust_db` fixture calls pytest.skip() with a clear explanation.
    """

    def test_rust_db_has_expected_tables(self, rust_db):
        """The Rust DB should contain the core POS tables."""
        tables = rust_db.table_names()
        missing = MIN_TABLES_FOR_REAL_TEST - tables
        assert not missing, (
            f"Rust DB missing core tables: {missing}. "
            f"Tables present: {sorted(tables)}"
        )

    def test_read_products_via_orm(self, rust_db):
        """Products table should be queryable via Django ORM."""
        count = rust_db.posapp.Product.objects.count()
        assert isinstance(count, int), f"Expected int count, got {type(count)}"
        assert count >= 0, f"Product count should be non-negative, got {count}"

    def test_read_categories_via_orm(self, rust_db):
        """Categories table should be queryable via Django ORM."""
        count = rust_db.posapp.Category.objects.count()
        assert isinstance(count, int)
        assert count >= 0

    def test_read_customers_via_orm(self, rust_db):
        """Customers table should be queryable via Django ORM."""
        count = rust_db.posapp.Customer.objects.count()
        assert isinstance(count, int)
        assert count >= 0

    def test_read_sales_via_orm(self, rust_db):
        """Sales table should be queryable via Django ORM."""
        count = rust_db.posapp.Sale.objects.count()
        assert isinstance(count, int)
        assert count >= 0

    def test_product_fields_accessible(self, rust_db):
        """Individual product fields should be readable via ORM."""
        product = rust_db.posapp.Product.objects.first()
        if product is not None:
            assert product.name is not None
            assert product.price is not None
            assert isinstance(product.name, str)
            assert isinstance(product.price, (int, float))

    def test_sale_foreign_keys_resolve(self, rust_db):
        """Sale FK relationships (customer, employee) should resolve."""
        sale = rust_db.posapp.Sale.objects.select_related(
            "customer", "employee"
        ).first()
        if sale is not None:
            # Sale exists — FK accessors should not crash
            customer = sale.customer
            employee = sale.employee
            # These may be None (nullable FKs), which is fine
            assert customer is None or hasattr(customer, "name")
            assert employee is None or hasattr(employee, "name")

    def test_sale_items_related(self, rust_db):
        """SaleItem should have a resolvable FK back to Sale."""
        item = rust_db.posapp.SaleItem.objects.select_related("sale").first()
        if item is not None:
            assert item.sale is not None
            assert hasattr(item.sale, "total_amount")

    def test_db_sanity_check(self, rust_db):
        """Sanity check: the Rust DB has the expected tables via raw SQL."""
        rows = rust_db.raw_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        assert len(rows) > 0
        table_names = [r[0] for r in rows]
        assert "products" in table_names, f"products table not found in {table_names}"

    def test_row_counts_match(self, rust_db):
        """ORM count() should match raw SQL COUNT(*)."""
        orm_count = rust_db.posapp.Product.objects.count()
        raw_count = rust_db.row_count("products")
        assert orm_count == raw_count, (
            f"ORM count {orm_count} != raw count {raw_count}"
        )

    def test_filter_query_works(self, rust_db):
        """Django ORM filter() should work on Rust-managed data."""
        # Query for products with a positive price
        products = list(
            rust_db.posapp.Product.objects.filter(price__gt=0)[:10]
        )
        if products:
            for p in products:
                assert p.price > 0

    def test_all_crm_tables_accessible(self, rust_db):
        """All 10 CRM tables should be queryable via Django ORM."""
        crm_tables = {
            "crm_companies": rust_db.posapp.CRMCompany,
            "crm_contacts": rust_db.posapp.CRMContact,
            "crm_pipelines": rust_db.posapp.CRMPipeline,
            "crm_stages": rust_db.posapp.CRMStage,
            "crm_deals": rust_db.posapp.CRMDeal,
            "crm_activities": rust_db.posapp.CRMActivity,
            "crm_notes": rust_db.posapp.PosCRMNote,
            "crm_sync_log": rust_db.posapp.CRMSyncLog,
            "crm_sync_queue": rust_db.posapp.CRMSyncQueue,
            "crm_cloud_config": rust_db.posapp.CRMCloudConfig,
        }
        present = rust_db.table_names()
        for table_name, model in crm_tables.items():
            if table_name in present:
                count = model.objects.count()
                assert isinstance(count, int), f"Failed to query {table_name}"
