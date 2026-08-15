"""POS Full — Employee Scheduling service (P3, Professional).

Shift planning + time tracking on top of ``EmployeeSchedule`` (the weekly
plan) and ``TimeClockEntry`` (the actual punches):

* ``upsert_shift`` — create/update one employee's shift for a day of the week.
* ``week_schedule`` — materialize the repeating plan into a concrete week
  (roster per day with total planned hours).
* ``clock_in`` / ``clock_out`` / ``toggle_break`` — time tracking with a
  single-active-punch guard per employee.
* ``worked_hours`` — hours + overtime (beyond 8/day) + pay estimate from
  ``Employee.hourly_rate`` for a date range.
* ``coverage`` — how many staff are scheduled per day of the week.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from models.hr import EmployeeSchedule
from models.timeclock import TimeClockEntry


class SchedulingError(ValueError):
    """Raised for invalid scheduling / time-clock operations."""


# ── Shifts ───────────────────────────────────────────────────────────────

def upsert_shift(
    employee,
    day_of_week: str,
    start_time,
    end_time,
    status: str = "scheduled",
    notes: str = "",
) -> EmployeeSchedule:
    """Create or replace an employee's shift for a day of the week."""
    valid_days = {choice for choice, _ in EmployeeSchedule.DAY_CHOICES}
    if day_of_week not in valid_days:
        raise SchedulingError(f"unknown day_of_week '{day_of_week}'")
    if start_time is None or end_time is None:
        raise SchedulingError("start_time and end_time are required")
    if start_time >= end_time:
        raise SchedulingError("start_time must be before end_time")

    shift, _ = EmployeeSchedule.objects.update_or_create(
        employee=employee,
        day_of_week=day_of_week,
        defaults={
            "start_time": start_time,
            "end_time": end_time,
            "status": status,
            "notes": notes or "",
        },
    )
    return shift


def list_shifts(employee_id=None, day_of_week: str | None = None) -> list[EmployeeSchedule]:
    qs = EmployeeSchedule.objects.select_related("employee")
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if day_of_week:
        qs = qs.filter(day_of_week=day_of_week)
    return list(qs.order_by("day_of_week", "start_time"))


def week_schedule(week_start) -> dict:
    """Materialize the repeating plan into a concrete week's roster.

    ``week_start`` is any date in the target week (a Monday is used if not
    already one). Returns per-employee and per-day breakdowns with planned
    hours.
    """
    from django.utils.dateparse import parse_date
    if isinstance(week_start, str):
        week_start = parse_date(week_start) or timezone.localdate()
    elif hasattr(week_start, "date"):
        week_start = week_start.date()
    monday = week_start - timedelta(days=week_start.weekday())
    days = [monday + timedelta(days=i) for i in range(7)]
    day_names = [d.strftime("%A").lower() for d in days]

    shifts = list(
        EmployeeSchedule.objects.filter(day_of_week__in=day_names)
        .select_related("employee")
    )
    by_employee: dict[int, dict] = {}
    by_day: dict[str, list] = {name: [] for name in day_names}

    for shift in shifts:
        emp = shift.employee
        planned_hours = (
            (shift.end_time.hour * 60 + shift.end_time.minute)
            - (shift.start_time.hour * 60 + shift.start_time.minute)
        ) / 60
        row = {
            "employee_id": emp.id,
            "employee_name": f"{emp.first_name} {emp.last_name}".strip(),
            "role": emp.role,
            "day_of_week": shift.day_of_week,
            "start_time": shift.start_time.isoformat(),
            "end_time": shift.end_time.isoformat(),
            "planned_hours": round(planned_hours, 2),
            "status": shift.status,
        }
        entry = by_employee.setdefault(emp.id, {
            "employee_id": emp.id,
            "employee_name": row["employee_name"],
            "role": emp.role,
            "total_planned_hours": 0.0,
            "shifts": [],
        })
        entry["total_planned_hours"] = round(entry["total_planned_hours"] + planned_hours, 2)
        entry["shifts"].append(row)
        by_day[shift.day_of_week].append(row)

    return {
        "week_start": monday.isoformat(),
        "days": [
            {"date": d.isoformat(), "day_of_week": name, "shifts": by_day[name]}
            for d, name in zip(days, day_names)
        ],
        "employees": list(by_employee.values()),
    }


def coverage(day_of_week: str | None = None) -> dict:
    """Staffing coverage per day of the week (staff count + planned hours)."""
    days = [choice for choice, _ in EmployeeSchedule.DAY_CHOICES]
    qs = EmployeeSchedule.objects.all()
    if day_of_week:
        if day_of_week not in days:
            raise SchedulingError(f"unknown day_of_week '{day_of_week}'")
        qs = qs.filter(day_of_week=day_of_week)

    coverage_rows = []
    for day in days:
        shifts = [s for s in qs if s.day_of_week == day] if not day_of_week else qs
        total_hours = sum(
            ((s.end_time.hour * 60 + s.end_time.minute)
             - (s.start_time.hour * 60 + s.start_time.minute)) / 60
            for s in shifts
        )
        coverage_rows.append({
            "day_of_week": day,
            "staff_count": len(shifts),
            "planned_hours": round(total_hours, 2),
        })
    return {"coverage": coverage_rows}


