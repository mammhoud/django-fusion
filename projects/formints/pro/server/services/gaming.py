"""POS Full — POS-KO Gaming Center service (P0).

Implements token-based session lifecycle and queue management on top of the
``GamingStation`` / ``GamingToken`` / ``GamingSession`` / ``GamingQueueEntry``
models:

* ``start_session``  — begin a session on an available station (optionally
                        drawing from a time token), mark the station occupied.
* ``pause_session``  — freeze the clock; accumulate active seconds so far.
* ``resume_session`` — restart the clock from the pause point.
* ``stop_session``   — finalise time, compute ``cost = duration × hourly_rate``,
                        decrement the token's remaining minutes, free the
                        station, and auto-assign the next waiting entry.
* ``enqueue`` / ``assign_next`` — waitlist management with a rough estimated
                        wait time (``ahead × 30 min``).

Time accounting: ``active_seconds`` is accumulated at every pause/stop
boundary from ``last_resume_at`` (the moment the current active run began),
so pause/resume cycles are excluded from billable time.  Cost is billed per
started minute (``ceil(active_seconds / 60)``) at the station's hourly rate.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from math import ceil

from django.db import transaction
from django.utils import timezone

from models.gaming import GamingQueueEntry, GamingSession, GamingStation, GamingToken

# Rough per-station turnover used for the waitlist estimate (minutes).
_AVG_SESSION_MINUTES = 30


class GamingError(ValueError):
    """Raised for invalid gaming operations (bad ids, wrong status, …)."""


def _now():
    return timezone.now()


def _elapsed_seconds(session: GamingSession, now=None) -> int:
    """Active seconds *including* the current run (if the session is active)."""
    now = now or _now()
    if session.status == "active":
        return session.active_seconds + int(
            (now - session.last_resume_at).total_seconds()
        )
    return session.active_seconds


def _billable_minutes(active_seconds: int) -> int:
    """Round active seconds up to whole minutes (minimum 1 when any time used)."""
    return max(ceil(active_seconds / 60), 1) if active_seconds > 0 else 0


def _compute_cost(station: GamingStation, active_seconds: int) -> Decimal:
    minutes = _billable_minutes(active_seconds)
    hours = Decimal(minutes) / Decimal(60)
    return (hours * station.hourly_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP,
    )


def _free_station(station: GamingStation) -> None:
    station.status = "available"
    station.save(update_fields=["status", "updated_at"])


# ══════════════════════════════════════════════════════════════════════════
# Session lifecycle
# ══════════════════════════════════════════════════════════════════════════


def start_session(
    station_id: int,
    token_id: int | None = None,
    customer_id: int | None = None,
) -> GamingSession:
    """Start a session on an available station.

    ``token_id`` optionally ties the session to a time token (whose remaining
    minutes are decremented when the session stops). Raises ``GamingError`` if
    the station is missing/inactive/not available, or the token is exhausted.
    """
    try:
        station = GamingStation.objects.get(id=station_id, is_active=True)
    except GamingStation.DoesNotExist as exc:
        raise GamingError(f"station {station_id} not found or inactive") from exc

    if station.status != "available":
        raise GamingError(f"station {station_id} is not available ({station.status})")

    token = None
    if token_id is not None:
        try:
            token = GamingToken.objects.get(id=token_id)
        except GamingToken.DoesNotExist as exc:
            raise GamingError(f"token {token_id} not found") from exc
        if token.is_exhausted:
            raise GamingError(f"token {token_id} has no remaining minutes")

    with transaction.atomic():
        station.status = "occupied"
        station.save(update_fields=["status", "updated_at"])

        now = _now()
        session = GamingSession.objects.create(
            station=station,
            token=token,
            customer_id=customer_id,
            status="active",
            started_at=now,
            last_resume_at=now,
            active_seconds=0,
            cost=Decimal("0"),
        )
    return session


def pause_session(session_id: int) -> GamingSession:
    """Freeze the clock on an active session, accumulating elapsed time."""
    session = _get_session(session_id)
    if session.status != "active":
        raise GamingError(f"session {session_id} is not active ({session.status})")

    now = _now()
    session.active_seconds = _elapsed_seconds(session, now)
    session.paused_at = now
    session.status = "paused"
    session.save(update_fields=["active_seconds", "paused_at", "status", "updated_at"])
    return session


def resume_session(session_id: int) -> GamingSession:
    """Restart the clock on a paused session."""
    session = _get_session(session_id)
    if session.status != "paused":
        raise GamingError(f"session {session_id} is not paused ({session.status})")

    now = _now()
    session.last_resume_at = now
    session.paused_at = None
    session.status = "active"
    session.save(update_fields=["last_resume_at", "paused_at", "status", "updated_at"])
    return session


def stop_session(session_id: int, *, cancelled: bool = False) -> GamingSession:
    """Finalise a session: bill time, decrement token, free the station.

    When ``cancelled`` is True the session is voided — no cost and no token
    decrement, but the station is still freed.  After freeing the station, the
    oldest waiting queue entry (if any) is auto-assigned to it.
    """
    session = _get_session(session_id)
    if session.status in ("completed", "cancelled"):
        raise GamingError(f"session {session_id} already ended ({session.status})")

    now = _now()
    active_seconds = _elapsed_seconds(session, now)

    with transaction.atomic():
        if cancelled:
            session.cost = Decimal("0")
        else:
            session.cost = _compute_cost(session.station, active_seconds)
            _decrement_token(session, active_seconds)

        session.active_seconds = active_seconds
        session.status = "cancelled" if cancelled else "completed"
        session.ended_at = now
        session.last_resume_at = now
        session.save(update_fields=[
            "active_seconds", "cost", "status", "ended_at", "last_resume_at",
            "updated_at",
        ])

        _free_station(session.station)
        assign_next(session.station)
    return session


def _get_session(session_id: int) -> GamingSession:
    try:
        return GamingSession.objects.get(id=session_id)
    except GamingSession.DoesNotExist as exc:
        raise GamingError(f"session {session_id} not found") from exc


def _decrement_token(session: GamingSession, active_seconds: int) -> None:
    """Consume billable minutes from the session's token (if any)."""
    token = session.token
    if token is None:
        return
    minutes = _billable_minutes(active_seconds)
    if minutes <= 0:
        return
    token.remaining_minutes = max(0, token.remaining_minutes - minutes)
    if token.remaining_minutes == 0:
        token.status = "used"
    token.save(update_fields=["remaining_minutes", "status"])


