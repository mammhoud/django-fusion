"""
FusionBoltDualModeMixin — bridges django-bolt with FusionDualModeMixin.

When ``django_bolt`` is installed, this mixin overrides the component's
data-mode rendering so that bolt API endpoints serve the actual
``get_fragment_data()`` payload (codec-encoded) instead of a bare
fragment pointer.  The mixin works with any ``RoutableComponent`` or
``FragmentComponent`` that already uses ``FusionDualModeMixin``::

    from django_fusion.plugins.bolt import FusionBoltDualModeMixin
    from django_fusion.routes.components.fragments import FragmentComponent

    class CourseGridFragment(FusionBoltDualModeMixin, FragmentComponent):
        route_name = "course-grid"
        route_path = "courses/grid/"
        fragment_name = "htmx.course_grid"

        def get_fragment_data(self):
            return {"courses": [...]}

The mixin is a no-op when ``django_bolt`` is not installed — it simply
inherits ``FusionDualModeMixin`` behaviour unchanged.

Design
------
``FusionBoltAPI.register_component()`` already registers bolt endpoints
for every ``RoutableComponent`` subclass.  The gap is that in data mode
(``fusion_render_first=False``) it returns a *fragment pointer* (metadata
only) rather than the actual data payload from ``get_fragment_data()``.

This mixin provides a ``get_bolt_data_payload()`` method that the bolt
endpoint (or any consumer) can call to get the full dual-mode response
without the Django template pipeline.  When bolt is installed, the mixin
also annotates the component class so ``FusionBoltAPI.register_component()``
can detect it and use the richer response shape.
"""

from __future__ import annotations

import logging
from typing import Any

from django_fusion.routes.components.dual_mode import FusionDualModeMixin

logger = logging.getLogger(__name__)

try:
    import django_bolt  # noqa: F401
    _HAS_BOLT = True
except ImportError:
    _HAS_BOLT = False


class FusionBoltDualModeMixin(FusionDualModeMixin):
    """Dual-mode mixin that exposes data payloads for django-bolt endpoints.

    When ``django_bolt`` is installed, this mixin:

    * Adds a ``_fusion_bolt_aware = True`` class attribute that
      ``FusionBoltAPI.register_component()`` detects so it can serve the
      full ``get_fragment_data()`` payload in data mode instead of a
      bare fragment pointer.
    * Provides ``get_bolt_data_payload()`` — a convenience that returns
      the same ``{encoded, meta}`` dict that ``render_data_response()``
      would produce, but as a plain dict (no ``HttpResponse`` wrapper).
      Callers include bolt endpoint handlers, CLI tools, or WebSocket
      consumers that need the data without the HTTP layer.

    When ``django_bolt`` is not installed, the mixin behaves exactly as
    ``FusionDualModeMixin`` — no bolt-specific attributes or methods are
    added.
    """

    if _HAS_BOLT:
        #: Marker for ``FusionBoltAPI.register_component()`` to detect that
        #: this component supports the full dual-mode data payload.
        _fusion_bolt_aware: bool = True

    # ------------------------------------------------------------------
    # Bolt-aware data payload
    # ------------------------------------------------------------------

    def get_bolt_data_payload(
        self,
        request: Any = None,
        *,
        encode: bool = True,
    ) -> dict[str, Any]:
        """Return the dual-mode data payload as a plain dict.

        When ``encode=True`` (default), ``get_fragment_data()`` is wrapped
        through ``FusionCodec`` so the payload includes the ``encoded``
        string.  When ``encode=False``, the raw ``get_fragment_data()``
        dict is returned directly (useful when the caller handles encoding
        or when the data is consumed by a non-HTTP transport).

        The returned shape (when ``encode=True``) mirrors
        ``render_data_response()``::

            {
                "encoded": "fusion_v1:<base64>",
                "meta": {
                    "component": "...",
                    "fragment_name": "...",
                    "fusion_render_first": True | False,
                    "language": "en",
                    "site": { ... }  # optional, from get_data_meta()
                }
            }

        When ``encode=False`` the payload is the raw ``get_fragment_data()``
        dict with ``meta`` merged in.
        """
        request = request or getattr(self, "request", None)
        payload = self.get_fragment_data()
        meta = self.get_data_meta()

        if not encode:
            payload["meta"] = meta
            return payload

        from django_fusion.routes.rendering.session import FusionCodec

        encoded = FusionCodec.encode(payload)
        return {
            "encoded": encoded,
            "meta": meta,
        }


# Re-export the bolt flag constant for use in ``FusionBoltAPI``.
FUSION_BOLT_AWARE_ATTR = "_fusion_bolt_aware"


__all__ = [
    "FusionBoltDualModeMixin",
    "FUSION_BOLT_AWARE_ATTR",
]