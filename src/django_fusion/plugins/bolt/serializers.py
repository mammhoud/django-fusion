"""
Fusion bolt serializers — auto-generate bolt-compatible schemas.

Converts ``RoutableComponent`` metadata into django-bolt serializer
classes for OpenAPI documentation and type-safe API responses.

Usage::

    from django_fusion.plugins.bolt import component_serializer

    Serializer = component_serializer(HomePageComponent)
    schema = Serializer.model_json_schema()
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("django_fusion.bolt")

# Try django-bolt serializers; fall back to plain dict
try:
    from django_bolt import Serializer as BoltSerializer

    _HAS_BOLT_SERIALIZER = True
except ImportError:
    BoltSerializer = None  # type: ignore[misc]
    _HAS_BOLT_SERIALIZER = False


def component_serializer(component_cls: type) -> type | None:
    """Generate a django-bolt ``Serializer`` from component metadata.

    Introspects the component's ``get_context_data()``, ``fragment_name``,
    ``route_path``, and ``fusion_render_first`` attributes and creates
    a serializer class that matches the bolt response contract.

    Returns ``None`` if django-bolt serializers are not available.
    """
    if not _HAS_BOLT_SERIALIZER or BoltSerializer is None:
        logger.debug("django_bolt.Serializer not available; serializer is None")
        return None

    title = (
        getattr(component_cls, "title", None)
        or getattr(component_cls, "page_title", None)
        or component_cls.__name__
    )
    fragment_name = getattr(component_cls, "fragment_name", None)
    if not fragment_name:
        route_name = getattr(component_cls, "route_name", None)
        fragment_name = f"components.{route_name}" if route_name else component_cls.__name__.lower()

    render_first = False
    if hasattr(component_cls, "get_fusion_render_first"):
        render_first = component_cls.get_fusion_render_first()

    # Build a dynamic Serializer subclass
    serializer_attrs = {
        "component": fragment_name,
        "fragment_name": fragment_name,
        "fragment_url": f"/fragments/{fragment_name}/",
        "fusion_render_first": render_first,
        "title": title,
        "route_path": getattr(component_cls, "route_path", ""),
        "route_name": getattr(component_cls, "route_name", ""),
        "meta": {
            "class_name": component_cls.__name__,
            "module": component_cls.__module__,
            "layout": getattr(component_cls, "layout", "default"),
            "icon": getattr(component_cls, "icon", "view_carousel"),
        },
    }

    serializer_name = f"{component_cls.__name__}Serializer"

    try:
        # Dynamically create a Bolt Serializer subclass
        SerializerClass: type = type(
            serializer_name,
            (BoltSerializer,),
            {
                "__annotations__": {
                    k: type(v) if not isinstance(v, dict) else dict
                    for k, v in serializer_attrs.items()
                },
                **serializer_attrs,
            },
        )
        return SerializerClass
    except Exception as exc:
        logger.warning(
            "Failed to create serializer for %s: %s",
            component_cls.__name__,
            exc,
        )
        return None
