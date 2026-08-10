"""FUSION_ANALYZER settings for the template/component skeleton analyzer.

All features are **disabled by default**. Each project must opt in explicitly
by setting ``FUSION_ANALYZER`` in its Django settings module.

Example (recommended production values once enabled)::

    FUSION_ANALYZER = {
        "ENABLED": True,
        "SKELETON_AUTO_DETECT": True,
        "SKELETON_DEFAULT_VARIANT": "line",
        "EMIT_SKELETON_MANIFEST": True,
        "CACHE_DURATION": 3600,
    }
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings


@dataclass(frozen=True, slots=True)
class AnalyzerOptions:
    """Resolved configuration for the component analyzer / skeleton pipeline."""

    enabled: bool = False
    skeleton_auto_detect: bool = True
    skeleton_default_variant: str = "line"
    emit_skeleton_manifest: bool = True
    cache_duration: int = 3600
    analyze_depth: int = 3
    analyze_filters: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_django_settings(cls) -> AnalyzerOptions:
        """Resolve options from ``FUSION_ANALYZER`` in Django settings."""
        raw = deepcopy(getattr(settings, "FUSION_ANALYZER", None) or {})

        return cls(
            enabled=bool(raw.get("ENABLED", False)),
            skeleton_auto_detect=bool(raw.get("SKELETON_AUTO_DETECT", True)),
            skeleton_default_variant=str(
                raw.get("SKELETON_DEFAULT_VARIANT", "line")
            ),
            emit_skeleton_manifest=bool(raw.get("EMIT_SKELETON_MANIFEST", True)),
            cache_duration=int(raw.get("CACHE_DURATION", 3600)),
            analyze_depth=int(raw.get("ANALYZE_DEPTH", 3)),
            analyze_filters=deepcopy(raw.get("ANALYZE_FILTERS", {}) or {}),
        )


def get_analyzer_options() -> AnalyzerOptions:
    """Return the current settings-derived analyzer options."""
    return AnalyzerOptions.from_django_settings()
