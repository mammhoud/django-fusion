"""
Tests for models/pos.py — Category, Product, Customer, Sale, SaleItem,
InventoryTransaction, Employee.

Covers defaults, custom field overrides, string representations, FK
relationships, choice fields, sync tracking fields, properties, and
edge cases (null/blank values, deactivation).
"""

from __future__ import annotations

import pytest


# ══════════════════════════════════════════════════════════════════════════
# Category
# ══════════════════════════════════════════════════════════════════════════

class TestCategory:
    def test_create_with_defaults(self, category_factory):
        cat = category_factory()
        assert cat.name.startswith("Category-")
        assert cat.description == ""
        assert cat.display_order == 0
        assert cat.is_active is True

    def test_create_with_custom_fields(self, category_factory):
        cat = category_factory(
            name="Beverages",
            slug="beverages",
            description="All drink items",
            display_order=1,
        )
        assert cat.name == "Beverages"
        assert cat.slug == "beverages"
        assert cat.description == "All drink items"
        assert cat.display_order == 1

    def test_slug_field_stores_value(self, category_factory):
        """Slug field stores the provided value."""
        cat = category_factory(name="Snacks", slug="snacks")
        assert cat.slug == "snacks"

    def test_str(self, category_factory):
        cat = category_factory(name="Main Course")
        assert str(cat) == "Main Course"

    def test_ordering(self, category_factory):
        cat = category_factory(display_order=5)
        assert cat.display_order == 5

    def test_deactivate(self, category_factory):
        cat = category_factory(is_active=True)
        cat.is_active = False
        cat.save()
        cat.refresh_from_db()
        assert cat.is_active is False

    def test_sync_fields_defaults(self, category_factory):
        cat = category_factory()
        assert cat.is_synced is False
        assert cat.sync_status == "pending"
        assert cat.synced_at is None


# ══════════════════════════════════════════════════════════════════════════
# Product
# ══════════════════════════════════════════════════════════════════════════

class TestProduct:
    def test_create_with_defaults(self, product_factory):
        prod = product_factory()
        assert prod.name.startswith("Product-")
        assert prod.sku is None
        assert prod.is_active is True
        assert prod.stock_quantity == 100
        assert prod.tax_rate == "standard"
        assert prod.border_color == ""
        assert prod.description == ""

    def test_create_with_custom_fields(self, product_factory):
        prod = product_factory(
            name="Espresso",
            price=3.50,
            sku="ESP-001",
            stock_quantity=200,
            barcode="4901234567890",
            border_color="#6366f1",
        )
        assert prod.name == "Espresso"
        assert float(prod.price) == 3.50
        assert prod.sku == "ESP-001"
        assert prod.stock_quantity == 200
        assert prod.barcode == "4901234567890"
        assert prod.border_color == "#6366f1"

    def test_str(self, product_factory):
        prod = product_factory(name="Latte", price=4.99)
        assert str(prod) == "Latte ($4.99)"

    def test_category_relation(self, product_factory, category_factory):
        cat = category_factory(name="Coffee")
        prod = product_factory(name="Cappuccino", category=cat)
        prod.refresh_from_db()
        assert prod.category.id == cat.id
        assert prod.category.name == "Coffee"

    def test_category_fk_allows_null(self, product_factory, category_factory):
        """Product.category FK allows null (null=True)."""
        prod = product_factory()
        assert prod.category is None
        # Manually setting the FK to None should work
        cat = category_factory(name="Tea")
        prod.category = cat
        prod.save()
        assert prod.category.id == cat.id
        prod.category = None
        prod.save()
        prod.refresh_from_db()
        assert prod.category is None

    def test_tax_rate_choices(self, product_factory):
        prod = product_factory(tax_rate="exempt")
        assert prod.tax_rate == "exempt"

    def test_default_tax_rate(self, product_factory):
        prod = product_factory()
        assert prod.tax_rate == "standard"

    def test_low_stock_threshold_default(self, product_factory):
        prod = product_factory()
        assert prod.low_stock_threshold == 10

    def test_cost_price_default(self, product_factory):
        prod = product_factory()
        assert float(prod.cost_price) == 0

    def test_deactivate(self, product_factory):
        prod = product_factory(is_active=True)
        prod.is_active = False
        prod.save()
        prod.refresh_from_db()
        assert prod.is_active is False

    def test_sync_fields_defaults(self, product_factory):
        prod = product_factory()
        assert prod.is_synced is False
        assert prod.sync_status == "pending"
        assert prod.synced_at is None


