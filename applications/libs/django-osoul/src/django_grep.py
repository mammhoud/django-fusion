"""Deprecated compatibility shim for :mod:`django_osoul`.

``django_grep`` remains importable during the migration to ``django_osoul`` and
will be removed in a future release.
"""
from __future__ import annotations

import warnings

warnings.warn(
    "django_grep is deprecated; import from django_osoul instead. "
    "The compatibility package will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from django_osoul import *  # noqa: F401,F403
