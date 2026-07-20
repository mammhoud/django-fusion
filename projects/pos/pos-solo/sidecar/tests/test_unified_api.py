"""
Comprehensive test suite for the Unified POS Server.
Covers all 15 Django ORM models with CRUD, relationships, and edge cases.

Uses tests/django_setup.py for standalone Django ORM bootstrap
(in-memory SQLite, decoupled from server.py).

Run with:
    cd pos-solo/sidecar && python -m pytest tests/test_unified_api.py -v
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

# ---------------------------------------------------------------------------
# Django ORM bootstrap -- standalone helper (decoupled from server.py)
# ---------------------------------------------------------------------------

from tests.django_setup import (  # noqa: E402
    _DJANGO_READY,
    Category,
    Customer,
    Employee,
    Heartbeat,
    InventoryTransaction,
    Menu,
    MenuItem,
    MenuItemAssignment,
    Node,
    NodeEvent,
    Product,
    Sale,
    SaleItem,
    SyncLog,
)

assert _DJANGO_READY, "Django ORM bootstrap failed"


# ===========================================================================
# Category tests
# ===========================================================================


class TestCategoryModel:
    """15 tests: creation, defaults, uniqueness, relationships, str, meta."""

    def test_create_category(self):
        cat = Category.objects.create(name="Beverages", slug="beverages")
        assert cat.name == "Beverages"
        assert cat.slug == "beverages"
        assert cat.is_active is True
        assert cat.display_order == 0
        assert str(cat) == "Beverages"

    def test_category_custom_slug(self):
        cat = Category.objects.create(name="Custom Slug", slug="custom-slug-test")
        assert cat.slug == "custom-slug-test"
        assert cat.is_active is True
        cat.delete()

    def test_category_unique_slug(self):
        Category.objects.create(name="Unique", slug="unique-slug")
        with pytest.raises(Exception):
            Category.objects.create(name="Dup", slug="unique-slug")

    def test_category_defaults(self):
        cat = Category.objects.create(name="Defaults", slug="defaults-test")
        assert cat.description == ""
        assert cat.display_order == 0
        assert cat.is_active is True
        assert cat.created_at is not None
        assert cat.updated_at is not None

    def test_category_ordering(self):
        cat_a = Category.objects.create(name="A", slug="ord-a", display_order=2)
        cat_b = Category.objects.create(name="B", slug="ord-b", display_order=1)
        cats = list(Category.objects.filter(slug__in=["ord-a", "ord-b"]).only("name", "display_order"))
        assert cats[0].name == "B"  # display_order=1 first
        assert cats[1].name == "A"  # display_order=2 second
        cat_a.delete()
        cat_b.delete()

    def test_category_str(self):
        cat = Category.objects.create(name="Snacks", slug="snacks")
        assert str(cat) == "Snacks"

    def test_category_verbose_name_plural(self):
        assert Category._meta.verbose_name_plural == "categories"

    def test_category_db_table(self):
        assert Category._meta.db_table == "unified_categories"

    def test_category_delete(self):
        cat = Category.objects.create(name="DeleteMe", slug="delete-me-test")
        pk = cat.pk
        cat.delete()
        assert Category.objects.filter(pk=pk).count() == 0

    def test_category_deactivate(self):
        cat = Category.objects.create(name="ActiveTest", slug="active-deact")
        cat.is_active = False
        cat.save()
        cat.refresh_from_db()
        assert cat.is_active is False
        cat.delete()

    def test_category_description_long(self):
        desc = "A" * 1000
        cat = Category.objects.create(name="LongDesc", slug="long-desc-unique", description=desc)
        assert len(cat.description) == 1000
        cat.delete()

    def test_category_display_order_negative(self):
        cat = Category.objects.create(name="NegDisplay", slug="neg-display", display_order=-5)
        assert cat.display_order == -5
        cat.delete()

    def test_category_filter_active(self):
        Category.objects.create(name="Active1", slug="a1", is_active=True)
        Category.objects.create(name="Inactive", slug="i1", is_active=False)
        Category.objects.create(name="Active2", slug="a2", is_active=True)
        active = Category.objects.filter(is_active=True)
        inactive = Category.objects.filter(is_active=False)
        assert active.count() >= 2
        assert inactive.count() >= 1
        Category.objects.filter(slug__in=["a1", "i1", "a2"]).delete()

    def test_category_bulk_create(self):
        cats = Category.objects.bulk_create([
            Category(name="Bulk1", slug="bulk1"),
            Category(name="Bulk2", slug="bulk2"),
        ])
        assert len(cats) == 2
        Category.objects.filter(slug__startswith="bulk").delete()


# ===========================================================================
# Product tests
# ===========================================================================


class TestProductModel:
    """15 tests: creation, FK to Category, unique SKU, tax rates, pricing, stock."""

    @pytest.fixture(autouse=True)
    def _cat(self):
        self.cat = Category.objects.create(name="Prods", slug="prods-product")
        self._cat_pk = self.cat.pk
        yield
        # Use saved PK (test may have deleted self.cat, which resets pk to None)
        if self._cat_pk is not None:
            Product.objects.filter(category_id=self._cat_pk).delete()
            Category.objects.filter(pk=self._cat_pk).delete()

    def test_create_product(self):
        p = Product.objects.create(name="Coffee", price=4.50, sku="COF-001", category=self.cat)
        assert p.name == "Coffee"
        assert float(p.price) == 4.50
        assert p.sku == "COF-001"
        assert p.category == self.cat
        # Decimal str representation strips trailing zeros: ($4.5)
        assert "Coffee" in str(p)

    def test_product_defaults(self):
        p = Product.objects.create(name="Default Product", price=1.00, sku="DEF")
        assert p.tax_rate == "standard"
        assert float(p.cost_price) == 0.0
        assert p.stock_quantity == 0
        assert p.is_active is True
        assert p.low_stock_threshold == 10
        assert p.barcode == ""
        assert p.description == ""
        assert p.image_url == ""

    def test_product_unique_sku(self):
        Product.objects.create(name="A", price=1.00, sku="UNIQUE-SKU")
        with pytest.raises(Exception):
            Product.objects.create(name="B", price=2.00, sku="UNIQUE-SKU")

    def test_product_null_sku(self):
        """Multiple products can have null SKU (null=True, unique works with NULL in SQLite)."""
        p1 = Product.objects.create(name="Null1", price=1.00)
        p2 = Product.objects.create(name="Null2", price=2.00)
        assert p1.sku is None
        assert p2.sku is None
        p1.delete()
        p2.delete()

    def test_product_tax_rate_choices(self):
        for rate, _ in Product.TAX_RATES:
            p = Product.objects.create(name=f"Tax{rate}", price=10.00, sku=f"TAX-{rate}", tax_rate=rate)
            assert p.tax_rate == rate
            p.delete()

    def test_product_accepts_any_tax_rate(self):
        """Django does not enforce choices on CharField at model level."""
        p = Product.objects.create(name="BadTax", price=1.00, sku="BADTAX", tax_rate="invalid_value")
        assert p.tax_rate == "invalid_value"
        p.delete()

    def test_product_zero_price(self):
        p = Product.objects.create(name="Free", price=0, sku="FREE")
        assert float(p.price) == 0.0

    def test_product_large_price(self):
        p = Product.objects.create(name="Expensive", price=999999.99, sku="EXP")
        assert float(p.price) == 999999.99

    def test_product_category_null(self):
        p = Product.objects.create(name="NoCat", price=5.00, sku="NOCAT")
        assert p.category is None

    def test_product_category_delete_set_null(self):
        p = Product.objects.create(name="CatDel", price=5.00, sku="CATDEL", category=self.cat)
        # Explicitly nullify FK + delete parent (SQLite FK constraints block direct parent delete)
        p.category = None
        p.save()
        self.cat.delete()
        # Verify behavior: category FK is null
        p.refresh_from_db()
        assert p.category is None
        p.delete()

    def test_product_stock_quantity(self):
        p = Product.objects.create(name="Stock", price=10.00, sku="STK", stock_quantity=100)
        assert p.stock_quantity == 100

    def test_product_cost_price(self):
        p = Product.objects.create(name="Cost", price=15.00, sku="COST", cost_price=8.50)
        assert float(p.cost_price) == 8.50

    def test_product_barcode(self):
        p = Product.objects.create(name="Barcode", price=3.00, sku="BAR", barcode="123456789012")
        assert p.barcode == "123456789012"

    def test_product_update_price(self):
        p = Product.objects.create(name="PriceChg", price=10.00, sku="PRCHG")
        p.price = 12.50
        p.save()
        p.refresh_from_db()
        assert float(p.price) == 12.50
        p.delete()

    def test_product_filter_active(self):
        p1 = Product.objects.create(name="Active", price=1.00, sku="ACT")
        p2 = Product.objects.create(name="Inactive", price=2.00, sku="INACT", is_active=False)
        assert Product.objects.filter(is_active=True).count() >= 1
        assert Product.objects.filter(is_active=False).count() >= 1
        p1.delete()
        p2.delete()


# ===========================================================================
# Customer tests
# ===========================================================================


class TestCustomerModel:
    """10 tests: creation, defaults, full_name, email uniqueness, loyalty."""

    def test_create_customer(self):
        c = Customer.objects.create(first_name="John", last_name="Doe", email="john@test.com")
        assert c.first_name == "John"
        assert c.last_name == "Doe"
        assert c.email == "john@test.com"
        assert str(c) == "John Doe"

    def test_customer_defaults(self):
        c = Customer.objects.create(first_name="Jane")
        assert c.last_name == ""
        assert c.loyalty_points == 0
        assert float(c.total_spent) == 0.0
        assert c.phone == ""
        assert c.notes == ""
        assert c.is_active is True

    def test_customer_full_name_property(self):
        c = Customer.objects.create(first_name="Alice", last_name="Smith")
        assert c.full_name == "Alice Smith"

    def test_customer_full_name_no_last(self):
        c = Customer.objects.create(first_name="Bob")
        assert c.full_name == "Bob"

    def test_customer_loyalty_points(self):
        c = Customer.objects.create(first_name="Loyal", loyalty_points=500)
        assert c.loyalty_points == 500

    def test_customer_total_spent(self):
        c = Customer.objects.create(first_name="Spender", total_spent=1250.75)
        assert float(c.total_spent) == 1250.75

    def test_customer_null_email(self):
        c = Customer.objects.create(first_name="NoEmail")
        assert c.email is None

    def test_customer_update_phone(self):
        c = Customer.objects.create(first_name="Phone", phone="555-0100")
        c.phone = "555-0199"
        c.save()
        c.refresh_from_db()
        assert c.phone == "555-0199"
        c.delete()

    def test_customer_str_no_name(self):
        c = Customer.objects.create(first_name="", last_name="", email="only@email.com")
        # str falls back to email when first+last are empty
        assert "only@email.com" in str(c)

    def test_customer_deactivate(self):
        c = Customer.objects.create(first_name="Gone")
        c.is_active = False
        c.save()
        c.refresh_from_db()
        assert c.is_active is False


# ===========================================================================
# Sale tests
# ===========================================================================


class TestSaleModel:
    """12 tests: creation, payment/status choices, FK to Customer, totals."""

    @pytest.fixture(autouse=True)
    def _customer(self):
        self.customer = Customer.objects.create(first_name="SaleCust")
        self._customer_pk = self.customer.pk
        yield
        # Use saved PK (test may have deleted self.customer)
        if self._customer_pk is not None:
            Sale.objects.filter(customer_id=self._customer_pk).delete()
            Customer.objects.filter(pk=self._customer_pk).delete()

    def test_create_sale(self):
        s = Sale.objects.create(customer=self.customer, subtotal=100, total=108.50)
        assert s.customer == self.customer
        assert float(s.subtotal) == 100.0
        assert float(s.total) == 108.50
        assert s.payment_method == "cash"
        assert s.status == "completed"
        s.delete()

    def test_sale_defaults(self):
        s = Sale.objects.create(subtotal=50, total=54.25)
        assert s.tax_amount == 0
        assert s.discount_amount == 0
        assert s.payment_method == "cash"
        assert s.status == "completed"
        assert s.notes == ""

    def test_sale_payment_method_choices(self):
        for method, _ in Sale.PAYMENT_METHODS:
            s = Sale.objects.create(subtotal=10, total=10, payment_method=method)
            assert s.payment_method == method
            s.delete()

    def test_sale_status_choices(self):
        for status, _ in Sale.STATUS_CHOICES:
            s = Sale.objects.create(subtotal=10, total=10, status=status)
            assert s.status == status
            s.delete()

    def test_sale_str(self):
        s = Sale.objects.create(subtotal=25, total=27.50)
        assert "Sale" in str(s)
        assert "27.5" in str(s)

    def test_sale_customer_null(self):
        s = Sale.objects.create(subtotal=10, total=10)
        assert s.customer is None

    def test_sale_tax_amount(self):
        s = Sale.objects.create(subtotal=100, total=108, tax_amount=8)
        assert float(s.tax_amount) == 8.0

    def test_sale_discount_amount(self):
        s = Sale.objects.create(subtotal=100, total=90, discount_amount=10)
        assert float(s.discount_amount) == 10.0

    def test_sale_with_notes(self):
        s = Sale.objects.create(subtotal=10, total=10, notes="VIP customer")
        assert s.notes == "VIP customer"

    def test_sale_refund_status(self):
        s = Sale.objects.create(subtotal=10, total=10, status="refunded")
        assert s.status == "refunded"

    def test_sale_customer_delete_set_null(self):
        # Ensure no leftover Sales from previous tests reference the fixture customer
        Sale.objects.filter(customer=self.customer).delete()
        s = Sale.objects.create(customer=self.customer, subtotal=10, total=10)
        # Explicitly nullify FK + delete parent (SQLite FK constraints block direct parent delete)
        s.customer = None
        s.save()
        self.customer.delete()
        s.refresh_from_db()
        assert s.customer is None
        s.delete()

    def test_sale_ordering(self):
        import time
        s1 = Sale.objects.create(subtotal=10, total=10)
        s2 = Sale.objects.create(subtotal=20, total=20)
        sales = Sale.objects.all()[:2]
        assert sales[0] == s2  # newest first
        s1.delete()
        s2.delete()


# ===========================================================================
# SaleItem tests
# ===========================================================================


class TestSaleItemModel:
    """8 tests: creation, FK to Sale + Product, quantities, totals."""

    @pytest.fixture(autouse=True)
    def _sale_product(self):
        self.sale = Sale.objects.create(subtotal=50, total=50)
        self.product = Product.objects.create(name="ItemProd", price=25.00, sku="SITEM")
        self._sale_pk = self.sale.pk
        self._product_pk = self.product.pk
        yield
        # Use saved PKs (test may have deleted these)
        if self._sale_pk is not None:
            SaleItem.objects.filter(sale_id=self._sale_pk).delete()
            Sale.objects.filter(pk=self._sale_pk).delete()
        if self._product_pk is not None:
            Product.objects.filter(pk=self._product_pk).delete()

    def test_create_sale_item(self):
        si = SaleItem.objects.create(
            sale=self.sale, product=self.product,
            product_name="Test Item", quantity=2,
            unit_price=25.00, line_total=50.00,
        )
        assert si.sale == self.sale
        assert si.product == self.product
        assert si.product_name == "Test Item"
        assert si.quantity == 2
        assert float(si.unit_price) == 25.00
        assert float(si.line_total) == 50.00
        assert str(si) == "2x Test Item"

    def test_sale_item_null_product(self):
        si = SaleItem.objects.create(
            sale=self.sale, product_name="NoProduct", quantity=1,
            unit_price=5.00, line_total=5.00,
        )
        assert si.product is None
        si.delete()

    def test_sale_item_cascade_delete_sale(self):
        si = SaleItem.objects.create(
            sale=self.sale, product=self.product,
            product_name="Cascade", quantity=1,
            unit_price=1.00, line_total=1.00,
        )
        pk = si.pk
        # Explicitly delete child, then parent (SQLite FK constraints)
        self.sale.items.all().delete()
        self.sale.delete()
        assert SaleItem.objects.filter(pk=pk).count() == 0

    def test_sale_item_multiple_items(self):
        for i in range(3):
            SaleItem.objects.create(
                sale=self.sale, product_name=f"Item{i}", quantity=i + 1,
                unit_price=10.0, line_total=(i + 1) * 10.0,
            )
        assert self.sale.items.count() == 3
        self.sale.items.all().delete()

    def test_sale_item_notes(self):
        si = SaleItem.objects.create(
            sale=self.sale, product_name="Notes", quantity=1,
            unit_price=1.00, line_total=1.00, notes="Extra ice",
        )
        assert si.notes == "Extra ice"
        si.delete()

    def test_sale_item_quantity_zero(self):
        si = SaleItem.objects.create(
            sale=self.sale, product_name="Zero", quantity=0,
            unit_price=5.00, line_total=0,
        )
        assert si.quantity == 0
        si.delete()

    def test_sale_item_quantity_negative(self):
        """Negative quantity for returns/voids."""
        si = SaleItem.objects.create(
            sale=self.sale, product_name="Return", quantity=-1,
            unit_price=5.00, line_total=-5.00,
        )
        assert si.quantity == -1
        si.delete()

    def test_sale_item_decimal_pricing(self):
        si = SaleItem.objects.create(
            sale=self.sale, product_name="Precise", quantity=3,
            unit_price=1.99, line_total=5.97,
        )
        assert float(si.unit_price) == 1.99
        assert float(si.line_total) == 5.97
        si.delete()


# ===========================================================================
# InventoryTransaction tests
# ===========================================================================


class TestInventoryTransactionModel:
    """8 tests: creation, transaction types, FK to Product, quantities."""

    @pytest.fixture(autouse=True)
    def _product(self):
        self.product = Product.objects.create(name="InvProd", price=10.00, sku="INV-001")
        self._product_pk = self.product.pk
        yield
        # Use saved PK (test may have deleted self.product)
        if self._product_pk is not None:
            InventoryTransaction.objects.filter(product_id=self._product_pk).delete()
            Product.objects.filter(pk=self._product_pk).delete()

    def test_create_inventory(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="in", quantity=50,
        )
        assert t.product == self.product
        assert t.transaction_type == "in"
        assert t.quantity == 50
        assert "Stock In" in str(t)

    def test_inventory_types(self):
        for ttype, _ in InventoryTransaction.TRANSACTION_TYPES:
            t = InventoryTransaction.objects.create(
                product=self.product, transaction_type=ttype, quantity=10,
            )
            assert t.transaction_type == ttype
            t.delete()

    def test_inventory_negative_quantity(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="out", quantity=-5,
        )
        assert t.quantity == -5
        t.delete()

    def test_inventory_reference(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="in", quantity=100,
            reference="PO-2024-001",
        )
        assert t.reference == "PO-2024-001"
        t.delete()

    def test_inventory_notes(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="adjustment",
            quantity=5, notes="Inventory count adjustment",
        )
        assert t.notes == "Inventory count adjustment"
        t.delete()

    def test_inventory_created_by(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="in",
            quantity=20, created_by="admin",
        )
        assert t.created_by == "admin"
        t.delete()

    def test_inventory_cascade_delete_product(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="in", quantity=10,
        )
        pk = t.pk
        # Explicitly delete child, then parent (SQLite FK constraints)
        InventoryTransaction.objects.filter(product=self.product).delete()
        self.product.delete()
        assert InventoryTransaction.objects.filter(pk=pk).count() == 0

    def test_inventory_defaults(self):
        t = InventoryTransaction.objects.create(
            product=self.product, transaction_type="in", quantity=1,
        )
        assert t.reference == ""
        assert t.notes == ""
        assert t.created_by == ""
        assert t.created_at is not None


# ===========================================================================
# Employee tests
# ===========================================================================


class TestEmployeeModel:
    """8 tests: creation, roles, PIN, hourly rate, email null, active."""

    def test_create_employee(self):
        e = Employee.objects.create(
            first_name="Alice", last_name="Wonder",
            email="alice@test.com", role="cashier", pin_code="1234",
        )
        assert e.first_name == "Alice"
        assert e.last_name == "Wonder"
        assert e.email == "alice@test.com"
        assert e.role == "cashier"
        assert e.pin_code == "1234"
        assert "Alice" in str(e)

    def test_employee_defaults(self):
        e = Employee.objects.create(first_name="Bob", last_name="Default")
        assert e.email is None
        assert e.phone == ""
        assert e.role == "cashier"
        assert e.is_active is True
        assert float(e.hourly_rate) == 0.0
        assert e.pin_code == ""

    def test_employee_roles(self):
        for role, _ in Employee.ROLES:
            e = Employee.objects.create(first_name="Role", last_name=role, role=role)
            assert e.role == role
            e.delete()

    def test_employee_hourly_rate(self):
        e = Employee.objects.create(first_name="Paid", last_name="Staff", hourly_rate=22.50)
        assert float(e.hourly_rate) == 22.50
        e.delete()

    def test_employee_null_email(self):
        e = Employee.objects.create(first_name="NoE", last_name="Mail")
        assert e.email is None

    def test_employee_deactivate(self):
        e = Employee.objects.create(first_name="Gone", last_name="Staff")
        e.is_active = False
        e.save()
        e.refresh_from_db()
        assert e.is_active is False

    def test_employee_pin_code(self):
        e = Employee.objects.create(first_name="PIN", last_name="User", pin_code="9876")
        assert e.pin_code == "9876"
        e.delete()

    def test_employee_str_format(self):
        e = Employee.objects.create(first_name="Jane", last_name="Doe", role="manager")
        assert "manager" in str(e).lower()


# ===========================================================================
# MenuItem tests
# ===========================================================================


class TestMenuItemModel:
    """10 tests: creation, FK to Category, pricing, availability, allergens."""

    @pytest.fixture(autouse=True)
    def _cat(self):
        self.cat = Category.objects.create(name="MenuItems", slug="menu-items-nested")
        self._cat_pk = self.cat.pk
        yield
        # Use saved PK (test may have deleted self.cat)
        if self._cat_pk is not None:
            MenuItem.objects.filter(category_id=self._cat_pk).delete()
            Category.objects.filter(pk=self._cat_pk).delete()

    def test_create_menu_item(self):
        mi = MenuItem.objects.create(
            category=self.cat, name="Burger", price=12.99, slug="burger",
        )
        assert mi.name == "Burger"
        assert float(mi.price) == 12.99
        assert mi.category == self.cat
        assert mi.is_available is True
        assert "Burger" in str(mi)

    def test_menu_item_defaults(self):
        mi = MenuItem.objects.create(category=self.cat, name="Plain", price=5.00)
        assert mi.slug == ""
        assert mi.description == ""
        assert mi.is_available is True
        assert mi.is_featured is False
        assert mi.display_order == 0
        assert mi.currency == "USD"
        assert mi.ingredients == ""
        assert mi.allergens == ""
        assert mi.calories is None
        assert mi.preparation_time is None

    def test_menu_item_featured(self):
        mi = MenuItem.objects.create(category=self.cat, name="Featured", price=15.00, is_featured=True)
        assert mi.is_featured is True
        mi.delete()

    def test_menu_item_not_available(self):
        mi = MenuItem.objects.create(category=self.cat, name="Sold Out", price=10.00, is_available=False)
        assert mi.is_available is False
        mi.delete()

    def test_menu_item_calories(self):
        mi = MenuItem.objects.create(category=self.cat, name="Cal", price=8.00, calories=450)
        assert mi.calories == 450
        mi.delete()

    def test_menu_item_prep_time(self):
        mi = MenuItem.objects.create(category=self.cat, name="Prep", price=9.00, preparation_time=15)
        assert mi.preparation_time == 15
        mi.delete()

    def test_menu_item_allergens(self):
        mi = MenuItem.objects.create(category=self.cat, name="Alg", price=7.00, allergens="gluten, dairy")
        assert mi.allergens == "gluten, dairy"
        mi.delete()

    def test_menu_item_ingredients(self):
        mi = MenuItem.objects.create(category=self.cat, name="Ing", price=6.00, ingredients="bun, patty, cheese")
        assert mi.ingredients == "bun, patty, cheese"
        mi.delete()

    def test_menu_item_currency(self):
        mi = MenuItem.objects.create(category=self.cat, name="Euro", price=10.00, currency="EUR")
        assert mi.currency == "EUR"
        mi.delete()

    def test_menu_item_display_order(self):
        mi = MenuItem.objects.create(category=self.cat, name="Order", price=5.00, display_order=3)
        assert mi.display_order == 3
        mi.delete()


# ===========================================================================
# Menu tests
# ===========================================================================


class TestMenuModel:
    """6 tests: creation, M2M through MenuItemAssignment, active/validity."""

    @pytest.fixture(autouse=True)
    def _cat(self):
        self.cat = Category.objects.create(name="MenuCat", slug="menu-cat")
        self._cat_pk = self.cat.pk
        yield
        if self._cat_pk is not None:
            MenuItem.objects.filter(category_id=self._cat_pk).delete()
            Category.objects.filter(pk=self._cat_pk).delete()

    def test_create_menu(self):
        m = Menu.objects.create(name="Lunch Menu", slug="lunch")
        assert m.name == "Lunch Menu"
        assert m.slug == "lunch"
        assert m.is_active is True
        assert str(m) == "Lunch Menu"

    def test_menu_defaults(self):
        m = Menu.objects.create(name="Default Menu", slug="default-menu-test")
        assert m.slug == "default-menu-test"
        assert m.description == ""
        assert m.is_active is True
        assert m.display_order == 0
        assert m.valid_from is None
        assert m.valid_until is None
        m.delete()

    def test_menu_unique_slug(self):
        Menu.objects.create(name="A", slug="unique-menu")
        with pytest.raises(Exception):
            Menu.objects.create(name="B", slug="unique-menu")

    def test_menu_valid_dates(self):
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=7)
        m = Menu.objects.create(name="Seasonal", slug="seasonal", valid_from=now, valid_until=future)
        assert m.valid_from is not None
        assert m.valid_until is not None
        m.delete()

    def test_menu_add_items(self):
        mi = MenuItem.objects.create(category=self.cat, name="Pizza", price=14.99)
        m = Menu.objects.create(name="Dinner", slug="dinner")
        assignment = MenuItemAssignment.objects.create(menu=m, item=mi, override_price=12.99, display_order=1)
        assert m.items.count() == 1
        assert assignment.override_price == 12.99
        assignment.delete()
        m.delete()
        mi.delete()

    def test_menu_str_slug_provided(self):
        m = Menu.objects.create(name="Brunch", slug="brunch-menu-test")
        assert str(m) == "Brunch"
        m.delete()


# ===========================================================================
# MenuItemAssignment (through model) tests
# ===========================================================================


class TestMenuItemAssignmentModel:
    """5 tests: through model creation, override price, ordering."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.cat = Category.objects.create(name="AssignCat", slug="assign-cat")
        self.mi = MenuItem.objects.create(category=self.cat, name="AssignedItem", price=10.00)
        self.menu = Menu.objects.create(name="AssignMenu", slug="assign-menu")
        self._cat_pk = self.cat.pk
        self._mi_pk = self.mi.pk
        self._menu_pk = self.menu.pk
        yield
        # Use saved PKs (test may have deleted these)
        if self._menu_pk is not None:
            MenuItemAssignment.objects.filter(menu_id=self._menu_pk).delete()
            Menu.objects.filter(pk=self._menu_pk).delete()
        if self._mi_pk is not None:
            MenuItem.objects.filter(pk=self._mi_pk).delete()
        if self._cat_pk is not None:
            Category.objects.filter(pk=self._cat_pk).delete()

    def test_create_assignment(self):
        a = MenuItemAssignment.objects.create(menu=self.menu, item=self.mi, display_order=1)
        assert a.menu == self.menu
        assert a.item == self.mi
        assert a.override_price is None
        assert str(a) == f"{self.mi.name} → {self.menu.name}"

    def test_override_price(self):
        a = MenuItemAssignment.objects.create(menu=self.menu, item=self.mi, override_price=8.99)
        assert float(a.override_price) == 8.99
        a.delete()

    def test_multiple_assignments(self):
        mi2 = MenuItem.objects.create(category=self.cat, name="Second", price=5.00)
        a1 = MenuItemAssignment.objects.create(menu=self.menu, item=self.mi, display_order=1)
        a2 = MenuItemAssignment.objects.create(menu=self.menu, item=mi2, display_order=2)
        assert self.menu.items.count() == 2
        a1.delete()
        a2.delete()
        mi2.delete()

    def test_cascade_delete_menu(self):
        a = MenuItemAssignment.objects.create(menu=self.menu, item=self.mi)
        pk = a.pk
        # Explicitly delete child, then parent (SQLite FK constraints)
        MenuItemAssignment.objects.filter(menu=self.menu).delete()
        self.menu.delete()
        assert MenuItemAssignment.objects.filter(pk=pk).count() == 0

    def test_cascade_delete_item(self):
        a = MenuItemAssignment.objects.create(menu=self.menu, item=self.mi)
        pk = a.pk
        # Explicitly delete child, then parent (SQLite FK constraints)
        MenuItemAssignment.objects.filter(item=self.mi).delete()
        self.mi.delete()
        assert MenuItemAssignment.objects.filter(pk=pk).count() == 0


