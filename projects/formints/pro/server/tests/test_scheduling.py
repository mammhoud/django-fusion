"""
Employee Scheduling (P3) — shift planning + time clock tests.

Covers ``services.scheduling``:
  * ``upsert_shift`` — create/update, day/order validation.
  * ``week_schedule`` — concrete week roster with planned hours.
  * ``coverage`` — staffing counts per day of the week.
  * ``clock_in`` / ``clock_out`` / ``toggle_break`` — time tracking with a
    single-active-punch guard; worked minutes subtract breaks.
  * ``worked_hours`` — hours, overtime (beyond 8/day), pay estimate.
  * ``timeclock_summary`` — active staff + recent punches.

Models and the service are imported lazily (the conftest ``django_bootstrap``
fixture configures Django first).
"""

from __future__ import annotations

from datetime import datetime, time, timedelta

import pytest

from django.utils import timezone as dj_tz


def _svc():
    import services.scheduling as s

    return s


@pytest.fixture(autouse=True)
def _clean(django_bootstrap):
    from models.timeclock import TimeClockEntry
    from models.hr import EmployeeSchedule
    TimeClockEntry.objects.all().delete()
    EmployeeSchedule.objects.all().delete()
    yield


def _employee(rate=15.0):
    from models.pos import Employee

    return Employee.objects.create(
        first_name="Sam", last_name="Staff",
        email="sam@test.com", role="server", hourly_rate=rate,
    )


class TestShifts:
    def test_upsert_shift(self):
        s = _svc()
        emp = _employee()
        shift = s.upsert_shift(
            emp, "monday", time(9, 0), time(17, 0),
            status="confirmed", notes="Opening",
        )
        assert shift.day_of_week == "monday"
        assert shift.start_time == time(9, 0)
        assert shift.end_time == time(17, 0)
        assert shift.status == "confirmed"

    def test_upsert_replaces_same_day(self):
        s = _svc()
        emp = _employee()
        s.upsert_shift(emp, "tuesday", time(9, 0), time(17, 0))
        s.upsert_shift(emp, "tuesday", time(10, 0), time(18, 0))
        from models.hr import EmployeeSchedule
        assert EmployeeSchedule.objects.filter(employee=emp).count() == 1
        shift = EmployeeSchedule.objects.get(employee=emp)
        assert shift.start_time == time(10, 0)

    def test_invalid_day_rejected(self):
        s = _svc()
        emp = _employee()
        with pytest.raises(s.SchedulingError):
            s.upsert_shift(emp, "funday", time(9, 0), time(17, 0))

    def test_end_before_start_rejected(self):
        s = _svc()
        emp = _employee()
        with pytest.raises(s.SchedulingError):
            s.upsert_shift(emp, "monday", time(17, 0), time(9, 0))

    def test_week_schedule_roster(self):
        s = _svc()
        emp = _employee()
        s.upsert_shift(emp, "monday", time(9, 0), time(17, 0))
        s.upsert_shift(emp, "wednesday", time(10, 0), time(14, 0))
        monday = datetime(2026, 8, 17)  # a Monday
        result = s.week_schedule(monday)
        assert result["week_start"] == "2026-08-17"
        assert len(result["days"]) == 7
        emp_row = result["employees"][0]
        assert emp_row["total_planned_hours"] == 12.0  # 8 + 4
        assert len(emp_row["shifts"]) == 2

    def test_coverage_per_day(self):
        s = _svc()
        emp1 = _employee()
        emp2 = _employee(rate=20.0)
        s.upsert_shift(emp1, "monday", time(9, 0), time(17, 0))
        s.upsert_shift(emp2, "monday", time(11, 0), time(19, 0))
        result = s.coverage("monday")
        day = next(r for r in result["coverage"] if r["day_of_week"] == "monday")
        assert day["staff_count"] == 2
        assert day["planned_hours"] == 16.0


class TestTimeClock:
    def test_clock_in_creates_active_entry(self):
        s = _svc()
        emp = _employee()
        entry = s.clock_in(emp, note="start")
        assert entry.is_active is True
        assert entry.clock_out is None

    def test_double_clock_in_rejected(self):
        s = _svc()
        emp = _employee()
        s.clock_in(emp)
        with pytest.raises(s.SchedulingError):
            s.clock_in(emp)

    def test_clock_out_computes_hours(self):
        s = _svc()
        emp = _employee()
        entry = s.clock_in(emp)
        entry.clock_in = dj_tz.now() - timedelta(hours=8)
        entry.save(update_fields=["clock_in"])
        entry = s.clock_out(emp)
        assert entry.is_active is False
        assert entry.worked_hours == 8.0

    def test_clock_out_without_punch_rejected(self):
        s = _svc()
        emp = _employee()
        with pytest.raises(s.SchedulingError):
            s.clock_out(emp)

    def test_break_accumulates(self):
        s = _svc()
        emp = _employee()
        entry = s.clock_in(emp)
        entry.clock_in = dj_tz.now() - timedelta(hours=6)
        entry.save(update_fields=["clock_in"])
        entry = s.toggle_break(emp)  # start break
        entry.clock_in = dj_tz.now() - timedelta(hours=6)
        entry.save(update_fields=["clock_in"])
        s.toggle_break(emp)  # end break (elapsed ≈ 0)
        assert entry.break_minutes >= 0
        entry = s.clock_out(emp)
        assert entry.worked_hours <= 6.0

    def test_worked_hours_with_overtime(self):
        s = _svc()
        emp = _employee(rate=15.0)
        entry = s.clock_in(emp)
        entry.clock_in = dj_tz.now() - timedelta(hours=10)
        entry.save(update_fields=["clock_in"])
        s.clock_out(emp)

        today = dj_tz.localdate()
        result = s.worked_hours(emp, today, today)
        assert result["total_hours"] == 10.0
        assert result["regular_hours"] == 8.0
        assert result["overtime_hours"] == 2.0
        # 8h * 15 + 2h * 1.5 * 15 = 120 + 45 = 165
        assert result["estimated_pay"] == 165.0

    def test_worked_hours_empty(self):
        s = _svc()
        emp = _employee()
        today = dj_tz.localdate()
        result = s.worked_hours(emp, today, today)
        assert result["total_hours"] == 0.0
        assert result["estimated_pay"] == 0.0

    def test_timeclock_summary_lists_active(self):
        s = _svc()
        emp = _employee()
        s.clock_in(emp)
        summary = s.timeclock_summary(days=7)
        assert len(summary["active_staff"]) == 1
        assert summary["active_staff"][0]["employee_id"] == emp.id
        assert len(summary["recent_entries"]) == 1
