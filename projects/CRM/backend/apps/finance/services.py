"""Finance domain services shared by the Django and django-bolt API roads.

The revenue-trend aggregate lives here so the compatibility road
(``apps.finance.views``) and the canonical django-bolt road
(``apps.core.bolt_api``) return an identical payload from their own
road-appropriate ORM queries.
"""
from __future__ import annotations

import datetime
from decimal import Decimal

from django.db.models import Case, Count, Q, Sum, When
from django.db.models.fields import DecimalField
from django.utils import timezone

#: RevenueEvent kinds that carry POS (Formint) money rather than deal money.
POS_KINDS: tuple[str, ...] = ("pos_sale", "pos_refund")

_TWO = Decimal("0.01")
_DECIMAL_SUM = DecimalField(max_digits=15, decimal_places=2)


def trend_aggregates() -> dict:
    """Shared aggregation kwargs for the revenue-trend query.

    Both roads aggregate the trailing six months into ``total``/``events`` and
    also split each bucket into ``pos_total`` (Formint POS revenue) and
    ``deal_total`` (deal-linked revenue) so the RevOps card can show the mix
    without a second query. A refund is netted by the ingest service removing
    the ``pos_sale`` event, so refunded sales never inflate ``pos_total``.
    """
    return {
        "total": Sum("amount"),
        "events": Count("id"),
        "pos_total": Sum(
            Case(
                When(kind__in=POS_KINDS, then="amount"),
                default=Decimal("0.00"),
                output_field=_DECIMAL_SUM,
            )
        ),
        "deal_total": Sum(
            Case(
                When(~Q(kind__in=POS_KINDS), then="amount"),
                default=Decimal("0.00"),
                output_field=_DECIMAL_SUM,
            )
        ),
    }


def _money(value) -> str:
    """Quantize a Decimal (or Decimal-like) value to a two-place string."""
    if value is None:
        return "0.00"
    return Decimal(str(value)).quantize(_TWO).__str__()


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
                "total": (bucket["total"] if bucket else Decimal("0.00")).quantize(_TWO).__str__(),
                "events": bucket["events"] if bucket else 0,
                "pos_total": _money(bucket.get("pos_total")) if bucket else "0.00",
                "deal_total": _money(bucket.get("deal_total")) if bucket else "0.00",
            }
        )
    grand = sum((row["total"] for row in rows), Decimal("0.00"))
    pos_grand = sum((row.get("pos_total") or Decimal("0.00") for row in rows), Decimal("0.00"))
    deal_grand = sum((row.get("deal_total") or Decimal("0.00") for row in rows), Decimal("0.00"))
    return {
        "results": results,
        "count": len(results),
        "grand_total": grand.quantize(_TWO).__str__(),
        "pos_total": pos_grand.quantize(_TWO).__str__(),
        "deal_total": deal_grand.quantize(_TWO).__str__(),
    }
