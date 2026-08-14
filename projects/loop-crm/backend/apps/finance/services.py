"""Finance domain services shared by the Django and django-bolt API roads.

The revenue-trend aggregate lives here so the compatibility road
(``apps.finance.views``) and the canonical django-bolt road
(``apps.core.bolt_api``) return an identical payload from their own
road-appropriate ORM queries.
"""
from __future__ import annotations

import datetime
from decimal import Decimal

from django.utils import timezone


def month_first(date: datetime.date, months_ago: int) -> datetime.date:
    """Return the first day of the month *months_ago* months before *date*."""
    year, month = date.year, date.month
    for _ in range(months_ago):
        month -= 1
        if month == 0:
            year -= 1
            month = 12
    return datetime.date(year, month, 1)


def revenue_trend_results(rows: list[dict], today: datetime.date | None = None) -> dict:
    """Shape ``TruncMonth``-aggregated revenue rows into the trend payload.

    *rows* are dicts with ``month`` (date), ``total`` (Decimal), and
    ``events`` (int). The payload zero-fills the trailing six months so the
    chart shows a real window instead of a sparse list, and rolls up a
    ``grand_total`` across the returned buckets.
    """
    two = Decimal("0.01")
    by_month = {row["month"]: row for row in rows}
    today = today or timezone.localdate()
    results = []
    for months_ago in range(5, -1, -1):
        first = month_first(today, months_ago)
        bucket = by_month.get(first)
        results.append(
            {
                "month": first.strftime("%Y-%m"),
                "label": first.strftime("%b %Y"),
                "total": (bucket["total"] if bucket else Decimal("0.00")).quantize(two).__str__(),
                "events": bucket["events"] if bucket else 0,
            }
        )
    grand = sum((row["total"] for row in rows), Decimal("0.00"))
    return {
        "results": results,
        "count": len(results),
        "grand_total": grand.quantize(two).__str__(),
    }