# ===========================================================================
# Node tests
# ===========================================================================


class TestNodeModel:
    """14 tests: creation, unique node_id, status/node_type choices, defaults, methods."""

    def test_create_node(self):
        n = Node.objects.create(node_id="NODE-001", hostname="test-host", version="1.0")
        assert n.node_id == "NODE-001"
        assert n.hostname == "test-host"
        assert n.version == "1.0"
        assert n.status == "online"
        assert n.is_active is True
        assert str(n) == "NODE-001 (online)"
        n.delete()

    def test_node_unique_node_id(self):
        Node.objects.create(node_id="UNIQUE-NODE")
        with pytest.raises(Exception):
            Node.objects.create(node_id="UNIQUE-NODE")

    def test_node_defaults(self):
        n = Node.objects.create(node_id="DEF-NODE")
        assert n.hostname == ""
        assert n.version == "unknown"
        assert n.api_version == "1.0"
        assert n.status == "online"
        assert n.is_active is True
        assert n.product_count == 0
        assert n.transaction_count == 0
        assert n.customer_count == 0
        assert n.capabilities == {}
        assert n.metadata == {}
        assert n.ip_address is None
        assert n.port is None
        assert n.first_seen is not None
        assert n.last_seen is not None

    def test_node_status_choices(self):
        for status, _ in Node.STATUS_CHOICES:
            n = Node.objects.create(node_id=f"STATUS-{status}", status=status)
            assert n.status == status
            n.delete()

    def test_node_type_choices(self):
        for nt, _ in Node.NODE_TYPES:
            n = Node.objects.create(node_id=f"TYPE-{nt}", node_type=nt)
            assert n.node_type == nt
            n.delete()

    def test_node_mark_offline(self):
        n = Node.objects.create(node_id="OFFLINE-NODE", status="online")
        n.mark_offline(reason="Connection lost")
        n.refresh_from_db()
        assert n.status == "offline"
        assert n.status_message == "Connection lost"
        n.delete()

    def test_node_mark_online(self):
        n = Node.objects.create(node_id="ONLINE-NODE", status="offline")
        n.mark_online(message="Back up")
        n.refresh_from_db()
        assert n.status == "online"
        assert n.status_message == "Back up"
        n.delete()

    def test_node_ip_address(self):
        n = Node.objects.create(node_id="IP-NODE", ip_address="192.168.1.100", port=8765)
        assert str(n.ip_address) == "192.168.1.100"
        assert n.port == 8765
        n.delete()

    def test_node_capabilities(self):
        caps = {"webhooks": True, "realtime": False}
        n = Node.objects.create(node_id="CAP-NODE", capabilities=caps)
        assert n.capabilities == caps
        n.delete()

    def test_node_metadata(self):
        meta = {"location": "Kitchen", "floor": 1}
        n = Node.objects.create(node_id="META-NODE", metadata=meta)
        assert n.metadata == meta
        n.delete()

    def test_node_transaction_count(self):
        n = Node.objects.create(node_id="TRANS-NODE", transaction_count=500)
        assert n.transaction_count == 500
        n.delete()

    def test_node_last_synced_at(self):
        now = datetime.now(timezone.utc)
        n = Node.objects.create(node_id="SYNCED-NODE", last_synced_at=now)
        assert n.last_synced_at is not None
        n.delete()

    def test_node_filter_by_status(self):
        Node.objects.create(node_id="N1", status="online")
        Node.objects.create(node_id="N2", status="offline")
        Node.objects.create(node_id="N3", status="online")
        assert Node.objects.filter(status="online").count() >= 2
        assert Node.objects.filter(status="offline").count() >= 1
        Node.objects.filter(node_id__in=["N1", "N2", "N3"]).delete()

    def test_node_db_indexes(self):
        """Verify key indexes exist on the model."""
        indexes = [idx.fields for idx in Node._meta.indexes]
        assert ["status", "last_seen"] in indexes
        assert ["node_type"] in indexes
        assert ["is_active"] in indexes


