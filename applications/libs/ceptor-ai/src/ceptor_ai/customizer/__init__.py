"""Compatibility shim — ``ceptor_ai.customizer`` is now ``ceptor_ai.ui``.

Import from the canonical path instead::

    from ceptor_ai.ui.bem import convert_to_bem
    from ceptor_ai.ui.watcher import BemWatcher
    from ceptor_ai.ui.viewsets import CSSViewSet
"""
from __future__ import annotations
import sys
import importlib

sys.modules.setdefault(__name__ + ".bem", importlib.import_module("ceptor_ai.ui.bem"))
sys.modules.setdefault(__name__ + ".watcher", importlib.import_module("ceptor_ai.ui.watcher"))
sys.modules.setdefault(__name__ + ".viewsets", importlib.import_module("ceptor_ai.ui.viewsets"))