# ── Time clock ───────────────────────────────────────────────────────────

def _active_entry(employee) -> TimeClockEntry | None:
    return TimeClockEntry.objects.filter(
        employee=employee, clock_out__isnull=True,
    ).order_by("-clock_in").first()


def clock_in(employee, note: str = "", schedule=None) -> TimeClockEntry:
    """Start a shift; rejects double punches (one active entry per employee)."""
    if _active_entry(employee) is not None:
        raise SchedulingError(f"{employee} already has an active clock-in")
    return TimeClockEntry.objects.create(
        employee=employee, note=note or "", schedule=schedule,
    )


def clock_out(employee) -> TimeClockEntry:
    """Close the employee's active punch and compute worked minutes."""
    entry = _active_entry(employee)
    if entry is None:
        raise SchedulingError(f"{employee} has no active clock-in")
    with transaction.atomic():
        entry = TimeClockEntry.objects.select_for_update().get(pk=entry.pk)
        entry.clock_out = timezone.now()
        entry.save(update_fields=["clock_out", "updated_at"])
    return entry


def toggle_break(employee) -> TimeClockEntry:
    """Start or end a break on the employee's active punch.

    Starting a break just marks the moment; ending it adds the elapsed
    minutes to ``break_minutes``. Implemented by round-tripping through a
    ``_break_started_at`` marker stored on the entry's ``note`` (kept simple
    and single-table).
    """
    entry = _active_entry(employee)
    if entry is None:
        raise SchedulingError(f"{employee} has no active clock-in")

    marker = "_break_started_at="
    if marker in entry.note:
        # End the break.
        started = entry.note.split(marker, 1)[1].strip()
        try:
            from django.utils.dateparse import parse_datetime
            started_dt = parse_datetime(started)
        except Exception:
            started_dt = None
        if started_dt is None:
            raise SchedulingError("break marker is unreadable — end break manually")
        elapsed = max(int((timezone.now() - started_dt).total_seconds() // 60), 0)
        entry.break_minutes = (entry.break_minutes or 0) + elapsed
        entry.note = entry.note.replace(marker + started, "").strip()
        entry.save(update_fields=["break_minutes", "note", "updated_at"])
    else:
        # Start the break.
        entry.note = f"{entry.note} {marker}{timezone.now().isoformat()}".strip()
        entry.save(update_fields=["note", "updated_at"])
    return entry


def worked_hours(employee, start, end) -> dict:
    """Worked hours + overtime (beyond 8/day) + pay estimate for a range.

    ``start``/``end`` are dates (inclusive). Pay estimate uses
    ``Employee.hourly_rate`` (0 when unset).
    """
    entries = list(
        TimeClockEntry.objects.filter(
            employee=employee,
            clock_in__date__gte=start,
            clock_in__date__lte=end,
            clock_out__isnull=False,
        )
    )
    total_minutes = 0
    per_day: dict[str, int] = {}
    for e in entries:
        minutes = e.worked_minutes or 0
        total_minutes += minutes
        day = e.clock_in.date().isoformat()
        per_day[day] = per_day.get(day, 0) + minutes

    regular_minutes = 0
    overtime_minutes = 0
    for minutes in per_day.values():
        regular_minutes += min(minutes, 8 * 60)
        overtime_minutes += max(minutes - 8 * 60, 0)

    rate = Decimal(str(employee.hourly_rate or 0))
    pay = (rate * Decimal(regular_minutes) / Decimal(60)) + (
        Decimal("1.5") * rate * Decimal(overtime_minutes) / Decimal(60)
    )

    return {
        "employee_id": employee.id,
        "employee_name": f"{employee.first_name} {employee.last_name}".strip(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days_worked": len(per_day),
        "total_hours": round(total_minutes / 60, 2),
        "regular_hours": round(regular_minutes / 60, 2),
        "overtime_hours": round(overtime_minutes / 60, 2),
        "estimated_pay": float(pay),
    }


def timeclock_summary(days: int = 7) -> dict:
    """Recent punches + currently active staff."""
    days = max(1, min(int(days), 90))
    start = timezone.localdate() - timedelta(days=days - 1)
    recent = list(
        TimeClockEntry.objects.filter(clock_in__date__gte=start)
        .select_related("employee")
        .order_by("-clock_in")[:50]
    )
    # Active = open punches.
    open_entries = TimeClockEntry.objects.filter(clock_out__isnull=True).select_related("employee")
    active = [
        {
            "employee_id": e.employee.id,
            "employee_name": f"{e.employee.first_name} {e.employee.last_name}".strip(),
            "clock_in": e.clock_in.isoformat(),
        }
        for e in open_entries
    ]
    return {
        "window_days": days,
        "active_staff": active,
        "recent_entries": [
            {
                "id": e.id,
                "employee_id": e.employee.id,
                "employee_name": f"{e.employee.first_name} {e.employee.last_name}".strip(),
                "clock_in": e.clock_in.isoformat(),
                "clock_out": e.clock_out.isoformat() if e.clock_out else None,
                "worked_hours": e.worked_hours,
                "break_minutes": e.break_minutes,
                "is_active": e.is_active,
            }
            for e in recent
        ],
    }
