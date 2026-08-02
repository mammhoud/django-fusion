"""
AssetTag
========
Enum of known asset tags used by the block component system.

Extracted from ``django_fusion.comp.templatetags.tags.asset`` to break a
circular import chain:

    staticfiles.py → asset.py → staticfiles.py  ✗  (was circular)

Now both ``staticfiles.py`` and ``asset.py`` import ``AssetTag`` from this
standalone module with no dependencies on other django-fusion internals.
"""

from __future__ import annotations

from enum import Enum


class AssetTag(Enum):
    CSS = "block:css"
    JS = "block:js"


__all__ = [
    "AssetTag",
]