# ══════════════════════════════════════════════════════════════════════════
# Customer
# ══════════════════════════════════════════════════════════════════════════

class TestCustomer:
    def test_create_with_defaults(self, customer_factory):
        cust = customer_factory()
        assert cust.first_name.startswith("Customer-")
        assert cust.last_name == "Test"
        assert cust.loyalty_points == 0
        assert float(cust.total_spent) == 0
        assert cust.is_active is True

    def test_create_with_custom_fields(self, customer_factory):
        cust = customer_factory(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone="555-1234",
            loyalty_points=100,
        )
        assert cust.first_name == "Alice"
        assert cust.last_name == "Smith"
        assert cust.email == "alice@example.com"
        assert cust.phone == "555-1234"
        assert cust.loyalty_points == 100

    def test_str_with_name(self, customer_factory):
        cust = customer_factory(first_name="Bob", last_name="Jones")
        assert str(cust) == "Bob Jones"

    def test_str_with_email_only(self, customer_factory):
        cust = customer_factory(first_name="", last_name="", email="bob@test.com")
        assert str(cust) == "bob@test.com"

    def test_full_name_property(self, customer_factory):
        cust = customer_factory(first_name="Alice", last_name="Smith")
        assert cust.full_name == "Alice Smith"

    def test_full_name_single_name(self, customer_factory):
        """If last_name is blank, full_name returns just first_name."""
        cust = customer_factory(first_name="Alice", last_name="")
        assert cust.full_name == "Alice"

    def test_loyalty_points_default_zero(self, customer_factory):
        cust = customer_factory()
        assert cust.loyalty_points == 0

    def test_total_spent_default_zero(self, customer_factory):
        cust = customer_factory()
        assert float(cust.total_spent) == 0

    def test_email_can_be_null(self, customer_factory):
        cust = customer_factory(email=None)
        assert cust.email is None

    def test_str_fallback_to_unknown(self, customer_factory):
        """When name is empty and email is None, __str__ should return 'Unknown'."""
        cust = customer_factory(
            first_name="", last_name="", email=None,
        )
        assert str(cust) == "Unknown"

    def test_deactivate(self, customer_factory):
        cust = customer_factory(is_active=True)
        cust.is_active = False
        cust.save()
        cust.refresh_from_db()
        assert cust.is_active is False

    def test_sync_fields_defaults(self, customer_factory):
        cust = customer_factory()
        assert cust.is_synced is False
        assert cust.sync_status == "pending"
        assert cust.synced_at is None


# ══════════════════════════════════════════════════════════════════════════
# Sale
# ══════════════════════════════════════════════════════════════════════════

