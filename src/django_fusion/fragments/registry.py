"""Registry for component-aware fragment requests.

``FragmentComponent`` subclasses register themselves automatically when
``fragment_name`` (or a derived name from ``route_name``) is provided.
Registered components can then be requested through the shared
``/fragments/<name>/`` endpoint, reusing SSE and HTMX transport support.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    # Avoid circular imports at module load time.
    from django_fusion.routes.fragments import FragmentComponent


# Mapping of dotted fragment identifiers to component classes.
_component_registry: dict[str, Type[FragmentComponent]] = {}


def register_fragment_component(name: str, component_class: Type[FragmentComponent]) -> None:
    """Register a component class under ``name``."""
    _component_registry[name] = component_class


def get_fragment_component(name: str) -> Type[FragmentComponent] | None:
    """Return the component class registered under ``name``, or ``None``."""
    return _component_registry.get(name)


def unregister_fragment_component(name: str) -> None:
    """Remove a component registration.  Useful for tests."""
    _component_registry.pop(name, None)


def clear_fragment_components() -> None:
    """Clear all component registrations.  Useful for tests."""
    _component_registry.clear()
