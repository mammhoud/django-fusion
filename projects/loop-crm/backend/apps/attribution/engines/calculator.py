"""Multi-touch attribution calculator.

Rewrites each touchpoint's fractional weight for a deal using one of the
supported strategies. Weight assignments are normalized to sum to 1.0 so a
closed deal's value can be split back across the campaigns that influenced it.
"""
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from .models import AttributionTouchpoint


def _normalize(weights: list[float]) -> list[Decimal]:
    total = sum(weights) or 1.0
    return [Decimal(f"{w / total:.4f}") for w in weights]


class AttributionCalculator:
    """Static attribution strategies; each returns a weight per touchpoint."""

    @staticmethod
    def first_touch(touchpoints: list["AttributionTouchpoint"]) -> list[Decimal]:
        n = len(touchpoints)
        weights = [1.0 if i == 0 else 0.0 for i in range(n)]
        return _normalize(weights)

    @staticmethod
    def last_touch(touchpoints: list["AttributionTouchpoint"]) -> list[Decimal]:
        n = len(touchpoints)
        weights = [1.0 if i == n - 1 else 0.0 for i in range(n)]
        return _normalize(weights)

    @staticmethod
    def linear(touchpoints: list["AttributionTouchpoint"]) -> list[Decimal]:
        return _normalize([1.0 for _ in touchpoints])

    @staticmethod
    def time_decay(
        touchpoints: list["AttributionTouchpoint"], decay_rate: float = 0.5
    ) -> list[Decimal]:
        n = len(touchpoints)
        weights = [decay_rate ** (n - 1 - i) for i in range(n)]
        return _normalize(weights)

    @staticmethod
    def position_based(
        touchpoints: list["AttributionTouchpoint"],
        first_weight: float = 0.4,
        last_weight: float = 0.4,
        middle_weight: float = 0.2,
    ) -> list[Decimal]:
        n = len(touchpoints)
        if n == 1:
            return [Decimal("1.0")]
        weights: list[float] = [0.0] * n
        weights[0] = first_weight
        weights[-1] = last_weight
        middle_count = n - 2
        if middle_count > 0:
            each = middle_weight / middle_count
            for i in range(1, n - 1):
                weights[i] = each
        return _normalize(weights)

    STRATEGIES = {
        "first_touch": first_touch,
        "last_touch": last_touch,
        "linear": linear,
        "time_decay": time_decay,
        "position_based": position_based,
    }

    @classmethod
    def apply(cls, touchpoints: list["AttributionTouchpoint"], model_type: str) -> None:
        """Recompute and persist each touchpoint's weight for the given strategy."""
        strategy = cls.STRATEGIES.get(model_type, cls.linear)
        weights = strategy(touchpoints)
        for touchpoint, weight in zip(touchpoints, weights):
            touchpoint.weight = weight
            touchpoint.save(update_fields=["weight"])

    @classmethod
    def calculate_for_deal(cls, deal_id: int, model_type: str = "linear") -> None:
        """Convenience wrapper: attribute one deal's touchpoints end-to-end."""
        from apps.attribution.models import AttributionTouchpoint

        touchpoints = list(AttributionTouchpoint.objects.filter(deal_id=deal_id).order_by("occurred_at"))
        cls.apply(touchpoints, model_type)
