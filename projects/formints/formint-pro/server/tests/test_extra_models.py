"""
Tests for models/extra.py — Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment.

Uses factory fixtures from conftest.py and Django TestCase for DB isolation.
Covers CRUD, business logic (save() overrides, auto-population), string
representations, sync fields, and edge cases.
"""

from __future__ import annotations

import pytest


# ══════════════════════════════════════════════════════════════════════════
# Ingredient
# ══════════════════════════════════════════════════════════════════════════

class TestIngredient:
    def test_create_with_defaults(self, ingredient_factory):
        ing = ingredient_factory()
        assert ing.name.startswith("Ingredient-")
        assert ing.unit == "kg"
        assert ing.is_active is True
        assert ing.current_quantity == 10.0

    def test_create_with_custom_fields(self, ingredient_factory):
        ing = ingredient_factory(
            name="Coffee Beans", unit="kg",
            current_quantity=25.5, cost_per_unit=12.00,
        )
        assert ing.name == "Coffee Beans"
        assert float(ing.current_quantity) == 25.5
        assert float(ing.cost_per_unit) == 12.00

    def test_str(self, ingredient_factory):
        ing = ingredient_factory(name="Milk", unit="liter")
        assert str(ing) == "Milk (liter)"

    def test_reorder_fields(self, ingredient_factory):
        ing = ingredient_factory(
            reorder_level=5.0, reorder_quantity=20.0,
        )
        assert float(ing.reorder_level) == 5.0
        assert float(ing.reorder_quantity) == 20.0

    def test_sync_fields_defaults(self, ingredient_factory):
        ing = ingredient_factory()
        assert ing.is_synced is False
        assert ing.sync_status == "pending"
        assert ing.synced_at is None

    def test_deactivate(self, ingredient_factory):
        ing = ingredient_factory(is_active=True)
        ing.is_active = False
        ing.save()
        ing.refresh_from_db()
        assert ing.is_active is False


# ══════════════════════════════════════════════════════════════════════════
# Recipe
# ══════════════════════════════════════════════════════════════════════════

class TestRecipe:
    def test_create_with_defaults(self, recipe_factory):
        recipe = recipe_factory()
        assert recipe.name.startswith("Recipe-")
        assert recipe.is_active is True
        assert recipe.yield_quantity == 1
        assert recipe.product is not None

    def test_create_with_explicit_product(self, recipe_factory, product_factory):
        prod = product_factory(name="Espresso")
        recipe = recipe_factory(product=prod, name="Espresso Recipe")
        assert recipe.product.id == prod.id
        assert recipe.name == "Espresso Recipe"

    def test_str_with_name(self, recipe_factory):
        recipe = recipe_factory(name="Latte Recipe")
        assert str(recipe) == "Latte Recipe"

    def test_save_auto_derives_name_from_product(self, recipe_factory, product_factory):
        """When name is empty, save() auto-derives it as 'Recipe: <product name>'."""
        prod = product_factory(name="Smoothie")
        recipe = recipe_factory(product=prod, name="")
        recipe.refresh_from_db()
        assert recipe.name == "Recipe: Smoothie"
        assert str(recipe) == "Recipe: Smoothie"

    def test_reverse_relation_deletes_recipes(self, recipe_factory, product_factory):
        """Verify the reverse FK relation (product.recipes) works and
        recipes can be deleted via the product's related manager.
        """
        prod = product_factory(name="Smoothie")
        recipe = recipe_factory(product=prod)
        pid = recipe.id
        # Verify FK points to the product
        assert recipe.product_id == prod.id
        # Delete via the product's FK relationship
        prod.recipes.all().delete()
        from models.extra import Recipe
        assert Recipe.objects.filter(id=pid).count() == 0

    def test_instructions_and_yield(self, recipe_factory):
        recipe = recipe_factory(
            instructions="Step 1: Brew. Step 2: Serve.",
            yield_quantity=2,
        )
        assert "Step 1" in recipe.instructions
        assert recipe.yield_quantity == 2


