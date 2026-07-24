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
