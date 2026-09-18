"""
Tests for the POS Full FragmentComponent classes.

These tests verify that each fragment class:
1. Is importable and has the correct ``fragment_name``
2. Is a proper ``FragmentComponent`` subclass
3. The registration decorator populates the module-level registry
4. Template strings reference only keys the fragments provide (string-match)

NOTE: Django is configured minimally here so that ``django_fusion.routes``
is importable. The tests do NOT call ``get_context()`` (which queries the
database), so no database is required.
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
            # POS Full app — required so pos_full models participate in the
            # relation graph (reverse FKs, cascade deletes). Omitting it here
            # poisons later tests with broken reverse relations / FK errors.
            "models.PosFullConfig",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY", "test-key-fragments"),
        # pos_full tables are created manually by the conftest bootstrap;
        # disable migrations so pytest-django's ``migrate`` doesn't re-create.
        MIGRATION_MODULES={"pos_full": None},
    )
    django.setup()

from django_fusion.routes.components.fragments import FragmentComponent


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

    count_before = len(_FRAGMENTS)
    all_frags = get_all_fragments()
    assert len(all_frags) >= 7, f"Expected at least 7 fragments, got {len(all_frags)}"
    # Idempotent: calling again doesn't double-register
    assert set(id(f) for f in all_frags) == set(id(f) for f in get_all_fragments())


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
# These verify that every ``{{ variable }}`` in the template string
# is a key the fragment's ``get_context()`` returns.  We check by
# name because the fragments don't need a database to validate this.


def test_dashboard_template_keys_exist_in_fragment():
    """The dashboard template only uses keys DashboardFragment provides."""
    import pytest
    pytest.importorskip("robyn", reason="Robyn removed — legacy routes/fusion_fragments is deprecated")
    from fragments.dashboard import DashboardFragment
    from routes.fusion_fragments import _DASHBOARD_FRAGMENT_TEMPLATE

    context_keys = {
        "restaurant_name", "product_count", "customer_count",
        "employee_count", "sale_count",
    }
    template_keys = _extract_variable_names(_DASHBOARD_FRAGMENT_TEMPLATE)
    # Only check the keys the template uses are in the context
    for key in template_keys:
        assert key in context_keys, (
            f"Dashboard template uses '{{{{ {key} }}}}' but "
            f"{DashboardFragment.__name__} does not provide it"
        )


def test_suppliers_template_keys_exist_in_fragment():
    import pytest
    pytest.importorskip("robyn", reason="Robyn removed — legacy routes/fusion_fragments is deprecated")
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
    import pytest
    pytest.importorskip("robyn", reason="Robyn removed — legacy routes/fusion_fragments is deprecated")
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
    """Extract ``{{ variable }}`` names from a Django template string.

    Handles dotted access (``{{ foo.bar }}`` → ``foo``), filters
    (``{{ foo|default:0 }}`` → ``foo``), and skips single-letter loop
    variables (``{{ s.name }}``'s ``s`` is a ``{% for s in %}`` variable,
    not a context key).
    """
    import re

    keys: set[str] = set()
    for match in re.finditer(r"\{\{\s*([\w_.|:]+?)\s*\}\}", template):
        raw = match.group(1).strip()
        # Split on | for filters, take first part
        var_part = raw.split("|")[0].strip()
        # Take the root name (before any dot)
        root = var_part.split(".")[0]
        # Skip template-control names and single-letter loop variables
        if root not in ("block", "endblock", "for", "endfor", "if", "endif", "else") and len(root) > 1:
            keys.add(root)
    return keys
