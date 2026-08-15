"""
Barcode Scanner (P1) — resolve + label tests.

Covers ``services.barcode``:
  * ``resolve_product`` — exact barcode match with SKU fallback, blank/unknown
    values return None.
  * ``barcode_label_svg`` — Code128 SVG output (skipped when the optional
    ``python-barcode`` dependency is absent).

Django models are imported lazily inside each test (the conftest
``django_bootstrap`` fixture configures Django first).
"""

from __future__ import annotations

import pytest


def _barcode():
    import services.barcode as bc

    return bc


@pytest.fixture(autouse=True)
def _clean_products(django_bootstrap):
    from models.pos import Product

    Product.objects.all().delete()
    yield


class TestResolveProduct:
    def test_exact_barcode_match(self, product_factory):
        product_factory(name="Espresso", price=3.50, barcode="4901234567890")
        result = _barcode().resolve_product("4901234567890")
        assert result is not None
        assert result.name == "Espresso"

    def test_sku_fallback(self, product_factory):
        product_factory(name="Cappuccino", price=4.20, sku="LEGACY-042")
        result = _barcode().resolve_product("LEGACY-042")
        assert result is not None
        assert result.name == "Cappuccino"

    def test_barcode_wins_over_sku(self, product_factory):
        product_factory(name="ByBarcode", price=1.00, barcode="123", sku="456")
        product_factory(name="BySku", price=2.00, barcode="", sku="123")
        result = _barcode().resolve_product("123")
        assert result.name == "ByBarcode"

    def test_unknown_returns_none(self, product_factory):
        product_factory(name="Latte", price=4.00, barcode="111111")
        assert _barcode().resolve_product("999999") is None

    def test_blank_returns_none(self):
        assert _barcode().resolve_product("") is None
        assert _barcode().resolve_product("   ") is None

    def test_strips_whitespace(self, product_factory):
        product_factory(name="Tea", price=2.50, barcode="7788")
        assert _barcode().resolve_product("  7788  ").name == "Tea"


class TestBarcodeLabel:
    def test_label_svg_renders(self):
        pytest.importorskip("barcode")
        svg = _barcode().barcode_label_svg("4901234567890")
        assert "<svg" in svg.lower()
        assert "4901234567890" in svg
