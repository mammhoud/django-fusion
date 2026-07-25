"""
POS Full — django-fusion FragmentComponent classes.

Each module exports one or more ``FragmentComponent`` subclasses with a
``fragment_name`` and ``get_context()`` method that fetches model data and
returns a context dictionary for template rendering.

Usage in route handlers::

    from fragments.dashboard import DashboardFragment

    fragment = DashboardFragment()
    context = fragment.get_context()
    # → {"product_count": 42, "customer_count": 17, ...}

Registration::

    from fragments import register_fragments
    register_fragments()

This registers all fragment names so they are discoverable by the
django-fusion component system (``{% comp \"fragment_name\" %}``).
"""

from __future__ import annotations

import logging
from typing import Any

from django_fusion.routes import FragmentComponent  # noqa: F401 — re-export base

logger = logging.getLogger("pos.fragments")

# ── Module-level registry ──────────────────────────────────────────
# All Fragments are collected here so ``register_fragments()`` can
# publish them to the django-fusion component system.
_FRAGMENTS: list[type[FragmentComponent]] = []


def register(fragment_cls: type[FragmentComponent]) -> type[FragmentComponent]:
    """Decorator that registers a FragmentComponent subclass.

    Usage::

        @register
        class MyFragment(FragmentComponent):
            fragment_name = "pos.my_fragment"
    """
    _FRAGMENTS.append(fragment_cls)
    return fragment_cls


def register_fragments() -> None:
    """Register all collected fragments with the django-fusion component system.

    The component system is optional — fragments still work standalone
    via get_context(). This function logs the available fragment names
    for debugging purposes.
    """
    logger.info("POS fragments available: %d", len(_FRAGMENTS))
    for cls in _FRAGMENTS:
        logger.debug("Fragment: %s → %s", getattr(cls, "fragment_name", "?"), cls.__name__)


def get_context(fragment_name: str, **kwargs: Any) -> dict[str, Any]:
    """Instantiate a fragment by name and return its context.

    Raises ``ValueError`` if *fragment_name* is not registered.
    """
    for cls in _FRAGMENTS:
        if getattr(cls, "fragment_name", None) == fragment_name:
            return cls().get_context(**kwargs)
    raise ValueError(f"Unknown fragment: {fragment_name!r}")


# ── Lazy imports so models are loaded after Django setup ──────────


def get_all_fragments() -> list[type[FragmentComponent]]:
    """Return the list of all registered fragment classes.

    Calling this triggers the lazy import of each fragment module so
    the ``@register`` decorators execute.
    """
    # Touch each module to populate _FRAGMENTS (relative imports)
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
