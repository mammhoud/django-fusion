"""
Multi-terminal Sync (P1) — changeset collector + acknowledge tests.

Covers ``services.sync_changes.SyncChangeCollector``: pulling pending
(``is_synced=False``) rows across sync-tracked models, entity filtering, and
acknowledgement. Models are imported lazily (Django must be configured first).
"""

from __future__ import annotations

import pytest


def _collector():
    import services.sync_changes as sc

    return sc


@pytest.fixture(autouse=True)
def _clean_sync(django_bootstrap):
    from models.pos import Category, Customer, Product, Sale, SaleItem

    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    Category.objects.all().delete()
    yield


class TestSyncChangeCollector:
    def test_collect_returns_pending_products(self, product_factory):
        product_factory(name="Espresso")
        product_factory(name="Latte")

        result = _collector().SyncChangeCollector().collect(entity_type="product")
        names = [c["data"]["name"] for c in result["changes"]]
        assert result["count"] == 2
        assert "Espresso" in names and "Latte" in names

    def test_collect_filters_by_entity_type(self, product_factory, customer_factory):
        product_factory(name="Espresso")
        customer_factory(first_name="Ada")

        collector = _collector().SyncChangeCollector()
        products = collector.collect(entity_type="product")
        customers = collector.collect(entity_type="customer")
        assert products["count"] == 1
        assert customers["count"] == 1
        assert all(c["entity_type"] == "product" for c in products["changes"])
        assert all(c["entity_type"] == "customer" for c in customers["changes"])

    def test_collect_all_includes_multiple_types(self, product_factory, customer_factory):
        product_factory(name="Espresso")
        customer_factory(first_name="Ada")

        result = _collector().SyncChangeCollector().collect()
        types = {c["entity_type"] for c in result["changes"]}
        assert "product" in types
        assert "customer" in types

    def test_acknowledge_marks_synced(self, product_factory):
        product = product_factory(name="Espresso")
        collector = _collector().SyncChangeCollector()

        result = collector.acknowledge("product", [product.id])
        assert result["acknowledged"] == 1

        # Row is no longer pending.
        remaining = collector.collect(entity_type="product")
        assert remaining["count"] == 0
        product.refresh_from_db()
        assert product.is_synced is True
        assert product.sync_status == "synced"

    def test_acknowledge_unknown_entity_type(self):
        collector = _collector().SyncChangeCollector()
        result = collector.acknowledge("nope", [1])
        assert "error" in result

    def test_entity_types_lists_tracked(self):
        types = _collector().entity_types()
        assert "product" in types
        assert "sale" in types
        assert "customer" in types
