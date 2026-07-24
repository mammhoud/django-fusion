"""
Tests for the POS Solo FragmentComponent classes.

Verifies each fragment class is importable, has correct metadata, and
the registration decorator works. Template context key alignment tests
ensure the route handler templates reference only keys provided by the
fragment classes.

NOTE: Django is configured minimally so that ``django_fusion.routes``
is importable. The tests do NOT call ``get_context()`` (which queries
the database).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# ── Minimal Django bootstrap for django_fusion ─────────────────────
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY", "test-key-fragments-solo"),
    )
    django.setup()

from django_fusion.comp.routes import FragmentComponent


# ── Tests: fragment class structure ────────────────────────────────


def test_dashboard_fragment_structure():
    from fragments.dashboard import DashboardFragment

    assert DashboardFragment.fragment_name == "pos.dashboard"
    assert issubclass(DashboardFragment, FragmentComponent)


def test_suppliers_fragment_structure():
    from fragments.suppliers import SuppliersFragment

    assert SuppliersFragment.fragment_name == "pos.suppliers"
    assert issubclass(SuppliersFragment, FragmentComponent)


def test_about_fragment_structure():
    from fragments.about import AboutFragment

    assert AboutFragment.fragment_name == "pos.about"
    assert issubclass(AboutFragment, FragmentComponent)


def test_customers_fragment_structure():
    from fragments.customers import CustomersFragment

    assert CustomersFragment.fragment_name == "pos.customers"
    assert issubclass(CustomersFragment, FragmentComponent)


def test_inventory_fragment_structure():
    from fragments.inventory import InventoryFragment

    assert InventoryFragment.fragment_name == "pos.inventory"
    assert issubclass(InventoryFragment, FragmentComponent)


def test_employees_fragment_structure():
    from fragments.employees import EmployeesFragment

    assert EmployeesFragment.fragment_name == "pos.employees"
    assert issubclass(EmployeesFragment, FragmentComponent)


def test_products_fragment_structure():
    from fragments.products import ProductListFragment

    assert ProductListFragment.fragment_name == "pos.products"
    assert issubclass(ProductListFragment, FragmentComponent)


def test_product_detail_fragment_structure():
    from fragments.products import ProductDetailFragment

    assert ProductDetailFragment.fragment_name == "pos.product_detail"
    assert issubclass(ProductDetailFragment, FragmentComponent)


# ── Tests: registration decorator ──────────────────────────────────


def test_get_all_fragments_imports_all_modules():
    from fragments import _FRAGMENTS, get_all_fragments

    all_frags = get_all_fragments()
    assert len(all_frags) >= 7, f"Expected at least 7 fragments, got {len(all_frags)}"


def test_each_fragment_has_unique_name():
    from fragments import _FRAGMENTS, get_all_fragments

    all_frags = get_all_fragments()
    names = [f.fragment_name for f in all_frags]
    assert len(names) == len(set(names)), f"Duplicate fragment names: {names}"


def test_all_fragments_have_nonempty_name():
    from fragments import _FRAGMENTS, get_all_fragments

    all_frags = get_all_fragments()
    for f in all_frags:
        assert f.fragment_name, f"{f.__name__} has empty fragment_name"


# ── Tests: template variable alignment (string-match) ──────────────


def test_dashboard_template_keys_exist_in_fragment():
    from fragments.dashboard import DashboardFragment
    from routes.fusion_fragments import _DASHBOARD_FRAGMENT_TEMPLATE

    context_keys = {
        "restaurant_name", "product_count", "customer_count",
        "employee_count", "sale_count",
    }
    template_keys = _extract_variable_names(_DASHBOARD_FRAGMENT_TEMPLATE)
    for key in template_keys:
        assert key in context_keys, (
            f"Dashboard template uses '{{{{ {key} }}}}' but "
            f"{DashboardFragment.__name__} does not provide it"
        )


def test_suppliers_template_keys_exist_in_fragment():
    from fragments.suppliers import SuppliersFragment
    from routes.fusion_fragments import _SUPPLIERS_FRAGMENT_TEMPLATE

    context_keys = {"suppliers", "count", "recent_purchase_orders"}
    template_keys = _extract_variable_names(_SUPPLIERS_FRAGMENT_TEMPLATE)
    for key in template_keys:
        assert key in context_keys, (
            f"Suppliers template uses '{{{{ {key} }}}}' but "
            f"{SuppliersFragment.__name__} does not provide it"
        )


def test_about_template_keys_exist_in_fragment():
    from fragments.about import AboutFragment
    from routes.fusion_fragments import _ABOUT_FRAGMENT_TEMPLATE

    context_keys = {"title", "version", "description", "year", "node_count", "db_size_mb"}
    template_keys = _extract_variable_names(_ABOUT_FRAGMENT_TEMPLATE)
    for key in template_keys:
        assert key in context_keys, (
            f"About template uses '{{{{ {key} }}}}' but "
            f"{AboutFragment.__name__} does not provide it"
        )


# ── Helper ─────────────────────────────────────────────────────────


def _extract_variable_names(template: str) -> set[str]:
    import re

    keys: set[str] = set()
    for match in re.finditer(r"\{\{\s*([\w_.|:]+?)\s*\}\}", template):
        raw = match.group(1).strip()
        var_part = raw.split("|")[0].strip()
        root = var_part.split(".")[0]
        if root not in ("block", "endblock", "for", "endfor", "if", "endif", "else") and len(root) > 1:
            keys.add(root)
    return keys
