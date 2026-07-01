"""Route builder helpers — convenience wrappers for Django URL patterns.

These are top-level compat re-exports from ``django_osoul.site.routes``.
Prefer importing from the canonical path::

    from django_osoul.site.routes import ModelRoutes, FragmentRoutes

Modules at this level provide the legacy import path::

    from django_osoul.routes import ModelRoutes   # still works
"""
from __future__ import annotations
import sys
import importlib as _importlib

_site_routes = _importlib.import_module("django_osoul.site.routes")
sys.modules.setdefault(__name__ + ".base", _importlib.import_module("django_osoul.site.routes.base"))
sys.modules.setdefault(__name__ + ".model", _importlib.import_module("django_osoul.site.routes.model"))
sys.modules.setdefault(__name__ + ".fragments", _importlib.import_module("django_osoul.site.routes.fragments"))
