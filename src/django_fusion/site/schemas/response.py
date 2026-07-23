"""Backward-compatibility re-exports for django_fusion.site.schemas.response.

``django_fusion.ci.schemas.response`` is the canonical location for the
``APIResponse`` envelope. This module keeps the old ``site.schemas.response``
import path working.
"""
from __future__ import annotations

from django_fusion.ci.schemas.response import APIResponse

__all__ = ["APIResponse"]