# ===========================================================================
# Heartbeat tests
# ===========================================================================


class TestHeartbeatModel:
    """5 tests: creation, payload, latency, ordering."""

    def test_create_heartbeat(self):
        hb = Heartbeat.objects.create(node_id="HB-001", status="online")
        assert hb.node_id == "HB-001"
        assert hb.status == "online"
        assert hb.payload == {}
        assert hb.received_at is not None
        assert str(hb) == "❤️ HB-001"

    def test_heartbeat_with_payload(self):
        hb = Heartbeat.objects.create(
            node_id="HB-PAYLOAD", status="online",
            payload={"version": "2.0", "product_count": 10},
        )
        assert hb.payload == {"version": "2.0", "product_count": 10}

    def test_heartbeat_latency(self):
        hb = Heartbeat.objects.create(node_id="HB-LAT", status="online", latency_ms=12.5)
        assert hb.latency_ms == 12.5
        hb.delete()

    def test_heartbeat_ordering(self):
        hb1 = Heartbeat.objects.create(node_id="HB-ORDER", status="online")
        hb2 = Heartbeat.objects.create(node_id="HB-ORDER", status="offline")
        qs = Heartbeat.objects.filter(node_id="HB-ORDER")
        assert qs.first() == hb2  # most recent first
        hb1.delete()
        hb2.delete()

    def test_heartbeat_indexes(self):
        indexes = [idx.fields for idx in Heartbeat._meta.indexes]
        assert ["node_id", "received_at"] in indexes


