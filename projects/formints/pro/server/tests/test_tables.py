"""
Table Management (P2) — floor layouts + order tracking + reservations tests.

Covers ``services.tables``:
  * ``create_table`` — name/section uniqueness, capacity guards.
  * ``update_status`` — valid transitions; occupied/free sale guards.
  * ``occupy_table`` / ``clear_table`` — order tracking via current_sale and
    table_number sync on the sale; close_sale option.
  * ``floor_summary`` — status/capacity aggregation.
  * Reservations — create (only free tables), cancel/seat/complete/no-show
    lifecycle, seat with a sale occupying the table.

Models and the service are imported lazily (the conftest ``django_bootstrap``
fixture configures Django first).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from django.utils import timezone


def _svc():
    import services.tables as t

    return t


def _models():
    from models.tables import RestaurantTable, TableReservation

    return RestaurantTable, TableReservation


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    RestaurantTable, TableReservation = _models()
    TableReservation.objects.all().delete()
    RestaurantTable.objects.all().delete()
    yield


def _sale(**kwargs):
    from models.pos import Customer, Sale

    defaults = {
        "subtotal": 19.99,
        "total": 23.99,
        "tax_amount": 2.00,
        "status": "pending",
        "payment_method": "cash",
        "customer": Customer.objects.create(
            first_name="Table", last_name="Guest", email="table@test.com",
        ),
    }
    defaults.update(kwargs)
    return Sale.objects.create(**defaults)


class TestCreateTable:
    def test_create_table(self):
        t = _svc()
        table = t.create_table("T12", section="patio", capacity=4)
        assert table.name == "T12"
        assert table.section == "patio"
        assert table.capacity == 4
        assert table.status == "free"

    def test_create_requires_name(self):
        t = _svc()
        with pytest.raises(t.TableError):
            t.create_table("  ")

    def test_create_rejects_zero_capacity(self):
        t = _svc()
        with pytest.raises(t.TableError):
            t.create_table("T1", capacity=0)

    def test_duplicate_name_in_section_rejected(self):
        t = _svc()
        t.create_table("T1", section="main")
        with pytest.raises(t.TableError):
            t.create_table("T1", section="main")
        # Same name in a different section is fine.
        table = t.create_table("T1", section="bar")
        assert table.section == "bar"


class TestStatusTransitions:
    def test_update_status(self):
        t = _svc()
        RestaurantTable, _ = _models()
        table = RestaurantTable.objects.create(name="T2", section="main", capacity=2)
        table = t.update_status(table, "cleaning")
        assert table.status == "cleaning"

    def test_unknown_status_rejected(self):
        t = _svc()
        RestaurantTable, _ = _models()
        table = RestaurantTable.objects.create(name="T2", section="main", capacity=2)
        with pytest.raises(t.TableError):
            t.update_status(table, "vaporized")

    def test_occupied_requires_sale(self):
        t = _svc()
        RestaurantTable, _ = _models()
        table = RestaurantTable.objects.create(name="T2", section="main", capacity=2)
        with pytest.raises(t.TableError):
            t.update_status(table, "occupied")

    def test_cannot_free_occupied_table_with_sale(self):
        t = _svc()
        RestaurantTable, _ = _models()
        sale = _sale()
        table = RestaurantTable.objects.create(
            name="T2", section="main", capacity=2,
            status="occupied", current_sale=sale,
        )
        with pytest.raises(t.TableError):
            t.update_status(table, "free")


class TestOccupyClear:
    def test_occupy_seats_sale(self):
        t = _svc()
        RestaurantTable, _ = _models()
        sale = _sale()
        table = RestaurantTable.objects.create(name="T12", section="main", capacity=2)
        table = t.occupy_table(table, sale)
        assert table.status == "occupied"
        assert table.current_sale_id == sale.pk

    def test_occupy_syncs_sale_group_table_number(self):
        t = _svc()
        RestaurantTable, _ = _models()
        from models.pos import SaleGroup
        sale = _sale()
        group = SaleGroup.objects.create(
            group_key="grp-tables-1", name="T12 party", table_number="OLD",
        )
        sale.group = group
        sale.save(update_fields=["group"])
        table = RestaurantTable.objects.create(name="T12", section="main", capacity=2)
        t.occupy_table(table, sale)
        group.refresh_from_db()
        assert group.table_number == "T12"

    def test_occupy_requires_sale(self):
        t = _svc()
        RestaurantTable, _ = _models()
        table = RestaurantTable.objects.create(name="T12", section="main", capacity=2)
        with pytest.raises(t.TableError):
            t.occupy_table(table, None)

    def test_occupy_rejects_other_sale_on_occupied_table(self):
        t = _svc()
        RestaurantTable, _ = _models()
        sale1 = _sale()
        sale2 = _sale()
        table = RestaurantTable.objects.create(
            name="T12", section="main", capacity=2,
            status="occupied", current_sale=sale1,
        )
        with pytest.raises(t.TableError):
            t.occupy_table(table, sale2)

    def test_clear_frees_table_and_drops_sale(self):
        t = _svc()
        RestaurantTable, _ = _models()
        sale = _sale()
        table = RestaurantTable.objects.create(
            name="T12", section="main", capacity=2,
            status="occupied", current_sale=sale,
        )
        table = t.clear_table(table)
        assert table.status == "free"
        assert table.current_sale_id is None

    def test_clear_with_close_sale_completes_pending_sale(self):
        t = _svc()
        RestaurantTable, _ = _models()
        sale = _sale()
        table = RestaurantTable.objects.create(
            name="T12", section="main", capacity=2,
            status="occupied", current_sale=sale,
        )
        t.clear_table(table, close_sale=True)
        sale.refresh_from_db()
        assert sale.status == "completed"


class TestFloorSummary:
    def test_floor_summary_counts(self):
        t = _svc()
        RestaurantTable, _ = _models()
        RestaurantTable.objects.create(name="A", section="main", capacity=2)
        RestaurantTable.objects.create(name="B", section="main", capacity=4)
        RestaurantTable.objects.create(name="C", section="patio", capacity=2, status="cleaning")

        summary = t.floor_summary()
        assert summary["total_tables"] == 3
        assert summary["total_capacity"] == 8
        assert summary["status_counts"] == {"free": 2, "cleaning": 1}
        assert summary["section_counts"] == {"main": 2, "patio": 1}
        assert summary["section_capacity"] == {"main": 6, "patio": 2}
        assert summary["free_tables"] == 2
        assert summary["occupied_tables"] == 0


class TestReservations:
    def test_create_reservation(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        when = timezone.now() + timedelta(hours=1)
        res = t.create_reservation(
            table, when, party_size=3, customer_name="Aisha",
        )
        assert res.status == "confirmed"
        assert res.party_size == 3
        assert res.display_name == "Aisha"

    def test_reservation_rejects_occupied_table(self):
        t = _svc()
        RestaurantTable, _ = _models()
        sale = _sale()
        table = RestaurantTable.objects.create(
            name="T5", section="main", capacity=4,
            status="occupied", current_sale=sale,
        )
        with pytest.raises(t.TableError):
            t.create_reservation(table, timezone.now() + timedelta(hours=1))

    def test_cancel_reservation(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        res = t.cancel_reservation(res)
        assert res.status == "cancelled"

    def test_cancel_twice_rejected(self):
        t = _svc()
        RestaurantTable, _ = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        t.cancel_reservation(res)
        with pytest.raises(t.TableError):
            t.cancel_reservation(res)

    def test_seat_reservation_with_sale_occupies_table(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        sale = _sale()
        res = t.seat_reservation(res, sale=sale)
        assert res.status == "seated"
        assert res.seated_at is not None
        table.refresh_from_db()
        assert table.status == "occupied"
        assert table.current_sale_id == sale.pk

    def test_seat_reservation_requires_confirmed(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        res = t.cancel_reservation(res)
        with pytest.raises(t.TableError):
            t.seat_reservation(res)

    def test_complete_reservation(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        res = t.seat_reservation(res)
        res = t.complete_reservation(res)
        assert res.status == "completed"
        assert res.completed_at is not None

    def test_no_show(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        res = t.no_show_reservation(res)
        assert res.status == "no_show"

    def test_no_show_on_completed_rejected(self):
        t = _svc()
        RestaurantTable, TableReservation = _models()
        table = RestaurantTable.objects.create(name="T5", section="main", capacity=4)
        res = t.create_reservation(table, timezone.now() + timedelta(hours=1))
        res = t.complete_reservation(t.seat_reservation(res))
        with pytest.raises(t.TableError):
            t.no_show_reservation(res)
