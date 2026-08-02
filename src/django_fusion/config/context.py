"""Context helpers for django-fusion.

Exposes ``SETTINGS(request)`` using the shared
``DjangoComponentsSettings`` instance from ``django_fusion.config.conf``.
"""
from __future__ import annotations

from django_fusion.config.conf import get_settings


def SETTINGS(request=None):  # noqa: N802
    """Return the shared DjangoComponentsSettings instance.

    ``request`` is accepted for API compatibility with callers that pass it,
    but it is not used by the current implementation.
    """
    return get_settings()
