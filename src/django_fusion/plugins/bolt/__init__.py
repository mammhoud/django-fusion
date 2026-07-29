"""
django_fusion.bolt — High-performance django-bolt API integration.

Provides a ``FusionBoltAPI`` class that auto-registers fusion components as
bolt endpoints, plus decorators, serializers, and auth bridges.

Graceful fallback: if ``django_bolt`` is not installed, all classes are
replaced with no-op stubs that log a warning and return empty results.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("django_fusion.bolt")

try:
    import django_bolt  # noqa: F401
    _HAS_BOLT = True
except ImportError:
    _HAS_BOLT = False
    logger.warning(
        "django_bolt is not installed. "
        "django_fusion.bolt features are disabled. "
        "Install django-bolt for high-performance API support."
    )


if _HAS_BOLT:
    from django_fusion.plugins.bolt.api import FusionBoltAPI, register_fusion_assets_bolt
    from django_fusion.plugins.bolt.decorators import fusion_endpoint
    from django_fusion.plugins.bolt.serializers import component_serializer
    from django_fusion.plugins.bolt.auth import FusionBoltAuthBackend

    __all__ = [
        "FusionBoltAPI",
        "register_fusion_assets_bolt",
        "fusion_endpoint",
        "component_serializer",
        "FusionBoltAuthBackend",
    ]
else:
    # No-op stubs
    class _NoopBoltAPI:  # pragma: no cover
        """Placeholder when django_bolt is not installed."""

        def __init__(self, *args, **kwargs):
            logger.warning(
                "FusionBoltAPI is a no-op (django_bolt not installed). "
                "Install django-bolt for high-performance API support."
            )

        def register_component(self, *args, **kwargs):
            logger.debug("FusionBoltAPI.register_component is a no-op")
            return None

        def autodiscover(self, *args, **kwargs):
            logger.debug("FusionBoltAPI.autodiscover is a no-op")
            return 0

    FusionBoltAPI = _NoopBoltAPI  # type: ignore[misc]

    def fusion_endpoint(*args, **kwargs):  # type: ignore[misc]
        """No-op decorator when django_bolt is not installed."""
        return lambda f: f

    def component_serializer(*args, **kwargs):  # type: ignore[misc]
        """No-op when django_bolt is not installed."""
        return None

    class FusionBoltAuthBackend:  # type: ignore[no-redef]
        """No-op auth backend when django_bolt is not installed."""

        def __init__(self, *args, **kwargs):
            pass

        def authenticate(self, request):
            return None

    __all__ = [
        "FusionBoltAPI",
        "fusion_endpoint",
        "component_serializer",
        "FusionBoltAuthBackend",
    ]
