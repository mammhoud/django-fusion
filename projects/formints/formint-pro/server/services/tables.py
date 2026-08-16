"""POS Full — Table Management service (P2, Professional+).

Implements restaurant floor management and order tracking on top of
``RestaurantTable`` / ``TableReservation``:

* ``create_table`` / ``get_table`` / ``update_status`` — table lifecycle.
* ``occupy_table`` / ``clear_table``      — seat an open sale at a table and
  free it again (order tracking via ``RestaurantTable.current_sale``; the
  sale's linked ``SaleGroup.table_number`` is kept in sync when present).
* ``floor_summary``                       — status/capacity counts per section.
* ``create_reservation`` / ``cancel_reservation`` / ``seat_reservation`` /
  ``complete_reservation`` / ``no_show_reservation`` — booking lifecycle.

Status transitions are validated so an occupied table can't silently become
``free`` while a sale is still seated, and reservations only apply to tables
that are actually free (or already reserved for that booking).
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from models.tables import RestaurantTable, TableReservation


class TableError(ValueError):
    """Raised for invalid table / reservation operations."""


# ── Tables ───────────────────────────────────────────────────────────────

def create_table(
    name: str,
    section: str = "main",
    capacity: int = 2,
    shape: str = "rect",
    pos_x: int = 0,
    pos_y: int = 0,
    width: int = 1,
    height: int = 1,
    notes: str = "",
) -> RestaurantTable:
    """Create a table on the floor plan (name unique within a section)."""
    name = (name or "").strip()
    if not name:
        raise TableError("table name is required")
    if capacity <= 0:
        raise TableError("capacity must be positive")
    if RestaurantTable.objects.filter(section=section, name=name).exists():
        raise TableError(f"table '{name}' already exists in section '{section}'")
    return RestaurantTable.objects.create(
        name=name,
        section=section,
        capacity=capacity,
        shape=shape,
        pos_x=pos_x,
        pos_y=pos_y,
        width=width,
        height=height,
        notes=notes or "",
    )


def get_table(table_id) -> RestaurantTable | None:
    """Fetch a table by pk, or None."""
    return RestaurantTable.objects.filter(pk=table_id).first()


def update_status(table: RestaurantTable, status: str) -> RestaurantTable:
    """Transition a table to ``status`` (guarding sale integrity).

    * ``occupied`` requires ``current_sale`` set (use ``occupy_table``).
    * A table with an open seated sale cannot be moved to ``free``/``closed``.
    """
    valid = {choice for choice, _ in RestaurantTable.STATUS_CHOICES}
    if status not in valid:
        raise TableError(f"unknown status '{status}'")
    if status == "occupied" and table.current_sale_id is None:
        raise TableError("occupy a table with occupy_table() and a current sale")
    if status in ("free", "closed") and table.current_sale_id is not None:
        raise TableError("clear the seated sale first (clear_table)")
    table.status = status
    table.save(update_fields=["status", "updated_at"])
    return table


def occupy_table(table: RestaurantTable, sale) -> RestaurantTable:
    """Seat an open sale at a table (order tracking).

    Marks the table ``occupied`` and links ``current_sale``. Tables that are
    ``closed`` or already occupied by a *different* sale are rejected.
    """
    if sale is None or not sale.pk:
        raise TableError("a sale is required to occupy a table")
    if table.status == "closed":
        raise TableError("table is closed")
    if table.status == "occupied" and table.current_sale_id != sale.pk:
        raise TableError(f"table is already occupied by sale #{table.current_sale_id}")

    with transaction.atomic():
        table = RestaurantTable.objects.select_for_update().get(pk=table.pk)
        table.current_sale = sale
        table.status = "occupied"
        table.save(update_fields=["current_sale", "status", "updated_at"])
        # Keep the sale's group (split-bill session) table reference in sync
        # when one is already linked to the sale.
        group = getattr(sale, "group", None)
        if group is not None and group.table_number != table.name:
            group.table_number = table.name
            group.save(update_fields=["table_number"])
    return table


def clear_table(table: RestaurantTable, close_sale: bool = False) -> RestaurantTable:
    """Free a table after the seated sale is settled.

    ``close_sale=True`` also marks the linked sale ``completed``. The table
    returns to ``free`` and its ``current_sale`` link is dropped.
    """
    with transaction.atomic():
        table = RestaurantTable.objects.select_for_update().get(pk=table.pk)
        sale = table.current_sale
        if close_sale and sale is not None and sale.status == "pending":
            sale.status = "completed"
            sale.save(update_fields=["status", "updated_at"])
        table.current_sale = None
        table.status = "free"
        table.save(update_fields=["current_sale", "status", "updated_at"])
    return table


def floor_summary() -> dict:
    """Aggregate floor-plan stats: counts per status, per section, capacity."""
    tables = RestaurantTable.objects.all()
    status_counts: dict[str, int] = {}
    section_counts: dict[str, int] = {}
    section_capacity: dict[str, int] = {}
    for t in tables:
        status_counts[t.status] = status_counts.get(t.status, 0) + 1
        section_counts[t.section] = section_counts.get(t.section, 0) + 1
        section_capacity[t.section] = section_capacity.get(t.section, 0) + t.capacity
    return {
        "total_tables": tables.count(),
        "total_capacity": sum(t.capacity for t in tables),
        "status_counts": status_counts,
        "section_counts": section_counts,
        "section_capacity": section_capacity,
        "occupied_tables": status_counts.get("occupied", 0),
        "free_tables": status_counts.get("free", 0),
    }


# ── Reservations ─────────────────────────────────────────────────────────

def create_reservation(
    table: RestaurantTable,
    reservation_time,
    party_size: int = 1,
    customer=None,
    customer_name: str = "",
    notes: str = "",
) -> TableReservation:
    """Book a table for a party (only free/reserved tables are bookable)."""
    if reservation_time is None:
        raise TableError("reservation_time is required")
    if party_size <= 0:
        raise TableError("party_size must be positive")
    if table.status == "closed":
        raise TableError("table is closed")
    if table.status == "occupied":
        raise TableError(f"table '{table.name}' is occupied")
    if table.status == "cleaning":
        raise TableError(f"table '{table.name}' is being cleaned")

    return TableReservation.objects.create(
        table=table,
        customer=customer,
        customer_name=(customer_name or "").strip(),
        party_size=party_size,
        reservation_time=reservation_time,
        notes=notes or "",
    )


def get_reservation(reservation_id) -> TableReservation | None:
    """Fetch a reservation by pk, or None."""
    return TableReservation.objects.filter(pk=reservation_id).first()


def cancel_reservation(reservation: TableReservation) -> TableReservation:
    """Cancel a confirmed/upcoming reservation."""
    if reservation.status in ("completed", "cancelled", "no_show"):
        raise TableError(f"reservation is already {reservation.status}")
    reservation.status = "cancelled"
    reservation.save(update_fields=["status", "updated_at"])
    return reservation


def seat_reservation(reservation: TableReservation, sale=None) -> TableReservation:
    """Mark a reservation ``seated``; optionally attach the open sale.

    The table is occupied via ``occupy_table`` when ``sale`` is provided so
    the floor plan reflects the live order immediately.
    """
    if reservation.status not in ("confirmed",):
        raise TableError(f"cannot seat a {reservation.status} reservation")
    table = RestaurantTable.objects.select_for_update().get(pk=reservation.table_id)
    if table.status == "occupied" and table.current_sale_id:
        raise TableError(f"table '{table.name}' is already occupied")
    reservation.status = "seated"
    reservation.seated_at = timezone.now()
    reservation.save(update_fields=["status", "seated_at", "updated_at"])
    if sale is not None:
        occupy_table(table, sale)
    return reservation


def complete_reservation(reservation: TableReservation) -> TableReservation:
    """Close out a seated reservation once the party has paid."""
    if reservation.status != "seated":
        raise TableError(f"cannot complete a {reservation.status} reservation")
    reservation.status = "completed"
    reservation.completed_at = timezone.now()
    reservation.save(update_fields=["status", "completed_at", "updated_at"])
    return reservation


def no_show_reservation(reservation: TableReservation) -> TableReservation:
    """Mark a confirmed reservation as a no-show (frees the table)."""
    if reservation.status not in ("confirmed", "seated"):
        raise TableError(f"cannot mark a {reservation.status} reservation as no-show")
    reservation.status = "no_show"
    reservation.completed_at = timezone.now()
    reservation.save(update_fields=["status", "completed_at", "updated_at"])
    return reservation