# ══════════════════════════════════════════════════════════════════════════
# ReceiptTemplate
# ══════════════════════════════════════════════════════════════════════════

class TestReceiptTemplate:
    def test_create_with_defaults(self, receipt_template_factory):
        tpl = receipt_template_factory()
        assert tpl.name.startswith("Template-")
        assert tpl.is_default is False
        assert tpl.is_active is True

    def test_create_with_template_html(self, receipt_template_factory):
        html = "<h1>{{restaurant_name}}</h1><p>{{date}}</p>"
        tpl = receipt_template_factory(
            name="Modern Print",
            template_html=html,
            template_css="body { font-family: sans-serif; }",
        )
        assert tpl.name == "Modern Print"
        assert "{{restaurant_name}}" in tpl.template_html
        assert "sans-serif" in tpl.template_css

    def test_make_default(self, receipt_template_factory):
        tpl = receipt_template_factory(is_default=True)
        assert tpl.is_default is True

    def test_str(self, receipt_template_factory):
        tpl = receipt_template_factory(name="Thermal 80mm")
        assert str(tpl) == "Thermal 80mm"

    def test_unique_name_enforced(self, receipt_template_factory):
        receipt_template_factory(name="Duplicate")
        from django.db import IntegrityError
        from models.extra import ReceiptTemplate
        with pytest.raises(IntegrityError):
            ReceiptTemplate.objects.create(name="Duplicate")


# ══════════════════════════════════════════════════════════════════════════
# Role
# ══════════════════════════════════════════════════════════════════════════

class TestRole:
    def test_create_with_defaults(self, role_factory):
        role = role_factory()
        assert role.name.startswith("Role-")
        assert role.is_active is True

    def test_permissions_json(self, role_factory):
        role = role_factory(
            permissions={
                "can_manage_products": True,
                "can_process_sales": True,
                "can_access_reports": False,
            }
        )
        assert role.permissions["can_manage_products"] is True
        assert role.permissions["can_access_reports"] is False

    def test_empty_permissions(self, role_factory):
        role = role_factory(permissions={})
        assert role.permissions == {}

    def test_str(self, role_factory):
        role = role_factory(name="Manager")
        assert str(role) == "Manager"

    def test_description(self, role_factory):
        role = role_factory(
            description="Full access to POS operations",
        )
        assert "Full access" in role.description

    def test_deactivate(self, role_factory):
        role = role_factory(is_active=True)
        role.is_active = False
        role.save()
        role.refresh_from_db()
        assert role.is_active is False

    def test_unique_name_enforced(self, role_factory):
        role_factory(name="Admin-Role")
        from django.db import IntegrityError
        from models.extra import Role
        with pytest.raises(IntegrityError):
            Role.objects.create(name="Admin-Role")


# ══════════════════════════════════════════════════════════════════════════
# InventoryAdjustment
# ══════════════════════════════════════════════════════════════════════════