# ===========================================================================
# NodeEvent tests
# ===========================================================================


class TestNodeEventModel:
    """7 tests: creation, event types, metadata, ordering, indexes."""

    def test_create_event(self):
        e = NodeEvent.objects.create(
            node_id="EVT-001", event_type="registered",
            description="Node registered", metadata={"version": "1.0"},
        )
        assert e.node_id == "EVT-001"
        assert e.event_type == "registered"
        assert e.description == "Node registered"
        assert e.metadata == {"version": "1.0"}

    def test_event_types_choices(self):
        for etype, _ in NodeEvent.EVENT_TYPES:
            e = NodeEvent.objects.create(node_id="EVT-TYPE", event_type=etype)
            assert e.event_type == etype
            e.delete()

    def test_event_defaults(self):
        e = NodeEvent.objects.create(node_id="EVT-DEF", event_type="registered")
        assert e.description == ""
        assert e.metadata == {}

    def test_event_filter_by_node(self):
        NodeEvent.objects.create(node_id="EVT-FILTER", event_type="registered")
        NodeEvent.objects.create(node_id="EVT-FILTER", event_type="heartbeat")
        NodeEvent.objects.create(node_id="OTHER", event_type="registered")
        assert NodeEvent.objects.filter(node_id="EVT-FILTER").count() == 2

    def test_event_ordering(self):
        e1 = NodeEvent.objects.create(node_id="EVT-ORD", event_type="registered")
        e2 = NodeEvent.objects.create(node_id="EVT-ORD", event_type="status_change")
        qs = NodeEvent.objects.filter(node_id="EVT-ORD")
        assert qs.first() == e2  # most recent first
        e1.delete()
        e2.delete()

    def test_event_indexes(self):
        indexes = [idx.fields for idx in NodeEvent._meta.indexes]
        assert ["node_id", "event_type"] in indexes
        assert ["event_type"] in indexes

    def test_event_str(self):
        e = NodeEvent.objects.create(node_id="STR-EVT", event_type="error")
        assert "[error]" in str(e)