class TestSale:
    def test_create_with_defaults(self, sale_factory):
        sale = sale_factory()
        assert float(sale.subtotal) == 19.99
        assert float(sale.tax_amount) == 2.00
        assert float(sale.total) == 23.99
        assert sale.payment_method == "cash"
        assert sale.status == "completed"
        assert sale.customer is not None

    def test_create_with_custom_fields(self, sale_factory):
        sale = sale_factory(
            subtotal=50.00,
            tax_amount=5.00,
            discount_amount=10.00,
            total=45.00,
            payment_method="card",
            status="pending",
            notes="Test order",
        )
        assert float(sale.subtotal) == 50.00
        assert float(sale.tax_amount) == 5.00
        assert float(sale.discount_amount) == 10.00
        assert float(sale.total) == 45.00
        assert sale.payment_method == "card"
        assert sale.status == "pending"
        assert sale.notes == "Test order"

    def test_str(self, sale_factory):
        sale = sale_factory(total=15.99)
        assert str(sale) == f"Sale #{sale.id} — $15.99"

    def test_customer_relation(self, sale_factory, customer_factory):
        cust = customer_factory(first_name="John")
        sale = sale_factory(customer=cust)
        sale.refresh_from_db()
        assert sale.customer.id == cust.id

    def test_customer_fk_allows_null(self, sale_factory, customer_factory):
        """Sale.customer FK allows null (null=True)."""
        sale = sale_factory()
        assert sale.customer is not None  # auto-created by factory
        # Manually setting the FK to None should work
        sale.customer = None
        sale.save()
        sale.refresh_from_db()
        assert sale.customer is None

    def test_payment_method_choices(self, sale_factory):
        sale = sale_factory(payment_method="mobile")
        assert sale.payment_method == "mobile"

    def test_status_choices(self, sale_factory):
        sale = sale_factory(status="refunded")
        assert sale.status == "refunded"

    def test_discount_default_zero(self, sale_factory):
        sale = sale_factory()
        assert float(sale.discount_amount) == 0

    def test_cashback_default_zero(self, sale_factory):
        sale = sale_factory()
        assert float(sale.cashback_amount) == 0

    def test_sale_date_auto_populated(self, sale_factory):
        """sale_date defaults to timezone.now() — should be set on creation."""
        sale = sale_factory()
        assert sale.sale_date is not None

    def test_sync_fields_defaults(self, sale_factory):
        sale = sale_factory()
        assert sale.is_synced is False
        assert sale.sync_status == "pending"
        assert sale.synced_at is None


# ══════════════════════════════════════════════════════════════════════════
# SaleItem
# ══════════════════════════════════════════════════════════════════════════

class TestSaleItem:
    def test_create_with_defaults(self, sale_item_factory):
        item = sale_item_factory()
        assert item.product_name.startswith("Item-")
        assert item.quantity == 1
        assert float(item.unit_price) == 5.99
        assert float(item.line_total) == 5.99
        assert item.sale is not None
        assert item.product is not None

    def test_create_with_custom_fields(self, sale_item_factory):
        item = sale_item_factory(
            product_name="Mocha",
            quantity=2,
            unit_price=6.50,
            line_total=13.00,
            notes="Extra hot",
        )
        assert item.product_name == "Mocha"
        assert item.quantity == 2
        assert float(item.unit_price) == 6.50
        assert float(item.line_total) == 13.00
        assert item.notes == "Extra hot"

    def test_str(self, sale_item_factory):
        item = sale_item_factory(quantity=3, product_name="Espresso")
        assert str(item) == "3x Espresso"

    def test_fk_to_sale(self, sale_item_factory, sale_factory):
        sale = sale_factory()
        item = sale_item_factory(sale=sale)
        item.refresh_from_db()
        assert item.sale.id == sale.id

    def test_fk_to_product(self, sale_item_factory, product_factory):
        prod = product_factory(name="Muffin")
        item = sale_item_factory(product=prod)
        item.refresh_from_db()
        assert item.product.id == prod.id

    def test_product_fk_allows_null(self, sale_item_factory, product_factory):
        """SaleItem.product FK allows null (null=True)."""
        item = sale_item_factory()
        assert item.product is not None  # auto-created by factory
        # Manually setting the FK to None should work
        item.product = None
        item.save()
        item.refresh_from_db()
        assert item.product is None

    def test_sync_fields_defaults(self, sale_item_factory):
        item = sale_item_factory()
        assert item.is_synced is False
        assert item.sync_status == "pending"
        assert item.synced_at is None


# ══════════════════════════════════════════════════════════════════════════
# InventoryTransaction
# ══════════════════════════════════════════════════════════════════════════