# ══════════════════════════════════════════════════════════════════════════
# Queue (waitlist)
# ══════════════════════════════════════════════════════════════════════════


def enqueue(customer_name: str, requested_minutes: int = 60) -> GamingQueueEntry:
    """Add a customer to the waitlist."""
    name = (customer_name or "").strip()
    if not name:
        raise GamingError("customer name is required")
    return GamingQueueEntry.objects.create(
        customer_name=name,
        requested_minutes=max(requested_minutes, 1),
        status="waiting",
    )


def estimated_wait_minutes(entry: GamingQueueEntry) -> int:
    """Rough wait estimate: number of waiting entries ahead × 30 minutes."""
    ahead = GamingQueueEntry.objects.filter(
        status="waiting",
        created_at__lt=entry.created_at,
    ).count()
    return ahead * _AVG_SESSION_MINUTES


def assign_next(station: GamingStation | None = None) -> GamingQueueEntry | None:
    """Assign the oldest waiting entry to ``station`` (or the first free one).

    Marking an entry ``assigned`` reserves the next available spot for it but
    does not change station status — the operator still calls ``start_session``
    when the customer sits down. Returns the assigned entry, or None when the
    waitlist is empty or no free station exists.
    """
    entry = GamingQueueEntry.objects.filter(status="waiting").order_by("created_at").first()
    if entry is None:
        return None

    if station is None:
        station = GamingStation.objects.filter(
            is_active=True, status="available",
        ).order_by("name").first()

    if station is None:
        return None

    entry.status = "assigned"
    entry.station = station
    entry.assigned_at = _now()
    entry.save(update_fields=["status", "station", "assigned_at"])
    return entry


def cancel_queue_entry(entry_id: int) -> GamingQueueEntry:
    """Cancel a waiting queue entry."""
    try:
        entry = GamingQueueEntry.objects.get(id=entry_id)
    except GamingQueueEntry.DoesNotExist as exc:
        raise GamingError(f"queue entry {entry_id} not found") from exc
    if entry.status != "waiting":
        raise GamingError(f"queue entry {entry_id} is not waiting ({entry.status})")
    entry.status = "cancelled"
    entry.completed_at = _now()
    entry.save(update_fields=["status", "completed_at"])
    return entry
