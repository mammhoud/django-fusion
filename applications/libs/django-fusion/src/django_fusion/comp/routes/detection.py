# All Rights Reserved.

"""
Fragment detection for HTMX requests in django-fusion.

This module provides utilities for detecting HTMX requests and determining
the appropriate rendering strategy (full, fragment, or out-of-band).

Classes:
    FragmentDetector: Detects HTMX fragment requests and determines rendering strategy.
    FragmentDetectionMixin: Mixin that annotates request with HTMX detection.

Functions:
    detect_fragment_strategy: Convenience function for fragment detection.
    add_fragment_detection_to_request: Annotate request with HTMX detection attributes.

The module delegates to the canonical helper `django_fusion.site._context_mixins.is_htmx_request`
for HTMX request detection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from django.http import HttpRequest

from django_fusion.site._context_mixins import is_htmx_request as _is_htmx

RenderStrategy = Literal["full", "fragment", "oob"]


class FragmentDetector:
    """Detects HTMX fragment requests and determines rendering strategy."""

    def detect(self, request: HttpRequest) -> RenderStrategy:
        """Return ``"full"``, ``"fragment"``, or ``"oob"``."""
        if not self.is_htmx_request(request):
            return "full"
        if self.has_oob_swap(request):
            return "oob"
        return "fragment"

    # Single canonical check — delegates to module-level helper
    def is_htmx_request(self, request: HttpRequest) -> bool:
        """Return True when the request carries ``HX-Request: true``."""
        return _is_htmx(request)

    def has_oob_swap(self, request: HttpRequest) -> bool:
        return "HX-Swap-OOB" in request.headers

    def get_target_id(self, request: HttpRequest) -> str | None:
        return request.headers.get("HX-Target")

    def get_trigger_id(self, request: HttpRequest) -> str | None:
        return request.headers.get("HX-Trigger")

    def get_current_url(self, request: HttpRequest) -> str | None:
        return request.headers.get("HX-Current-URL")

    def is_boosted(self, request: HttpRequest) -> bool:
        return request.headers.get("HX-Boosted") == "true"

    def is_history_restore(self, request: HttpRequest) -> bool:
        return request.headers.get("HX-History-Restore-Request") == "true"


def detect_fragment_strategy(request: HttpRequest) -> RenderStrategy:
    """Convenience function — delegates to ``FragmentDetector.detect()``."""
    return FragmentDetector().detect(request)


def add_fragment_detection_to_request(request: HttpRequest) -> None:
    """Annotate *request* with HTMX detection attributes."""
    detector = FragmentDetector()
    request.strategy = detector.detect(request)           # type: ignore[attr-defined]
    request.is_htmx = detector.is_htmx_request(request)  # type: ignore[attr-defined]
    request.htmx_target = detector.get_target_id(request)         # type: ignore[attr-defined]
    request.htmx_trigger = detector.get_trigger_id(request)       # type: ignore[attr-defined]
    request.htmx_current_url = detector.get_current_url(request)  # type: ignore[attr-defined]
    request.is_htmx_boosted = detector.is_boosted(request)        # type: ignore[attr-defined]
    request.is_htmx_history_restore = detector.is_history_restore(request)  # type: ignore[attr-defined]


class FragmentDetectionMixin:
    """Mixin that annotates the request with HTMX detection in ``setup()``."""

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:  # noqa: F821
        super().setup(request, *args, **kwargs)  # type: ignore[misc]
        add_fragment_detection_to_request(request)