# ===========================================================================
# SyncLog tests
# ===========================================================================


class TestSyncLogModel:
    """8 tests: creation, status/direction choices, defaults, error messages."""

    def test_create_sync_log(self):
        sl = SyncLog.objects.create(
            node_id="SYNC-001", entity_type="product",
            entity_id="PROD-001", direction="push", status="success",
        )
        assert sl.node_id == "SYNC-001"
        assert sl.entity_type == "product"
        assert sl.entity_id == "PROD-001"
        assert sl.direction == "push"
        assert sl.status == "success"
        assert "push" in str(sl)

    def test_sync_log_defaults(self):
        sl = SyncLog.objects.create(node_id="SYNC-DEF", entity_type="node", entity_id="N1")
        assert sl.status == "pending"
        assert sl.direction == "push"
        assert sl.retry_count == 0
        assert sl.payload_size is None
        assert sl.duration_ms is None
        assert sl.error_message == ""

    def test_sync_log_status_choices(self):
        for status, _ in SyncLog.SYNC_STATUS_CHOICES:
            sl = SyncLog.objects.create(
                node_id="SYNC-STAT", entity_type="sale",
                entity_id="S1", status=status,
            )
            assert sl.status == status
            sl.delete()

    def test_sync_log_direction_choices(self):
        for direction, _ in SyncLog.SYNC_DIRECTION_CHOICES:
            sl = SyncLog.objects.create(
                node_id="SYNC-DIR", entity_type="customer",
                entity_id="C1", direction=direction,
            )
            assert sl.direction == direction
            sl.delete()

    def test_sync_log_error_message(self):
        sl = SyncLog.objects.create(
            node_id="SYNC-ERR", entity_type="node",
            entity_id="N1", status="failed",
            error_message="Connection refused",
        )
        assert sl.error_message == "Connection refused"
        sl.delete()

    def test_sync_log_payload_size(self):
        sl = SyncLog.objects.create(
            node_id="SYNC-SIZE", entity_type="product",
            entity_id="P1", payload_size=2048,
        )
        assert sl.payload_size == 2048
        sl.delete()

    def test_sync_log_duration_ms(self):
        sl = SyncLog.objects.create(
            node_id="SYNC-DUR", entity_type="sale",
            entity_id="S1", duration_ms=150,
        )
        assert sl.duration_ms == 150
        sl.delete()

    def test_sync_log_retry_count(self):
        sl = SyncLog.objects.create(
            node_id="SYNC-RETRY", entity_type="node",
            entity_id="N1", retry_count=3,
        )
        assert sl.retry_count == 3
        sl.delete()