class TestInventoryAdjustment:
    def test_create_with_defaults(self, inventory_adjustment_factory):
        adj = inventory_adjustment_factory()
        assert adj.adjustment_type == "addition"
        assert adj.reason == "correction"
        assert adj.ingredient is not None
        assert adj.notes == "Test adjustment"

    def test_save_populates_previous_quantity(self, inventory_adjustment_factory):
        """Verify that save() auto-populates previous_quantity from ingredient."""
        adj = inventory_adjustment_factory(quantity=5)
        assert adj.previous_quantity is not None
        # ingredient was created with current_quantity=50
        assert float(adj.previous_quantity) == 50.0

    def test_save_computes_new_quantity(self, inventory_adjustment_factory):
        """Verify that new_quantity = previous_quantity + quantity."""
        adj = inventory_adjustment_factory(quantity=5)
        assert adj.new_quantity is not None
        expected = float(adj.previous_quantity) + 5
        assert float(adj.new_quantity) == expected

    def test_removal_adjustment(self, inventory_adjustment_factory):
        """Negative quantity reduces stock."""
        adj = inventory_adjustment_factory(quantity=-3, adjustment_type="removal")
        expected = float(adj.previous_quantity) - 3
        assert float(adj.new_quantity) == expected

    def test_save_updates_ingredient_stock(self, inventory_adjustment_factory):
        """Verify save() updates the ingredient's current_quantity."""
        adj = inventory_adjustment_factory(quantity=10)
        adj.ingredient.refresh_from_db()
        assert float(adj.ingredient.current_quantity) == float(adj.new_quantity)

    def test_str(self, inventory_adjustment_factory):
        adj = inventory_adjustment_factory()
        assert "addition" in str(adj).lower()
        assert adj.ingredient.name in str(adj)

    def test_notes_and_created_by(self, inventory_adjustment_factory):
        adj = inventory_adjustment_factory(
            notes="Year-end inventory correction",
            created_by="admin",
        )
        assert "inventory correction" in adj.notes
        assert adj.created_by == "admin"

    def test_multiple_adjustments_accumulate(self, inventory_adjustment_factory, ingredient_factory):
        """Multiple adjustments to the same ingredient accumulate."""
        ing = ingredient_factory(current_quantity=100.0)
        adj1 = inventory_adjustment_factory(ingredient=ing, quantity=10)
        adj2 = inventory_adjustment_factory(ingredient=ing, quantity=-5)
        ing.refresh_from_db()
        # 100 + 10 - 5 = 105
        assert float(ing.current_quantity) == 105.0


# ══════════════════════════════════════════════════════════════════════════
# POS/HR/CRM resource persistence (frontend modal create payloads)

from decimal import Decimal as _D


