"""Deprecated compatibility shim for :mod:`django_fusion`.

``django_grep`` remains importable during the migration to ``django_fusion`` and
will be removed in a future release.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "django_grep is deprecated; import from django_fusion instead. "
    "The compatibility package will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from django_fusion import *  # noqa: F401,F403