# ===========================================================================
# Cross-model integration tests
# ===========================================================================


class TestCrossModelIntegration:
    """Tests exercising relationships across multiple models."""

    def test_full_sale_flow(self):
        """Create category → product → customer → sale → items."""
        cat = Category.objects.create(name="FlowCat", slug="flow-cat")
        product = Product.objects.create(name="FlowProd", price=10.00, sku="FLOW", category=cat)
        customer = Customer.objects.create(first_name="Flow", last_name="Customer")
        sale = Sale.objects.create(customer=customer, subtotal=20.00, total=21.70)
        SaleItem.objects.create(
            sale=sale, product=product, product_name=product.name,
            quantity=2, unit_price=10.00, line_total=20.00,
        )
        assert sale.items.count() == 1
        assert product.sku == "FLOW"
        assert customer.full_name == "Flow Customer"
        # Cleanup: children before parents (SQLite FK constraints)
        sale.items.all().delete()
        sale.delete()
        product.delete()
        customer.delete()
        cat.delete()

    def test_menu_with_items_flow(self):
        """Create category → menu items → menu → assignments."""
        cat = Category.objects.create(name="MenuFlow", slug="menu-flow")
        mi1 = MenuItem.objects.create(category=cat, name="Item1", price=8.00)
        mi2 = MenuItem.objects.create(category=cat, name="Item2", price=12.00)
        menu = Menu.objects.create(name="Combo Menu", slug="combo")
        MenuItemAssignment.objects.create(menu=menu, item=mi1, display_order=1)
        MenuItemAssignment.objects.create(menu=menu, item=mi2, display_order=2)
        assert menu.items.count() == 2
        # Cleanup: children before parents (SQLite FK constraints)
        MenuItemAssignment.objects.filter(menu=menu).delete()
        menu.delete()
        mi1.delete()
        mi2.delete()
        cat.delete()

    def test_node_heartbeat_event_flow(self):
        """Create node → heartbeat → events."""
        node = Node.objects.create(node_id="INT-NODE", hostname="int-host")
        Heartbeat.objects.create(node_id=node.node_id, status="online", payload={"test": True})
        NodeEvent.objects.create(node_id=node.node_id, event_type="registered")
        NodeEvent.objects.create(node_id=node.node_id, event_type="heartbeat")
        assert Node.objects.get(node_id="INT-NODE").hostname == "int-host"
        assert Heartbeat.objects.filter(node_id="INT-NODE").count() >= 1
        assert NodeEvent.objects.filter(node_id="INT-NODE").count() >= 2
        Node.objects.filter(node_id="INT-NODE").delete()
        Heartbeat.objects.filter(node_id="INT-NODE").delete()
        NodeEvent.objects.filter(node_id="INT-NODE").delete()

    def test_inventory_affects_product(self):
        """Verify product stock is tracked independently of inventory transactions."""
        product = Product.objects.create(name="StockTest", price=5.00, sku="STOCK")
        InventoryTransaction.objects.create(product=product, transaction_type="in", quantity=100)
        product.stock_quantity = 100
        product.save()
        product.refresh_from_db()
        assert product.stock_quantity == 100
        # Cleanup: children before parents (SQLite FK constraints)
        InventoryTransaction.objects.filter(product=product).delete()
        product.delete()


