"""URL patterns for the canonical django-fusion asset manifest API."""

from django.urls import path

from .views import (
    AssetsBottomView,
    AssetsManifestView,
    AssetsTopView,
    ComponentAssetDetailView,
    ComponentAssetsView,
    PageAssetsView,
)

app_name = "fusion-assets"

urlpatterns = [
    path("top/", AssetsTopView.as_view(), name="assets-top"),
    path("bottom/", AssetsBottomView.as_view(), name="assets-bottom"),
    path("manifest/", AssetsManifestView.as_view(), name="assets-manifest"),
    # Phase 3 — per-component asset endpoints
    path("components/", ComponentAssetsView.as_view(), name="component-assets"),
    path(
        "components/<path:component_name>/",
        ComponentAssetDetailView.as_view(),
        name="component-asset-detail",
    ),
    path(
        "page/<path:page_path>/",
        PageAssetsView.as_view(),
        name="page-assets",
    ),
]
