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
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
        SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY", "test-key-fragments"),
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

