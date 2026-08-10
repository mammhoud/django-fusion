"""SKELETON settings for the django-fusion skeleton rendering pipeline.

All features are **disabled by default**.  Each project must opt in
explicitly by setting ``FUSION_SKELETON`` in its Django settings module.

Example (recommended production values once enabled)::

    FUSION_SKELETON = {
        "ENABLED": True,
        "FIRST_PAINT_SKELETON": True,
        "HTMX_SKELETON": True,
        "ANIMATION_DURATION": "1.4s",
        "REDUCED_MOTION_MODE": "prefers",
        "ALLOWED_SKELETON_VARIANTS": [],
    }
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings


@dataclass(frozen=True, slots=True)
class SkeletonOptions:
    """Resolved configuration for the skeleton rendering pipeline."""

    enabled: bool = False
    first_paint_skeleton: bool = True
    htmx_skeleton: bool = True
    skeleton_css_path: str | None = None
    allowed_skeleton_variants: list[str] = field(default_factory=list)
    reduced_motion_mode: str = "prefers"  # "prefers" | "always" | "never"
    animation_duration: str = "1.4s"

    @classmethod
    def from_django_settings(cls) -> SkeletonOptions:
        """Resolve options from ``FUSION_SKELETON`` in Django settings."""
        raw = deepcopy(getattr(settings, "FUSION_SKELETON", None) or {})

        return cls(
            enabled=bool(raw.get("ENABLED", False)),
            first_paint_skeleton=bool(raw.get("FIRST_PAINT_SKELETON", True)),
            htmx_skeleton=bool(raw.get("HTMX_SKELETON", True)),
            skeleton_css_path=(
                str(raw["SKELETON_CSS_PATH"])
                if raw.get("SKELETON_CSS_PATH")
                else None
            ),
            allowed_skeleton_variants=list(
                raw.get("ALLOWED_SKELETON_VARIANTS", [])
            ),
            reduced_motion_mode=str(
                raw.get("REDUCED_MOTION_MODE", "prefers")
            ),
            animation_duration=str(
                raw.get("ANIMATION_DURATION", "1.4s")
            ),
        )


def get_skeleton_options() -> SkeletonOptions:
    """Return the current settings-derived skeleton options."""
    return SkeletonOptions.from_django_settings()
