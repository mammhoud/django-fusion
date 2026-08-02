"""Site-level views and fragments for the Core app.

Submodules (``components``, ``blog``, ``tags``, ``asset_health``) are imported
directly by their consumers (e.g. ``apps.core.application`` imports
``apps.core.site.components``); this package marker intentionally exports
nothing to avoid stale shim imports.
"""