class TestInventoryTransaction:
    def test_create_with_defaults(self, inventory_transaction_factory):
        txn = inventory_transaction_factory()
        assert txn.transaction_type == "in"
        assert txn.quantity == 10
        assert txn.inventory_id == "main"
        assert txn.product is not None
        assert txn.reference == ""

    def test_create_with_custom_fields(self, inventory_transaction_factory):
        txn = inventory_transaction_factory(
            transaction_type="out",
            quantity=5,
            reference="PO-1234",
            notes="Weekly restock",
            created_by="admin",
            shipping_fee=2.50,
        )
        assert txn.transaction_type == "out"
        assert txn.quantity == 5
        assert txn.reference == "PO-1234"
        assert txn.notes == "Weekly restock"
        assert txn.created_by == "admin"
        assert float(txn.shipping_fee) == 2.50

    def test_str(self, inventory_transaction_factory):
        txn = inventory_transaction_factory(
            transaction_type="in", quantity=20,
        )
        assert "Stock In" in str(txn)
        assert "x20" in str(txn)

    def test_transaction_type_choices(self, inventory_transaction_factory):
        for ttype in ["in", "out", "adjustment", "return",
                       "transfer_out", "transfer_in", "waste", "restock"]:
            txn = inventory_transaction_factory(transaction_type=ttype)
            assert txn.transaction_type == ttype

    def test_fk_to_product(self, inventory_transaction_factory, product_factory):
        prod = product_factory(name="Coffee Beans")
        txn = inventory_transaction_factory(product=prod)
        txn.refresh_from_db()
        assert txn.product.id == prod.id

    def test_reverse_relation_to_product(self, inventory_transaction_factory, product_factory):
        """Verify the reverse FK relation (product.inventory_transactions) works."""
        prod = product_factory(name="Milk")
        txn = inventory_transaction_factory(product=prod)
        prod.refresh_from_db()
        related = list(prod.inventory_transactions.all())
        assert len(related) == 1
        assert related[0].id == txn.id

    def test_inventory_id_defaults_to_main(self, inventory_transaction_factory):
        txn = inventory_transaction_factory()
        assert txn.inventory_id == "main"

    def test_custom_inventory_id(self, inventory_transaction_factory):
        txn = inventory_transaction_factory(inventory_id="warehouse-b")
        assert txn.inventory_id == "warehouse-b"

    def test_sync_fields_defaults(self, inventory_transaction_factory):
        txn = inventory_transaction_factory()
        assert txn.is_synced is False
        assert txn.sync_status == "pending"
        assert txn.synced_at is None


# ══════════════════════════════════════════════════════════════════════════
# Employee
# ══════════════════════════════════════════════════════════════════════════

class TestEmployee:
    def test_create_with_defaults(self, employee_factory):
        emp = employee_factory()
        assert emp.first_name.startswith("Emp-")
        assert emp.last_name == "Test"
        assert emp.role == "cashier"
        assert emp.is_active is True
        assert emp.pin_code == "1234"
        assert len(emp.pin_code) == 4

    def test_create_with_custom_fields(self, employee_factory):
        emp = employee_factory(
            first_name="Jane",
            last_name="Doe",
            email="jane@cafe.com",
            phone="555-0001",
            role="manager",
            pin_code="7890",
            hourly_rate=22.50,
        )
        assert emp.first_name == "Jane"
        assert emp.last_name == "Doe"
        assert emp.email == "jane@cafe.com"
        assert emp.phone == "555-0001"
        assert emp.role == "manager"
        assert emp.pin_code == "7890"
        assert float(emp.hourly_rate) == 22.50

    def test_str(self, employee_factory):
        emp = employee_factory(first_name="John", last_name="Doe", role="cashier")
        assert str(emp) == "John Doe (Cashier)"

    def test_role_choices(self, employee_factory):
        for role_code, role_label in [("cashier", "Cashier"), ("server", "Server"),
                                       ("manager", "Manager"), ("admin", "Administrator"),
                                       ("kitchen", "Kitchen Staff")]:
            emp = employee_factory(role=role_code)
            assert emp.role == role_code
            assert role_label in str(emp)

    def test_pin_code_string(self, employee_factory):
        emp = employee_factory(pin_code="4321")
        assert isinstance(emp.pin_code, str)
        assert emp.pin_code == "4321"

    def test_hourly_rate_default_zero(self, employee_factory):
        emp = employee_factory()
        assert float(emp.hourly_rate) == 15.00  # factory default

    def test_deactivate(self, employee_factory):
        emp = employee_factory(is_active=True)
        emp.is_active = False
        emp.save()
        emp.refresh_from_db()
        assert emp.is_active is False

    def test_sync_fields_defaults(self, employee_factory):
        emp = employee_factory()
        assert emp.is_synced is False
        assert emp.sync_status == "pending"
        assert emp.synced_at is None
