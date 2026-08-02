"""Canonical asset manifest API for django-fusion.

The implementation lives in :mod:`django_fusion.core.assets.views` so the
same configuration is shared by Django URL routes, template tags, and the
optional Bolt API integration.
"""

from .views import (
    AssetsBottomView,
    AssetsManifestView,
    AssetsTopView,
    _get_assets_config,
)

__all__ = [
    "AssetsBottomView",
    "AssetsManifestView",
    "AssetsTopView",
    "_get_assets_config",
]