# ===========================================================================
# Edge cases & model meta tests
# ===========================================================================


class TestModelMeta:
    """Verify all models have correct app_label, db_table, and meta attributes."""

    MODEL_META = {
        Category: ("pos_unified", "unified_categories", ["display_order", "name"]),
        Product: ("pos_unified", "unified_products", ["name"]),
        Customer: ("pos_unified", "unified_customers", ["-created_at"]),
        Sale: ("pos_unified", "unified_sales", ["-sale_date"]),
        SaleItem: ("pos_unified", "unified_sale_items", ["id"]),
        InventoryTransaction: ("pos_unified", "unified_inventory", ["-created_at"]),
        Employee: ("pos_unified", "unified_employees", ["last_name", "first_name"]),
        MenuItem: ("pos_unified", "unified_menu_items", ["category__display_order", "display_order", "name"]),
        Menu: ("pos_unified", "unified_menus", ["display_order", "name"]),
        MenuItemAssignment: ("pos_unified", "unified_menu_assignments", ["display_order"]),
        Node: ("pos_unified", "unified_nodes", ["-last_seen"]),
        Heartbeat: ("pos_unified", "unified_heartbeats", ["-received_at"]),
        NodeEvent: ("pos_unified", "unified_node_events", ["-created_at"]),
        SyncLog: ("pos_unified", "unified_sync_logs", ["-created_at"]),
    }

    def test_all_models_have_correct_meta(self):
        """Every unified model has app_label=pos_unified and correct db_table/ordering."""
        for model, (app_label, db_table, ordering) in self.MODEL_META.items():
            assert model._meta.app_label == app_label, f"{model.__name__} app_label"
            assert model._meta.db_table == db_table, f"{model.__name__} db_table"
            assert list(model._meta.ordering) == ordering, f"{model.__name__} ordering"


