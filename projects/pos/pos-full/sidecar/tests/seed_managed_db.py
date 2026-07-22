#!/usr/bin/env python3
"""
Seed the managed Django ORM tables (full_*) with sample data for development.

Seeds all 5 new managed models:
  - Ingredient (8 items)
  - Recipe (7 recipes linked to products)
  - ReceiptTemplate (3 templates)
  - Role (5 roles with permission sets)
  - InventoryAdjustment (4 adjustments linked to ingredients)

Also seeds dependency models (Category, Product) if they are empty,
so that Recipe (FK → Product) and InventoryAdjustment (FK → Ingredient)
can reference existing rows.

Usage:
    # Basic: seed if tables are empty
    python3 tests/seed_managed_db.py

    # Force re-seed (delete and recreate)
    python3 tests/seed_managed_db.py --force

    # Seed only specific models
    python3 tests/seed_managed_db.py --models ingredient,role

    # Dry run (print what would be done)
    python3 tests/seed_managed_db.py --dry-run

    # Use a specific database path
    python3 tests/seed_managed_db.py --db /path/to/restaurant.db

Requires Django ORM bootstrap (same as server.py/manage.py).
The script auto-detects whether tables exist and skips seeding
already-populated models unless --force is given.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal

# ── Path setup ───────────────────────────────────────────────────────────────
_PATH = Path(__file__).resolve().parent
_SIDECAR_DIR = _PATH.parent  # sidecar/ (contains configs/, models/, etc.)
for _p in (_PATH, _SIDECAR_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# ── Argument parsing (before Django bootstrap so --help is fast) ──────────────

parser = argparse.ArgumentParser(
    description="Seed managed Django ORM tables (full_*) with sample data.",
)
parser.add_argument("--force", action="store_true",
                     help="Delete existing data and re-seed")
parser.add_argument("--dry-run", action="store_true",
                     help="Print actions without executing")
parser.add_argument("--db", type=str, default=None,
                     help="Path to restaurant.db (default: auto-detect)")
parser.add_argument("--models", type=str, default="",
                     help="Comma-separated list of models to seed "
                          "(ingredient,recipe,receipttemplate,role,inventoryadjustment)")
parser.add_argument("--verbose", action="store_true",
                     help="Print detailed creation info")

args = parser.parse_args()

# Ensure --db is a Path if given
DB_PATH: Path | None = Path(args.db).resolve() if args.db else None

# ── Django ORM bootstrap ────────────────────────────────────────────────────

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manage_settings")

import django
from django.conf import settings

if not settings.configured:
    from configs import (
        DEBUG, DATABASES, INSTALLED_APPS, MIDDLEWARE,
        TEMPLATES, ROOT_URLCONF, SECRET_KEY,
        DEFAULT_AUTO_FIELD, USE_TZ, STATIC_URL, STATIC_ROOT,
    )
    if DB_PATH:
        DATABASES["default"]["NAME"] = str(DB_PATH)
    settings.configure(
        DEBUG=DEBUG,
        DATABASES=DATABASES,
        INSTALLED_APPS=INSTALLED_APPS,
        MIDDLEWARE=MIDDLEWARE,
        TEMPLATES=TEMPLATES,
        ROOT_URLCONF=ROOT_URLCONF,
        SECRET_KEY=SECRET_KEY,
        DEFAULT_AUTO_FIELD=DEFAULT_AUTO_FIELD,
        USE_TZ=USE_TZ,
        STATIC_URL=STATIC_URL,
        STATIC_ROOT=STATIC_ROOT,
    )

django.setup()

# ── Imports (must come after django.setup) ──────────────────────────────────

from django.db import connection

from models.extra import (
    Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment,
)
from models.pos import Category, Product


# ── Helpers ──────────────────────────────────────────────────────────────────

_now = datetime.now(timezone.utc)


def log(msg: str) -> None:
    print(f"  {msg}")


def verbose(msg: str) -> None:
    if args.verbose:
        print(f"    {msg}")


def dry_or_create(model, **kwargs) -> object | None:
    """Create a model instance or skip if exists (unless --force).

    Uses the passed kwargs as both the lookup filter and the creation fields.
    Returns the created (or existing) instance, or ``None`` in dry-run mode.
    """
    if args.dry_run:
        verbose(f"[DRY-RUN] Would create {model.__name__}: {kwargs}")
        return None

    existing = model.objects.filter(**kwargs).first()
    if existing:
        if args.force:
            verbose(f"Deleting existing {model.__name__}: {kwargs}")
            existing.delete()
        else:
            verbose(f"Skipping existing {model.__name__}: {kwargs}")
            return existing

    obj = model.objects.create(**kwargs)
    verbose(f"Created {model.__name__}: {obj}")
    return obj


# ── Seeding Functions ────────────────────────────────────────────────────────

_seeded_models: list[str] = []


def _has_data(model) -> bool:
    return model.objects.count() > 0


def seed_categories() -> None:
    """Seed categories if empty."""
    if _has_data(Category) and not args.force:
        log(f"Categories: {Category.objects.count()} existing, skipping")
        return
    if args.force:
        Category.objects.all().delete()
        log("Categories: cleared (--force)")

    data = [
        {"name": "Hot Drinks", "slug": "hot-drinks", "display_order": 1},
        {"name": "Cold Drinks", "slug": "cold-drinks", "display_order": 2},
        {"name": "Pastries", "slug": "pastries", "display_order": 3},
        {"name": "Sandwiches", "slug": "sandwiches", "display_order": 4},
        {"name": "Desserts", "slug": "desserts", "display_order": 5},
    ]
    for item in data:
        dry_or_create(Category, **item)

    log(f"Categories: {Category.objects.count()} seeded")
    _seeded_models.append("Category")


def seed_products() -> None:
    """Seed products if empty (depends on categories)."""
    if _has_data(Product) and not args.force:
        log(f"Products: {Product.objects.count()} existing, skipping")
        return
    if args.force:
        Product.objects.all().delete()
        log("Products: cleared (--force)")

    cats = {c.name: c for c in Category.objects.all()}

    data = [
        {"name": "Cappuccino", "sku": "CAP-001", "price": Decimal("4.50"),
         "category": cats.get("Hot Drinks"), "stock_quantity": 50,
         "cost_price": Decimal("1.80"), "description": "Classic Italian cappuccino with steamed milk foam"},
        {"name": "Espresso", "sku": "ESP-001", "price": Decimal("3.00"),
         "category": cats.get("Hot Drinks"), "stock_quantity": 100,
         "cost_price": Decimal("1.00"), "description": "Single shot of rich espresso"},
        {"name": "Iced Latte", "sku": "ICL-001", "price": Decimal("5.50"),
         "category": cats.get("Cold Drinks"), "stock_quantity": 30,
         "cost_price": Decimal("2.20"), "description": "Cold latte over ice"},
        {"name": "Chocolate Muffin", "sku": "MUF-001", "price": Decimal("3.75"),
         "category": cats.get("Pastries"), "stock_quantity": 25,
         "cost_price": Decimal("1.50"), "description": "Rich double-chocolate muffin"},
        {"name": "Chicken Sandwich", "sku": "CS-001", "price": Decimal("8.50"),
         "category": cats.get("Sandwiches"), "stock_quantity": 20,
         "cost_price": Decimal("3.40"), "description": "Grilled chicken sandwich with lettuce and tomato"},
        {"name": "Cheesecake", "sku": "CHK-001", "price": Decimal("6.50"),
         "category": cats.get("Desserts"), "stock_quantity": 15,
         "cost_price": Decimal("2.60"), "description": "New York style cheesecake with berry topping"},
        {"name": "Club Sandwich", "sku": "CLS-001", "price": Decimal("9.00"),
         "category": cats.get("Sandwiches"), "stock_quantity": 20,
         "cost_price": Decimal("3.60"), "description": "Triple-decker club with turkey, bacon, and avocado"},
    ]
    for item in data:
        item.setdefault("is_active", True)
        item.setdefault("low_stock_threshold", 10)
        dry_or_create(Product, **item)

    log(f"Products: {Product.objects.count()} seeded")
    _seeded_models.append("Product")


def seed_ingredients() -> None:
    """Seed ingredients (8 items covering coffee, bakery, sandwich supplies)."""
    if _has_data(Ingredient) and not args.force:
        log(f"Ingredients: {Ingredient.objects.count()} existing, skipping")
        return
    if args.force:
        Ingredient.objects.all().delete()
        log("Ingredients: cleared (--force)")

    data = [
        {"name": "Coffee Beans", "unit": "kg",
         "current_quantity": Decimal("50.0"), "reorder_level": Decimal("10.0"),
         "reorder_quantity": Decimal("20.0"), "cost_per_unit": Decimal("15.00")},
        {"name": "Milk", "unit": "liter",
         "current_quantity": Decimal("30.0"), "reorder_level": Decimal("5.0"),
         "reorder_quantity": Decimal("15.0"), "cost_per_unit": Decimal("2.50")},
        {"name": "Sugar", "unit": "kg",
         "current_quantity": Decimal("20.0"), "reorder_level": Decimal("5.0"),
         "reorder_quantity": Decimal("10.0"), "cost_per_unit": Decimal("1.50")},
        {"name": "All-Purpose Flour", "unit": "kg",
         "current_quantity": Decimal("25.0"), "reorder_level": Decimal("5.0"),
         "reorder_quantity": Decimal("15.0"), "cost_per_unit": Decimal("1.20")},
        {"name": "Dark Chocolate", "unit": "kg",
         "current_quantity": Decimal("15.0"), "reorder_level": Decimal("3.0"),
         "reorder_quantity": Decimal("8.0"), "cost_per_unit": Decimal("8.00")},
        {"name": "Chicken Breast", "unit": "kg",
         "current_quantity": Decimal("20.0"), "reorder_level": Decimal("5.0"),
         "reorder_quantity": Decimal("12.0"), "cost_per_unit": Decimal("6.50")},
        {"name": "Bread Buns", "unit": "piece",
         "current_quantity": Decimal("50.0"), "reorder_level": Decimal("10.0"),
         "reorder_quantity": Decimal("25.0"), "cost_per_unit": Decimal("0.80")},
        {"name": "Cheddar Cheese", "unit": "kg",
         "current_quantity": Decimal("10.0"), "reorder_level": Decimal("2.0"),
         "reorder_quantity": Decimal("5.0"), "cost_per_unit": Decimal("7.00")},
    ]
    for item in data:
        item.setdefault("is_active", True)
        dry_or_create(Ingredient, **item)

    log(f"Ingredients: {Ingredient.objects.count()} seeded")
    _seeded_models.append("Ingredient")


def seed_recipes() -> None:
    """Seed recipes linking products → ingredients.

    Depends on: Product, Ingredient
    Each recipe references a product and describes its ingredient composition
    via the Recipe model (no separate RecipeIngredient model in managed schema).
    """
    if _has_data(Recipe) and not args.force:
        log(f"Recipes: {Recipe.objects.count()} existing, skipping")
        return
    if args.force:
        Recipe.objects.all().delete()
        log("Recipes: cleared (--force)")

    prods = {p.name: p for p in Product.objects.all()}

    instructions_data = {
        "Cappuccino": ("1. Brew a double shot of espresso.\n"
                       "2. Steam 200ml of milk until frothy.\n"
                       "3. Pour steamed milk over espresso.\n"
                       "4. Top with milk foam and dust with cocoa."),
        "Espresso": ("1. Grind 18g of coffee beans fine.\n"
                     "2. Tamp evenly in portafilter.\n"
                     "3. Extract 36g of espresso in 25–30 seconds."),
        "Iced Latte": ("1. Brew a double shot of espresso.\n"
                       "2. Fill a tall glass with ice.\n"
                       "3. Add 250ml of cold milk.\n"
                       "4. Pour espresso over milk and stir."),
        "Chocolate Muffin": ("1. Mix 200g flour, 100g sugar, 50g cocoa.\n"
                             "2. Add 2 eggs and 100ml milk; whisk smooth.\n"
                             "3. Fold in 80g chopped dark chocolate.\n"
                             "4. Bake at 180°C for 20 minutes."),
        "Chicken Sandwich": ("1. Season chicken breast with salt and pepper.\n"
                             "2. Grill for 6–7 minutes per side.\n"
                             "3. Toast bread buns lightly.\n"
                             "4. Assemble with lettuce, tomato, and sauce."),
        "Cheesecake": ("1. Crush graham crackers and mix with melted butter.\n"
                       "2. Press into pan as crust; chill 30 min.\n"
                       "3. Blend cream cheese, sugar, eggs, and vanilla.\n"
                       "4. Bake at 160°C for 50 minutes; cool overnight."),
        "Club Sandwich": ("1. Grill chicken breast; cook bacon until crisp.\n"
                          "2. Toast 3 slices of bread.\n"
                          "3. Layer: bread → mayo → lettuce → chicken → cheese → bread.\n"
                          "4. Top layer: bacon → tomato → avocado → bread; secure with picks."),
    }

    recipes_data = [
        {"product": prods.get("Cappuccino"), "name": "Recipe: Cappuccino",
         "yield_quantity": Decimal("1")},
        {"product": prods.get("Espresso"), "name": "Recipe: Espresso",
         "yield_quantity": Decimal("1")},
        {"product": prods.get("Iced Latte"), "name": "Recipe: Iced Latte",
         "yield_quantity": Decimal("1")},
        {"product": prods.get("Chocolate Muffin"), "name": "Recipe: Chocolate Muffin",
         "yield_quantity": Decimal("24")},
        {"product": prods.get("Chicken Sandwich"), "name": "Recipe: Chicken Sandwich",
         "yield_quantity": Decimal("1")},
        {"product": prods.get("Cheesecake"), "name": "Recipe: Cheesecake",
         "yield_quantity": Decimal("12")},
        {"product": prods.get("Club Sandwich"), "name": "Recipe: Club Sandwich",
         "yield_quantity": Decimal("1")},
    ]

    for r in recipes_data:
        prod = r["product"]
        if prod and prod.name in instructions_data:
            r["instructions"] = instructions_data[prod.name]
        r.setdefault("is_active", True)
        dry_or_create(Recipe, **r)

    log(f"Recipes: {Recipe.objects.count()} seeded")
    _seeded_models.append("Recipe")


def seed_receipt_templates() -> None:
    """Seed receipt/invoice templates (standard, commercial, minimal)."""
    if _has_data(ReceiptTemplate) and not args.force:
        log(f"ReceiptTemplates: {ReceiptTemplate.objects.count()} existing, skipping")
        return
    if args.force:
        ReceiptTemplate.objects.all().delete()
        log("ReceiptTemplates: cleared (--force)")

    templates = [
        {
            "name": "Standard Receipt",
            "description": "Default POS receipt with all order details",
            "template_html": (
                "<div class='receipt'>"
                "<h1>{{restaurant_name}}</h1>"
                "<p>{{address}} | {{phone}}</p>"
                "<hr>"
                "<p><strong>Date:</strong> {{date}}</p>"
                "<p><strong>Time:</strong> {{time}}</p>"
                "<p><strong>Server:</strong> {{server_name}}</p>"
                "<p><strong>Table:</strong> {{table_number}}</p>"
                "<hr>"
                "<table>"
                "<tr><th>Item</th><th>Qty</th><th>Price</th></tr>"
                "{{#items}}"
                "<tr><td>{{name}}</td><td>{{qty}}</td><td>${{price}}</td></tr>"
                "{{/items}}"
                "</table>"
                "<hr>"
                "<p><strong>Subtotal:</strong> ${{subtotal}}</p>"
                "<p><strong>Tax:</strong> ${{tax}}</p>"
                "<p><strong>Total:</strong> ${{total}}</p>"
                "<hr>"
                "<p>{{footer}}</p>"
                "</div>"
            ),
            "template_css": (
                ".receipt { font-family: monospace; max-width: 300px; margin: 0 auto; }"
                ".receipt h1 { text-align: center; font-size: 18px; }"
                ".receipt table { width: 100%; border-collapse: collapse; }"
                ".receipt th, .receipt td { padding: 4px 0; text-align: left; }"
                ".receipt hr { border: 1px dashed #999; }"
            ),
            "is_default": True,
        },
        {
            "name": "Commercial Invoice",
            "description": "Detailed invoice for business customers",
            "template_html": (
                "<div class='invoice'>"
                "<div class='header'>"
                "<h1>INVOICE</h1>"
                "<p><strong>{{restaurant_name}}</strong></p>"
                "<p>{{address}} | {{phone}} | {{email}}</p>"
                "</div>"
                "<hr>"
                "<div class='meta'>"
                "<p><strong>Invoice #:</strong> {{invoice_number}}</p>"
                "<p><strong>Date:</strong> {{date}}</p>"
                "<p><strong>Customer:</strong> {{customer_name}}</p>"
                "</div>"
                "<hr>"
                "<table class='items'>"
                "<tr><th>#</th><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr>"
                "{{#items}}"
                "<tr><td>{{index}}</td><td>{{name}}</td><td>{{qty}}</td>"
                "<td>${{unit_price}}</td><td>${{line_total}}</td></tr>"
                "{{/items}}"
                "</table>"
                "<hr>"
                "<div class='totals'>"
                "<p>Subtotal: ${{subtotal}}</p>"
                "<p>Tax ({{tax_rate}}%): ${{tax}}</p>"
                "<p><strong>Total Due: ${{total}}</strong></p>"
                "</div>"
                "<hr>"
                "<p class='footer'>Thank you for your business!</p>"
                "</div>"
            ),
            "template_css": (
                ".invoice { font-family: 'Helvetica', sans-serif; max-width: 400px; margin: 0 auto; }"
                ".invoice .header { text-align: center; margin-bottom: 10px; }"
                ".invoice .header h1 { font-size: 24px; color: #333; }"
                ".invoice .meta { font-size: 12px; }"
                ".invoice table.items { width: 100%; border-collapse: collapse; }"
                ".invoice table.items th { background: #f5f5f5; padding: 6px; text-align: left; }"
                ".invoice table.items td { padding: 4px 6px; border-bottom: 1px solid #eee; }"
                ".invoice .totals { text-align: right; font-size: 14px; }"
                ".invoice .footer { text-align: center; color: #888; font-size: 11px; }"
            ),
            "is_default": False,
        },
        {
            "name": "Minimal Receipt",
            "description": "Clean, minimal receipt for quick printing",
            "template_html": (
                "<div class='minimal'>"
                "<h2>{{restaurant_name}}</h2>"
                "<p class='date'>{{date}} {{time}}</p>"
                "<table>"
                "{{#items}}"
                "<tr><td>{{qty}}x {{name}}</td><td class='right'>${{line_total}}</td></tr>"
                "{{/items}}"
                "</table>"
                "<hr>"
                "<p class='total'><strong>TOTAL: ${{total}}</strong></p>"
                "<p class='payment'>Paid via {{payment_method}}</p>"
                "<p class='thanks'>{{footer}}</p>"
                "</div>"
            ),
            "template_css": (
                ".minimal { font-family: 'Courier New', monospace; max-width: 280px; margin: 0 auto; }"
                ".minimal h2 { text-align: center; margin: 0 0 5px; }"
                ".minimal .date { text-align: center; font-size: 11px; color: #666; }"
                ".minimal table { width: 100%; }"
                ".minimal td { padding: 2px 0; }"
                ".minimal .right { text-align: right; }"
                ".minimal .total { text-align: right; font-size: 16px; }"
                ".minimal .payment { text-align: center; font-size: 11px; color: #666; }"
                ".minimal .thanks { text-align: center; font-size: 12px; margin-top: 8px; }"
                ".minimal hr { border: 1px solid #ccc; }"
            ),
            "is_default": False,
        },
    ]

    for tpl in templates:
        tpl.setdefault("is_active", True)
        dry_or_create(ReceiptTemplate, **tpl)

    log(f"ReceiptTemplates: {ReceiptTemplate.objects.count()} seeded")
    _seeded_models.append("ReceiptTemplate")


def seed_roles() -> None:
    """Seed user roles with comprehensive permission sets."""
    if _has_data(Role) and not args.force:
        log(f"Roles: {Role.objects.count()} existing, skipping")
        return
    if args.force:
        Role.objects.all().delete()
        log("Roles: cleared (--force)")

    roles_data = [
        {
            "name": "Admin",
            "description": "Full system access — all permissions granted",
            "permissions": {
                "can_manage_products": True,
                "can_manage_categories": True,
                "can_manage_customers": True,
                "can_manage_employees": True,
                "can_manage_sales": True,
                "can_manage_inventory": True,
                "can_manage_suppliers": True,
                "can_manage_purchase_orders": True,
                "can_manage_settings": True,
                "can_manage_roles": True,
                "can_view_reports": True,
                "can_manage_sync": True,
                "can_approve_changes": True,
                "can_process_refunds": True,
                "can_discount": True,
                "can_access_admin_panel": True,
                "can_manage_users": True,
            },
        },
        {
            "name": "Manager",
            "description": "Day-to-day operations management",
            "permissions": {
                "can_manage_products": True,
                "can_manage_categories": True,
                "can_manage_customers": True,
                "can_manage_employees": False,
                "can_manage_sales": True,
                "can_manage_inventory": True,
                "can_manage_suppliers": True,
                "can_manage_purchase_orders": True,
                "can_manage_settings": True,
                "can_manage_roles": False,
                "can_view_reports": True,
                "can_manage_sync": False,
                "can_approve_changes": True,
                "can_process_refunds": True,
                "can_discount": True,
                "can_access_admin_panel": False,
                "can_manage_users": False,
            },
        },
        {
            "name": "Cashier",
            "description": "Point-of-sale operations",
            "permissions": {
                "can_manage_products": False,
                "can_manage_categories": False,
                "can_manage_customers": True,
                "can_manage_employees": False,
                "can_manage_sales": True,
                "can_manage_inventory": False,
                "can_manage_suppliers": False,
                "can_manage_purchase_orders": False,
                "can_manage_settings": False,
                "can_manage_roles": False,
                "can_view_reports": False,
                "can_manage_sync": False,
                "can_approve_changes": False,
                "can_process_refunds": False,
                "can_discount": False,
                "can_access_admin_panel": False,
                "can_manage_users": False,
            },
        },
        {
            "name": "Kitchen Staff",
            "description": "Kitchen display and order preparation",
            "permissions": {
                "can_manage_products": False,
                "can_manage_categories": False,
                "can_manage_customers": False,
                "can_manage_employees": False,
                "can_manage_sales": False,
                "can_manage_inventory": False,
                "can_manage_suppliers": False,
                "can_manage_purchase_orders": False,
                "can_manage_settings": False,
                "can_manage_roles": False,
                "can_view_reports": False,
                "can_manage_sync": False,
                "can_approve_changes": False,
                "can_process_refunds": False,
                "can_discount": False,
                "can_access_admin_panel": False,
                "can_view_kitchen_display": True,
                "can_update_ticket_status": True,
            },
        },
        {
            "name": "Server",
            "description": "Front-of-house table service",
            "permissions": {
                "can_manage_products": False,
                "can_manage_categories": False,
                "can_manage_customers": True,
                "can_manage_employees": False,
                "can_manage_sales": True,
                "can_manage_inventory": False,
                "can_manage_suppliers": False,
                "can_manage_purchase_orders": False,
                "can_manage_settings": False,
                "can_manage_roles": False,
                "can_view_reports": False,
                "can_manage_sync": False,
                "can_approve_changes": False,
                "can_process_refunds": False,
                "can_discount": True,
                "can_access_admin_panel": False,
            },
        },
    ]

    for role in roles_data:
        role.setdefault("is_active", True)
        dry_or_create(Role, **role)

    log(f"Roles: {Role.objects.count()} seeded")
    _seeded_models.append("Role")


def seed_inventory_adjustments() -> None:
    """Seed inventory adjustments (linked to ingredients).

    Depends on: Ingredient
    Adjustments auto-populate previous_quantity from the ingredient's
    current_quantity and compute new_quantity.
    """
    if _has_data(InventoryAdjustment) and not args.force:
        log(f"InventoryAdjustments: {InventoryAdjustment.objects.count()} existing, skipping")
        return
    if args.force:
        InventoryAdjustment.objects.all().delete()
        log("InventoryAdjustments: cleared (--force)")

    ingredients = {i.name: i for i in Ingredient.objects.all()}

    adjustments = [
        {
            "ingredient": ingredients.get("Coffee Beans"),
            "quantity": Decimal("20.0"),
            "adjustment_type": "addition",
            "reason": "return",
            "notes": "Weekly delivery from Bean Supply Co — 20kg Arabica",
            "created_by": "system",
        },
        {
            "ingredient": ingredients.get("Milk"),
            "quantity": Decimal("-5.0"),
            "adjustment_type": "removal",
            "reason": "damage",
            "notes": "Spoiled batch — refrigeration failure overnight",
            "created_by": "Alice Worker",
        },
        {
            "ingredient": ingredients.get("All-Purpose Flour"),
            "quantity": Decimal("-2.0"),
            "adjustment_type": "adjustment",
            "reason": "correction",
            "notes": "Inventory count correction: actual 23.0kg vs system 25.0kg",
            "created_by": "Bob Manager",
        },
        {
            "ingredient": ingredients.get("Dark Chocolate"),
            "quantity": Decimal("-3.0"),
            "adjustment_type": "transfer",
            "reason": "correction",
            "notes": "Transferred 3kg to pastry station",
            "created_by": "Alice Worker",
        },
    ]

    for adj in adjustments:
        dry_or_create(InventoryAdjustment, **adj)

    log(f"InventoryAdjustments: {InventoryAdjustment.objects.count()} seeded")
    _seeded_models.append("InventoryAdjustment")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    db_name = settings.DATABASES["default"]["NAME"]
    print(f"\n{'=' * 60}")
    print(f"  POS Managed DB Seed Script")
    print(f"  Database: {db_name}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'FORCE' if args.force else 'NORMAL'}")
    print(f"{'=' * 60}\n")

    # Filter to requested models
    model_filter = [m.strip().lower() for m in args.models.split(",") if m.strip()]
    if model_filter:
        print(f"  Filter: seeding only {', '.join(model_filter)}\n")

    # Determine which seed functions to run
    seed_fn_map = {
        "category": seed_categories,
        "product": seed_products,
        "ingredient": seed_ingredients,
        "recipe": seed_recipes,
        "receipttemplate": seed_receipt_templates,
        "role": seed_roles,
        "inventoryadjustment": seed_inventory_adjustments,
    }

    # Always seed dependencies (category + product) so Recipe FK works
    # But only if the user asked for recipe or didn't specify a filter
    should_seed_deps = not model_filter or "recipe" in model_filter or "inventoryadjustment" in model_filter

    if should_seed_deps:
        seed_categories()
        seed_products()

    for name, fn in seed_fn_map.items():
        if name in ("category", "product"):
            continue  # already seeded above
        if model_filter and name not in model_filter:
            continue
        fn()

    # ── Summary ──
    print(f"\n{'─' * 60}")
    if args.dry_run:
        print("  DRY RUN — no data was written.")
    else:
        print(f"  Seeded models: {', '.join(_seeded_models) if _seeded_models else 'none'}")
        counts = {}
        for model_cls in [Category, Product, Ingredient, Recipe, ReceiptTemplate, Role, InventoryAdjustment]:
            name = model_cls.__name__
            try:
                counts[name] = model_cls.objects.count()
            except Exception:
                counts[name] = "?"
        print(f"  Final counts: {counts}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