class TestFrontendModalCreatePayloadsPersist:
    """Seed the six Formint Pro resources and assert create payloads the
    frontend modals send actually persist, mirroring the payloads in
    frontend/src/tests/create-forms.contract.test.ts § 7.

    Supplier:   name, contact_name, phone, email, address, tax_id,
                payment_terms, is_active
    Role:       name, description, permissions, is_active
    Schedule:   employee, day_of_week, start_time, end_time, status, notes
    Payroll:    employee, period_start, period_end, regular_hours,
                overtime_hours, base_salary, bonuses, deductions, notes
    Note:       title, content, status, reference_type, reference_id, created_by
    Recipe:     product, name, instructions, yield_quantity, is_active
    Ingredient: name, unit, current_quantity, reorder_level,
               reorder_quantity, cost_per_unit, is_active
    """

    # ── Supplier (pos/suppliers/index.astro modal payload) ─────────────────

    def test_supplier_create_payload_persists(self, django_bootstrap):
        from models.inventory import Supplier
        s = Supplier.objects.create(
            name="North Bean Supply",
            contact_name="Mara Ellison",
            phone="+1 555-0100",
            email="mara@northbean.example",
            address="1200 Roast Rd",
            tax_id="TE-9981",
            payment_terms="Net 30",
            is_active=True,
        )
        s.refresh_from_db()
        assert s.name == "North Bean Supply"
        assert s.contact_name == "Mara Ellison"
        assert s.phone == "+1 555-0100"
        assert s.email == "mara@northbean.example"
        assert s.address == "1200 Roast Rd"
        assert s.tax_id == "TE-9981"
        assert s.payment_terms == "Net 30"
        assert s.is_active is True

    # ── Role (hr/roles/index.astro modal payload) ───────────────────────────

    def test_role_create_payload_persists(self, django_bootstrap):
        from models.extra import Role
        r = Role.objects.create(
            name="Back Office",
            description="HR + payroll + notes access",
            permissions={
                "can_manage_roles": True,
                "can_manage_payroll": True,
                "can_manage_notes": True,
            },
            is_active=True,
        )
        r.refresh_from_db()
        assert r.name == "Back Office"
        assert r.description == "HR + payroll + notes access"
        assert r.permissions["can_manage_roles"] is True
        assert r.permissions["can_manage_payroll"] is True
        assert r.is_active is True

    # ── EmployeeSchedule (hr/schedules/index.astro modal payload) ───────────

    def test_schedule_create_payload_persists(self, django_bootstrap):
        from models.pos import Employee
        from models.hr import EmployeeSchedule
        emp = Employee.objects.create(
            first_name="Priya", last_name="Nair",
            email="priya@pos.example", role="cashier",
        )
        sched = EmployeeSchedule.objects.create(
            employee=emp,
            day_of_week="monday",
            start_time="09:00",
            end_time="17:00",
            status="scheduled",
            notes="Morning register shift",
        )
        sched.refresh_from_db()
        assert sched.employee_id == emp.id
        assert sched.day_of_week == "monday"
        assert sched.start_time == "09:00"
        assert sched.end_time == "17:00"
        assert sched.status == "scheduled"
        assert sched.notes == "Morning register shift"

    # ── Payroll (hr/payroll/index.astro modal payload) ──────────────────────

    def test_payroll_create_payload_persists(self, django_bootstrap):
        from models.pos import Employee
        from models.hr import Payroll
        emp = Employee.objects.create(
            first_name="Dan", last_name="Osei",
            email="dan@pos.example", role="cook",
        )
        pay = Payroll.objects.create(
            employee=emp,
            period_start="2026-09-01",
            period_end="2026-09-15",
            regular_hours=_D("80.00"),
            overtime_hours=_D("4.00"),
            base_salary=_D("1200.00"),
            bonuses=_D("100.00"),
            deductions=_D("50.00"),
            notes="September half-month",
        )
        pay.refresh_from_db()
        assert pay.employee_id == emp.id
        assert pay.period_start == "2026-09-01"
        assert pay.period_end == "2026-09-15"
        assert float(pay.regular_hours) == 80.00
        assert float(pay.overtime_hours) == 4.00
        assert float(pay.base_salary) == 1200.00
        assert float(pay.bonuses) == 100.00
        assert float(pay.deductions) == 50.00
        assert pay.notes == "September half-month"

    # ── Note (admin/notes/index.astro modal payload) ────────────────────────

    def test_note_create_payload_persists(self, django_bootstrap):
        from models.notes import Note
        n = Note.objects.create(
            title="Shift discrepancy",
            content="Drawer short by $4.20 at close of shift #12.",
            status="open",
            reference_type="shift",
            reference_id=12,
            created_by="cashier",
        )
        n.refresh_from_db()
        assert n.title == "Shift discrepancy"
        assert n.content == "Drawer short by $4.20 at close of shift #12."
        assert n.status == "open"
        assert n.reference_type == "shift"
        assert n.reference_id == 12
        assert n.created_by == "cashier"

    # ── Recipe + Ingredient (kitchen/recipes/index.astro dual-tab modal) ───

    def test_recipe_and_ingredient_create_payloads_persist(self, django_bootstrap):
        from models.pos import Product
        from models.extra import Recipe, Ingredient
        prod = Product.objects.create(
            name="Carrot Cake", price=_D("6.50"), stock_quantity=12,
        )
        recipe = Recipe.objects.create(
            product=prod,
            name="Carrot Cake",
            instructions="Cream cheese frosting, bake 35 min at 175C.",
            yield_quantity=12,
            is_active=True,
        )
        recipe.refresh_from_db()
        assert recipe.product_id == prod.id
        assert recipe.name == "Carrot Cake"
        assert recipe.instructions == "Cream cheese frosting, bake 35 min at 175C."
        assert recipe.yield_quantity == 12
        assert recipe.is_active is True

        ing = Ingredient.objects.create(
            name="Carrot",
            unit="kg",
            current_quantity=_D("25.0"),
            reorder_level=_D("5.0"),
            reorder_quantity=_D("10.0"),
            cost_per_unit=_D("1.20"),
            is_active=True,
        )
        ing.refresh_from_db()
        assert ing.name == "Carrot"
        assert ing.unit == "kg"
        assert float(ing.current_quantity) == 25.0
        assert float(ing.reorder_level) == 5.0
        assert float(ing.reorder_quantity) == 10.0
        assert float(ing.cost_per_unit) == 1.20
        assert ing.is_active is True
        assert Recipe.objects.filter(id=recipe.id).exists()
        assert Ingredient.objects.filter(id=ing.id).exists()
