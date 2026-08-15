"""
Mobile Waiter (P1) — split/merge bill tests.

Covers ``SaleGroup`` + ``Sale.group``/``Sale.parent_sale`` and the
``services.split_merge`` split/merge workflows.

Django models are imported lazily inside each test (the conftest
``django_bootstrap`` fixture configures Django, which must happen before the
``models`` package is imported).
"""

from __future__ import annotations

from decimal import Decimal

import pytest


def _split_merge():
    import services.split_merge as sm

    return sm


@pytest.fixture(autouse=True)
def _clean_orders(django_bootstrap):
    from models.pos import Customer, Product, Sale, SaleGroup, SaleItem

    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    SaleGroup.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    yield


def _sale_with_items(sale_factory, sale_item_factory, prices=(5.0, 7.5, 10.0)):
    sale = sale_factory(subtotal=22.5, total=22.5)
    items = [
        sale_item_factory(sale=sale, line_total=Decimal(str(p)), unit_price=Decimal(str(p)))
        for p in prices
    ]
    return sale, items


class TestSplitSale:
    def test_split_creates_group_and_children(self, sale_factory, sale_item_factory):
        sale, items = _sale_with_items(sale_factory, sale_item_factory)

        group, parent, children = _split_merge().split_sale(
            sale.id,
            splits=[
                {"item_ids": [items[0].id], "payment_method": "card"},
                {"item_ids": [items[1].id], "payment_method": "cash"},
            ],
        )

        assert group.status == "open"
        assert parent.id == sale.id
        assert len(children) == 2
        # Parent retains only the un-split item (10.0).
        parent.refresh_from_db()
        assert parent.total == Decimal("10.00")

    def test_split_recomputes_child_totals(self, sale_factory, sale_item_factory):
        sale, items = _sale_with_items(sale_factory, sale_item_factory)

        _, _, children = _split_merge().split_sale(
            sale.id,
            splits=[
                {"item_ids": [items[0].id, items[1].id]},  # 5.0 + 7.5
            ],
        )
        assert children[0].total == Decimal("12.50")

    def test_split_duplicate_item_raises(self, sale_factory, sale_item_factory):
        sale, items = _sale_with_items(sale_factory, sale_item_factory)
        with pytest.raises(_split_merge().SplitMergeError):
            _split_merge().split_sale(
                sale.id,
                splits=[
                    {"item_ids": [items[0].id]},
                    {"item_ids": [items[0].id]},
                ],
            )

    def test_split_missing_item_raises(self, sale_factory, sale_item_factory):
        sale, _ = _sale_with_items(sale_factory, sale_item_factory)
        with pytest.raises(_split_merge().SplitMergeError):
            _split_merge().split_sale(sale.id, splits=[{"item_ids": [999999]}])


class TestMergeSale:
    def test_merge_child_back_to_parent(self, sale_factory, sale_item_factory):
        from models.pos import Sale

        sm = _split_merge()
        sale, items = _sale_with_items(sale_factory, sale_item_factory)
        _, parent, children = sm.split_sale(
            sale.id,
            splits=[{"item_ids": [items[0].id, items[1].id]}],
        )
        child_id = children[0].id
        merged_parent, group = sm.merge_sale(child_id)

        assert merged_parent.id == parent.id
        merged_parent.refresh_from_db()
        assert merged_parent.total == Decimal("22.50")
        assert not Sale.objects.filter(id=child_id).exists()
        # Group closed when no children remain.
        assert group is not None
        assert group.status == "closed"

    def test_merge_non_child_raises(self, sale_factory, sale_item_factory):
        sale, _ = _sale_with_items(sale_factory, sale_item_factory)
        with pytest.raises(_split_merge().SplitMergeError):
            _split_merge().merge_sale(sale.id)  # sale is not a child

    def test_merge_group_merges_all_children(self, sale_factory, sale_item_factory):
        from models.pos import Sale

        sm = _split_merge()
        sale, items = _sale_with_items(sale_factory, sale_item_factory)
        group, parent, children = sm.split_sale(
            sale.id,
            splits=[
                {"item_ids": [items[0].id]},
                {"item_ids": [items[1].id]},
            ],
        )
        closed_group, parents = sm.merge_group(group.group_key)
        assert closed_group.status == "closed"
        assert len(parents) == 2
        parent.refresh_from_db()
        assert parent.total == Decimal("22.50")
        assert Sale.objects.filter(parent_sale=parent).count() == 0
