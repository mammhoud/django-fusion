"""Compatibility shim — ``ceptor_ai.http`` is now ``ceptor_ai.transport``.

Import from the canonical path instead::

    from ceptor_ai.transport.middlewares import PrivacyConsentMiddleware
    from ceptor_ai.transport.signals import binding
"""
from __future__ import annotations
import sys
import importlib

# Redirect sub-module lookups: ceptor_ai.http.X -> ceptor_ai.transport.X
_transport = importlib.import_module("ceptor_ai.transport")
sys.modules.setdefault(__name__ + ".middlewares", importlib.import_module("ceptor_ai.transport.middlewares"))
sys.modules.setdefault(__name__ + ".signals", importlib.import_module("ceptor_ai.transport.signals"))
sys.modules.setdefault(__name__ + ".handlers", importlib.import_module("ceptor_ai.transport.handlers"))
