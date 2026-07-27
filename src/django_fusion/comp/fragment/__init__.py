"""django_fusion.comp.fragment

Core component registry and data structures.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_fusion.comp.fragment._init import Component, components

# ``Component`` and ``components`` are available at ``TYPE_CHECKING`` time
# for static analysis only.  At runtime, import directly from ``_init``:
#
#     from django_fusion.comp.fragment._init import Component, components
#
# This avoids eagerly parsing ``_init.py`` (which depends on
# ``staticfiles.py``) when importing the ``fragment`` package, preventing
# circular import chains.
__all__: list[str] = []
