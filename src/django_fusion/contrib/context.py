"""Context helpers for django-fusion.

Exposes ``SETTINGS(request)`` used by the canonical ``django_fusion.site.interface``
implementation.  The implementation reuses the single
``DjangoComponentsSettings`` instance already created in the component
configuration module.
"""
from __future__ import annotations

from django_fusion.comp.configuration.conf import get_settings


def SETTINGS(request=None):  # noqa: N802
    """Return the shared DjangoComponentsSettings instance.

    ``request`` is accepted for API compatibility with callers that pass it,
    but it is not used by the current implementation.
    """
    return get_settings()
