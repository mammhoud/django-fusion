"""
Type definitions and utilities for django_fusion.

This module provides shared type aliases and utility decorators for type checking.

Classes:
    override: Decorator for marking methods as overrides (backported for Python < 3.12).

Type Aliases:
    TagBits: List of strings representing tag identifiers.

The override decorator allows marking methods as overrides to catch
mistakes when subclassing. It's backported from Python 3.12 for
compatibility with older versions.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 12):
    from typing import override as typing_override
else:
    from typing_extensions import override as typing_override

override = typing_override

TagBits = list[str]
