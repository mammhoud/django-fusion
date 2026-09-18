"""
KDS station routing tests — KitchenStation model + route_station_for_sale.

Covers the "station routing" pillar of the Kitchen Display System (P0):
defaults, category-keyword routing, expedite fallback, and the
KitchenTicket ↔ KitchenStation relation.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clean_kds(django_bootstrap):
    """Isolate KDS tests — the conftest shares one in-memory DB per session.

    Wipe KDS-related tables before each test so routing assertions are not
    polluted by stations/tickets created by earlier tests.
    """
    from models.ops import KitchenStation, KitchenTicket
    from models.pos import Category, Customer, Product, Sale, SaleItem

    KitchenTicket.objects.all().delete()
    SaleItem.objects.all().delete()
    Sale.objects.all().delete()
    KitchenStation.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Customer.objects.all().delete()
    yield


class TestKitchenStation:
    def test_create_with_defaults(self, station_factory):
        s = station_factory()
        assert s.name.startswith("Station-")
        assert s.station_type == "expedite"
        assert s.category_keywords == ""
        assert s.is_active is True
        assert s.sort_order == 0

    def test_create_with_custom_fields(self, station_factory):
        s = station_factory(
            name="Grill",
            slug="grill",
            station_type="grill",
            category_keywords="burger, steak",
            sort_order=20,
        )
        assert s.name == "Grill"
        assert s.slug == "grill"
        assert s.station_type == "grill"
        assert s.category_keywords == "burger, steak"
        assert s.sort_order == 20

    def test_str(self, station_factory):
        s = station_factory(name="Bar")
        assert str(s) == "Bar"

    def test_unique_name(self, station_factory):
        station_factory(name="Expedite", slug="expedite-a")
        with pytest.raises(Exception):
            station_factory(name="Expedite", slug="expedite-b")

    def test_ordering(self, station_factory):
        station_factory(name="B", sort_order=2)
        station_factory(name="A", sort_order=1)
        from models.ops import KitchenStation
        names = [s.name for s in KitchenStation.objects.all()]
        assert names.index("A") < names.index("B")


class TestRouteStationForSale:
    def _sale_with_category(self, sale_factory, sale_item_factory, category_factory, product_factory, category_name, product_name):
        cat = category_factory(name=category_name)
        prod = product_factory(name=product_name, category=cat)
        sale = sale_factory()
        sale_item_factory(sale=sale, product=prod, product_name=product_name)
        return sale

    def test_routes_by_category_keyword(self, sale_factory, sale_item_factory, category_factory, product_factory, station_factory):
        station_factory(name="Grill", station_type="grill", category_keywords="burger, steak")
        station_factory(name="Bar", station_type="bar", category_keywords="drink, coffee")
        sale = self._sale_with_category(
            sale_factory, sale_item_factory, category_factory, product_factory,
            "Burgers", "Cheeseburger",
        )
        from models.ops import route_station_for_sale
        station = route_station_for_sale(sale)
        assert station is not None
        assert station.name == "Grill"

    def test_keyword_match_is_case_insensitive(self, sale_factory, sale_item_factory, category_factory, product_factory, station_factory):
        station_factory(name="Bar", station_type="bar", category_keywords="COFFEE, Tea")
        sale = self._sale_with_category(
            sale_factory, sale_item_factory, category_factory, product_factory,
            "Hot Coffee Drinks", "Latte",
        )
        from models.ops import route_station_for_sale
        assert route_station_for_sale(sale).name == "Bar"

    def test_falls_back_to_expedite(self, sale_factory, sale_item_factory, category_factory, product_factory, station_factory):
        station_factory(name="Expedite", station_type="expedite")
        station_factory(name="Grill", station_type="grill", category_keywords="burger")
        sale = self._sale_with_category(
            sale_factory, sale_item_factory, category_factory, product_factory,
            "Desserts", "Tiramisu",
        )
        from models.ops import route_station_for_sale
        assert route_station_for_sale(sale).name == "Expedite"

    def test_returns_none_without_stations(self, sale_factory, sale_item_factory, category_factory, product_factory):
        sale = self._sale_with_category(
            sale_factory, sale_item_factory, category_factory, product_factory,
            "Desserts", "Tiramisu",
        )
        from models.ops import route_station_for_sale
        assert route_station_for_sale(sale) is None


class TestKitchenTicketStation:
    def test_station_fk_defaults_null(self, kitchen_ticket_factory):
        ticket = kitchen_ticket_factory()
        assert ticket.station is None

    def test_station_fk_assignment(self, kitchen_ticket_factory, station_factory):
        station = station_factory(name="Prep", station_type="prep")
        ticket = kitchen_ticket_factory(station=station)
        ticket.refresh_from_db()
        assert ticket.station_id == station.id
        assert list(station.tickets.all()) == [ticket]

    def test_lifecycle_timestamps_default_null(self, kitchen_ticket_factory):
        ticket = kitchen_ticket_factory()
        assert ticket.started_at is None
        assert ticket.ready_at is None
        assert ticket.completed_at is None

    def test_status_choices(self, kitchen_ticket_factory):
        for status in ("pending", "preparing", "ready", "delivered"):
            ticket = kitchen_ticket_factory(status=status)
            assert ticket.status == status