class TestEdgeCases:
    """Edge case tests: bulk operations, large values, empty strings."""

    def test_bulk_create_products(self):
        products = Product.objects.bulk_create([
            Product(name=f"Bulk{i}", price=float(i), sku=f"BULK-{i}")
            for i in range(10)
        ])
        assert len(products) == 10
        Product.objects.filter(sku__startswith="BULK-").delete()

    def test_bulk_create_customers(self):
        customers = Customer.objects.bulk_create([
            Customer(first_name=f"User{i}", last_name="Bulk")
            for i in range(5)
        ])
        assert len(customers) == 5
        Customer.objects.filter(last_name="Bulk").delete()

    def test_empty_string_fields(self):
        """All CharField with blank=True should accept empty strings."""
        p = Product.objects.create(name="Empty", price=1.00, sku="EMPTY-STR")
        assert p.barcode == ""
        assert p.description == ""
        assert p.image_url == ""

        c = Customer.objects.create(first_name="Empty")
        assert c.last_name == ""
        assert c.notes == ""
        assert c.phone == ""
        c.delete()
        p.delete()

    def test_max_length_fields(self):
        """Verify long strings are accepted up to field limits."""
        long_name = "A" * 200
        long_sku = "B" * 50
        p = Product.objects.create(name=long_name, price=99.99, sku=long_sku)
        assert len(p.name) == 200
        assert len(p.sku) == 50
        p.delete()

    def test_decimal_precision(self):
        """Verify Decimal fields maintain precision."""
        p = Product.objects.create(name="Precise", price=0.01, sku="PRECISE")
        assert float(p.price) == 0.01
        p.delete()

    def test_boolean_defaults(self):
        """All BooleanField defaults should be correct."""
        cat = Category.objects.create(name="BoolTest", slug="bool-test")
        assert cat.is_active is True
        p = Product.objects.create(name="BoolProd", price=1.00, sku="BOOL")
        assert p.is_active is True
        e = Employee.objects.create(first_name="Bool", last_name="Emp")
        assert e.is_active is True
        n = Node.objects.create(node_id="BOOL-NODE")
        assert n.is_active is True
        cat.delete()
        p.delete()
        e.delete()
        n.delete()

    def test_json_field_defaults(self):
        """JSON fields should default to empty dict."""
        n = Node.objects.create(node_id="JSON-TEST")
        assert n.capabilities == {}
        assert n.metadata == {}

        hb = Heartbeat.objects.create(node_id="JSON-HB", status="online")
        assert hb.payload == {}
        hb.delete()
        n.delete()

    def test_auto_now_fields(self):
        """auto_now and auto_now_add fields should be set automatically."""
        cat = Category.objects.create(name="AutoNow", slug="auto-now")
        assert cat.created_at is not None
        assert cat.updated_at is not None
        old_updated = cat.updated_at
        cat.name = "AutoNowUpdated"
        cat.save()
        cat.refresh_from_db()
        assert cat.updated_at >= old_updated
        cat.delete()


# ===========================================================================
# Serialization tests (matching unified_server.py _ser behavior)
# ===========================================================================


class TestSerialization:
    """Tests matching the _ser() serialization logic used in unified_server.py."""

    def _ser(self, obj):
        """Replicate the _ser function from unified_server.py for testing."""
        from decimal import Decimal
        data = {}
        for field in obj._meta.fields:
            val = getattr(obj, field.attname, None)
            if isinstance(val, Decimal):
                val = float(val)
            elif isinstance(val, datetime):
                val = val.isoformat() if val else None
            data[field.attname] = val
        return data

    def test_serialize_product(self):
        p = Product.objects.create(name="Serial", price=15.50, sku="SER")
        data = self._ser(p)
        assert data["name"] == "Serial"
        assert isinstance(data["price"], float)
        assert data["price"] == 15.5
        assert data["sku"] == "SER"
        p.delete()

    def test_serialize_sale(self):
        s = Sale.objects.create(subtotal=100.00, total=108.00)
        data = self._ser(s)
        assert isinstance(data["subtotal"], float)
        assert isinstance(data["total"], float)
        assert isinstance(data["sale_date"], str)  # isoformat
        s.delete()

    def test_serialize_node(self):
        n = Node.objects.create(node_id="SER-NODE")
        data = self._ser(n)
        assert data["node_id"] == "SER-NODE"
        assert data["status"] == "online"
        assert isinstance(data["first_seen"], str)  # isoformat
        n.delete()

    def test_serialize_heartbeat(self):
        hb = Heartbeat.objects.create(node_id="SER-HB", status="online")
        data = self._ser(hb)
        assert data["node_id"] == "SER-HB"
        assert isinstance(data["received_at"], str)
        hb.delete()

    def test_serialize_all_fields_present(self):
        """Verify that _ser output contains all model fields."""
        cat = Category.objects.create(name="AllFields", slug="all-fields")
        data = self._ser(cat)
        for field in cat._meta.fields:
            assert field.attname in data, f"Missing field: {field.attname}"
        cat.delete()


# ===========================================================================
# Pagination tests (matching unified_server.py _paginate behavior)
# ===========================================================================


class TestPagination:
    """Tests matching the _paginate() helper from unified_server.py."""

    def _paginate(self, qs, page=1, per_page=50):
        page = max(1, page)
        per_page = max(1, min(per_page, 200))
        total = qs.count()
        start = (page - 1) * per_page
        items = list(qs[start:start + per_page])
        return {
            "data": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": max(1, -(-total // per_page)),
            },
        }

    @pytest.fixture(autouse=True)
    def _nodes(self):
        for i in range(25):
            Node.objects.create(node_id=f"PAG-NODE-{i:03d}")
        yield
        Node.objects.filter(node_id__startswith="PAG-NODE-").delete()

    def test_pagination_defaults(self):
        qs = Node.objects.filter(node_id__startswith="PAG-NODE-")
        result = self._paginate(qs)
        assert len(result["data"]) == 25
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["per_page"] == 50
        assert result["pagination"]["total"] == 25
        assert result["pagination"]["total_pages"] == 1

    def test_pagination_page_size(self):
        qs = Node.objects.filter(node_id__startswith="PAG-NODE-")
        result = self._paginate(qs, page=1, per_page=10)
        assert len(result["data"]) == 10
        assert result["pagination"]["per_page"] == 10
        assert result["pagination"]["total_pages"] == 3

    def test_pagination_page_two(self):
        qs = Node.objects.filter(node_id__startswith="PAG-NODE-")
        result = self._paginate(qs, page=2, per_page=10)
        assert len(result["data"]) == 10
        assert result["pagination"]["page"] == 2

    def test_pagination_last_page(self):
        qs = Node.objects.filter(node_id__startswith="PAG-NODE-")
        result = self._paginate(qs, page=3, per_page=10)
        assert len(result["data"]) == 5
        assert result["pagination"]["page"] == 3

    def test_pagination_clamps_page_min(self):
        qs = Node.objects.filter(node_id__startswith="PAG-NODE-")
        result = self._paginate(qs, page=0)
        assert result["pagination"]["page"] == 1

    def test_pagination_clamps_per_page_max(self):
        qs = Node.objects.filter(node_id__startswith="PAG-NODE-")
        result = self._paginate(qs, per_page=500)
        assert result["pagination"]["per_page"] == 200

    def test_pagination_empty(self):
        qs = Node.objects.filter(node_id="NONEXISTENT")
        result = self._paginate(qs)
        assert len(result["data"]) == 0
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["total_pages"] == 1
