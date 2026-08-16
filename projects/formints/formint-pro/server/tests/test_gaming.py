"""
POS-KO Gaming Center (P0) — token-based session tests.

Covers ``services.gaming``:
  * ``start_session`` — station availability + token validation.
  * ``pause_session`` / ``resume_session`` — clock freeze/unfreeze.
  * ``stop_session`` — cost from duration × hourly rate, token decrement,
    station freed, auto-assign next queue entry; ``cancelled`` voids billing.
  * ``enqueue`` / ``assign_next`` / ``estimated_wait_minutes`` — waitlist.

Time is controlled by rewinding ``GamingSession.last_resume_at`` so tests are
deterministic without a clock-mocking dependency. Django models and the
service are imported lazily (the conftest ``django_bootstrap`` fixture
configures Django first).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from django.utils import timezone


def _svc():
    import services.gaming as g

    return g


def _models():
    from models.gaming import (
        GamingQueueEntry,
        GamingSession,
        GamingStation,
        GamingToken,
    )
    return GamingQueueEntry, GamingSession, GamingStation, GamingToken


def make_station(**kwargs):
    _, _, GamingStation, _ = _models()
    defaults = {
        "name": kwargs.pop("name", "Station A"),
        "slug": kwargs.pop("slug", "station-a"),
        "station_type": "pc",
        "status": kwargs.pop("status", "available"),
        "hourly_rate": kwargs.pop("hourly_rate", 10),
        "is_active": True,
    }
    defaults.update(kwargs)
    return GamingStation.objects.create(**defaults)


def make_token(**kwargs):
    _, _, _, GamingToken = _models()
    minutes = kwargs.pop("minutes", 60)
    defaults = {
        "name": kwargs.pop("name", "1 Hour"),
        "minutes": minutes,
        "price": kwargs.pop("price", 5),
        "remaining_minutes": kwargs.pop("remaining_minutes", minutes),
    }
    defaults.update(kwargs)
    return GamingToken.objects.create(**defaults)


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    GamingQueueEntry, GamingSession, GamingStation, GamingToken = _models()
    GamingQueueEntry.objects.all().delete()
    GamingSession.objects.all().delete()
    GamingToken.objects.all().delete()
    GamingStation.objects.all().delete()
    yield


# ── start_session ──────────────────────────────────────────────────────────

class TestStartSession:
    def test_creates_active_session_and_occupies_station(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        station.refresh_from_db()
        assert session.status == "active"
        assert session.active_seconds == 0
        assert station.status == "occupied"

    def test_rejects_occupied_station(self):
        g = _svc()
        station = make_station(status="occupied")
        with pytest.raises(g.GamingError):
            g.start_session(station.id)

    def test_rejects_maintenance_station(self):
        g = _svc()
        station = make_station(status="maintenance")
        with pytest.raises(g.GamingError):
            g.start_session(station.id)

    def test_rejects_missing_station(self):
        g = _svc()
        with pytest.raises(g.GamingError):
            g.start_session(9999)

    def test_rejects_exhausted_token(self):
        g = _svc()
        station = make_station()
        token = make_token(remaining_minutes=0, status="used")
        with pytest.raises(g.GamingError):
            g.start_session(station.id, token_id=token.id)

    def test_accepts_token_with_balance(self):
        g = _svc()
        station = make_station()
        token = make_token(remaining_minutes=30)
        session = g.start_session(station.id, token_id=token.id)
        assert session.token_id == token.id


# ── pause / resume ─────────────────────────────────────────────────────────

class TestPauseResume:
    def test_pause_accumulates_active_seconds(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        session.last_resume_at = timezone.now() - timedelta(minutes=30)
        session.save(update_fields=["last_resume_at"])

        session = g.pause_session(session.id)
        assert session.status == "paused"
        assert session.active_seconds == 30 * 60

    def test_pause_on_inactive_session_raises(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        g.stop_session(session.id)
        with pytest.raises(g.GamingError):
            g.pause_session(session.id)

    def test_resume_restarts_clock(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        session.last_resume_at = timezone.now() - timedelta(minutes=10)
        session.save(update_fields=["last_resume_at"])
        g.pause_session(session.id)

        session = g.resume_session(session.id)
        assert session.status == "active"
        assert session.paused_at is None

    def test_resume_on_non_paused_raises(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        with pytest.raises(g.GamingError):
            g.resume_session(session.id)


# ── stop_session ───────────────────────────────────────────────────────────

class TestStopSession:
    def test_cost_from_duration_times_rate(self):
        g = _svc()
        station = make_station(hourly_rate=10)
        session = g.start_session(station.id)
        session.last_resume_at = timezone.now() - timedelta(minutes=30)
        session.save(update_fields=["last_resume_at"])

        session = g.stop_session(session.id)
        station.refresh_from_db()
        assert session.status == "completed"
        assert session.active_seconds == 30 * 60
        assert float(session.cost) == 5.0  # 0.5h × $10
        assert station.status == "available"

    def test_bills_per_started_minute(self):
        g = _svc()
        station = make_station(hourly_rate=60)  # $1/min
        session = g.start_session(station.id)
        session.last_resume_at = timezone.now() - timedelta(seconds=90)
        session.save(update_fields=["last_resume_at"])

        session = g.stop_session(session.id)
        # 90s → 2 started minutes → $2.00
        assert float(session.cost) == 2.0

    def test_decrements_token_by_billable_minutes(self):
        g = _svc()
        station = make_station()
        token = make_token(minutes=60, remaining_minutes=60)
        session = g.start_session(station.id, token_id=token.id)
        session.last_resume_at = timezone.now() - timedelta(minutes=25)
        session.save(update_fields=["last_resume_at"])

        g.stop_session(session.id)
        token.refresh_from_db()
        assert token.remaining_minutes == 35
        assert token.status == "active"

    def test_exhausts_token_when_balance_hits_zero(self):
        g = _svc()
        station = make_station()
        token = make_token(minutes=30, remaining_minutes=30)
        session = g.start_session(station.id, token_id=token.id)
        session.last_resume_at = timezone.now() - timedelta(minutes=30)
        session.save(update_fields=["last_resume_at"])

        g.stop_session(session.id)
        token.refresh_from_db()
        assert token.remaining_minutes == 0
        assert token.status == "used"

    def test_cancelled_session_has_no_cost_and_no_token_decrement(self):
        g = _svc()
        station = make_station(hourly_rate=10)
        token = make_token(minutes=60, remaining_minutes=60)
        session = g.start_session(station.id, token_id=token.id)
        session.last_resume_at = timezone.now() - timedelta(minutes=40)
        session.save(update_fields=["last_resume_at"])

        session = g.stop_session(session.id, cancelled=True)
        token.refresh_from_db()
        station.refresh_from_db()
        assert session.status == "cancelled"
        assert float(session.cost) == 0.0
        assert token.remaining_minutes == 60
        assert station.status == "available"

    def test_auto_assigns_next_queue_entry_on_stop(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        g.enqueue("Jane", requested_minutes=30)

        g.stop_session(session.id)

        GamingQueueEntry, *_ = _models()
        entry = GamingQueueEntry.objects.get(customer_name="Jane")
        assert entry.status == "assigned"
        assert entry.station_id == station.id

    def test_stop_on_already_ended_raises(self):
        g = _svc()
        station = make_station()
        session = g.start_session(station.id)
        g.stop_session(session.id)
        with pytest.raises(g.GamingError):
            g.stop_session(session.id)


# ── queue ──────────────────────────────────────────────────────────────────

class TestQueue:
    def test_enqueue_and_wait_estimate(self):
        g = _svc()
        first = g.enqueue("Alice")
        second = g.enqueue("Bob")
        assert first.status == "waiting"
        # Alice is next → 0 min; Bob has one ahead → 30 min.
        assert g.estimated_wait_minutes(first) == 0
        assert g.estimated_wait_minutes(second) == 30

    def test_enqueue_requires_name(self):
        g = _svc()
        with pytest.raises(g.GamingError):
            g.enqueue("   ")

    def test_assign_next_marks_oldest_waiting_entry(self):
        g = _svc()
        station = make_station()
        first = g.enqueue("Alice")
        g.enqueue("Bob")

        assigned = g.assign_next(station)
        assert assigned.id == first.id
        assert assigned.status == "assigned"
        assert assigned.station_id == station.id

    def test_assign_next_returns_none_when_queue_empty(self):
        g = _svc()
        assert g.assign_next() is None

    def test_assign_next_picks_first_free_station(self):
        g = _svc()
        make_station(name="Busy", slug="busy", status="occupied")
        free = make_station(name="Free", slug="free")
        g.enqueue("Alice")

        assigned = g.assign_next()
        assert assigned.station_id == free.id

    def test_cancel_queue_entry(self):
        g = _svc()
        entry = g.enqueue("Alice")
        entry = g.cancel_queue_entry(entry.id)
        assert entry.status == "cancelled"

    def test_cancel_non_waiting_raises(self):
        g = _svc()
        station = make_station()
        entry = g.enqueue("Alice")
        g.assign_next(station)
        with pytest.raises(g.GamingError):
            g.cancel_queue_entry(entry.id)
