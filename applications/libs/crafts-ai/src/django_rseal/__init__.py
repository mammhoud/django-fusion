"""Deprecated compatibility namespace for the merged ``django-rseal`` package.

``django-rseal`` has been merged into ``crafts-ai``. New code must import from
``crafts_ai.rseal`` or another ``crafts_ai`` namespace directly; this package is
kept temporarily for legacy top-level import probes during the migration.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "django_rseal is deprecated; import crafts_ai.rseal instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
