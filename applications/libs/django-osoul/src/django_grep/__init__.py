"""Deprecated compatibility namespace for the merged ``django-grep`` package.

``django-grep`` has been merged into ``django-osoul``. New code must import
from ``django_osoul`` directly; this module remains only as a temporary marker
for environments that still probe the legacy top-level package.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "django_grep is deprecated; import django_osoul instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
