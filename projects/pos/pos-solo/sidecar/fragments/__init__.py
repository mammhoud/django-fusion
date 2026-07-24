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

from django_fusion.comp.routes import FragmentComponent  # noqa: F401 — re-export base

logger = logging.getLogger("pos.fragments")

_FRAGMENTS: list[type[FragmentComponent]] = []


def register(fragment_cls: type[FragmentComponent]) -> type[FragmentComponent]:
    """Decorator that registers a FragmentComponent subclass."""
    _FRAGMENTS.append(fragment_cls)
    return fragment_cls


def register_fragments() -> None:
    """Register all collected fragments with the django-fusion component system.

    The component system is optional — fragments still work standalone
    via get_context(). This function logs the available fragment names
    for debugging purposes.
    """
    logger.info("POS Solo fragments available: %d", len(_FRAGMENTS))
    for cls in _FRAGMENTS:
        logger.debug("Fragment: %s → %s", getattr(cls, "fragment_name", "?"), cls.__name__)


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
