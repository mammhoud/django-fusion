"""Compatibility namespace — ``ceptor_ai.email`` redirects to ``ceptor_ai.communication.email``.

This shim registers the communication.email sub-modules under both the old
``ceptor_ai.email.*`` path and the canonical ``ceptor_ai.communication.email.*``
path — using the *same module objects* to avoid Django model registry conflicts.

Usage::

    from ceptor_ai.email.models.models import EmailLog   # legacy
    from ceptor_ai.communication.email.models.models import EmailLog  # canonical
"""
from __future__ import annotations
import importlib
import sys

_PREFIX = "ceptor_ai.communication.email"
_COMPAT = __name__  # ceptor_ai.email

def _alias(sub: str) -> None:
    canonical = f"{_PREFIX}.{sub}"
    compat = f"{_COMPAT}.{sub}"
    if compat in sys.modules:
        return
    try:
        mod = importlib.import_module(canonical)
        sys.modules[compat] = mod
    except ImportError:
        pass

for _sub in ("models", "services", "templates", "processing", "management", "apps"):
    _alias(_sub)
    _alias(f"{_sub}.models")
    _alias(f"{_sub}.services")
    _alias(f"{_sub}.template_selector")
