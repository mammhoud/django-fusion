"""
POS Solo — django-fusion FragmentComponent classes.

Mirrors ``pos-full/sidecar/fragments/`` but adapted for the solo's
single-restaurant database and standalone operation.

Each module exports one or more ``FragmentComponent`` subclasses with a
``fragment_name`` and ``get_context()`` method that fetches model data.

Registration::

    from fragments import register_fragments
    register_fragments()
"""

from __future__ import annotations

import logging
from typing import Any

from django_fusion.routes import FragmentComponent  # noqa: F401 — re-export base

logger = logging.getLogger("pos.fragments")

_FRAGMENTS: list[type[FragmentComponent]] = []


def register(fragment_cls: type[FragmentComponent]) -> type[FragmentComponent]:
    """Decorator that registers a FragmentComponent subclass."""
    _FRAGMENTS.append(fragment_cls)
    return fragment_cls


def register_fragments() -> None:
    """Register all collected fragments with the django-fusion component system.

    Wrapped in try/except so that a missing component system does not
    prevent the server from starting.
    """
    try:
        from django_fusion.comp.loaders import register_component

        for cls in _FRAGMENTS:
            name = getattr(cls, "fragment_name", None)
            if name:
                register_component(name, cls)
                logger.debug("Registered fragment: %s → %s", name, cls.__name__)

        logger.info("Registered %d POS Solo fragments", len(_FRAGMENTS))
    except Exception as exc:
        logger.warning("Fragment registration skipped: %s", exc)


def get_context(fragment_name: str, **kwargs: Any) -> dict[str, Any]:
    """Instantiate a fragment by name and return its context."""
    for cls in _FRAGMENTS:
        if getattr(cls, "fragment_name", None) == fragment_name:
            return cls().get_context(**kwargs)
    raise ValueError(f"Unknown fragment: {fragment_name!r}")


def get_all_fragments() -> list[type[FragmentComponent]]:
    """Return the list of all registered fragment classes."""
    from . import (  # noqa: F401 — side-effect: @register decorators
        dashboard,
        suppliers,
        about,
        customers,
        inventory,
        employees,
        products,
    )
    return _FRAGMENTS


__all__ = [
    "FragmentComponent",
    "register",
    "register_fragments",
    "get_context",
    "get_all_fragments",
]
