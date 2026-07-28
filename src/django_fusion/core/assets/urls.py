"""URL patterns for django-fusion assets endpoints."""

from django.urls import path

from .views import (
    AssetsBottomView,
    AssetsManifestView,
    AssetsTopView,
)

urlpatterns = [
    path("top/", AssetsTopView.as_view(), name="assets-top"),
    path("bottom/", AssetsBottomView.as_view(), name="assets-bottom"),
    path("manifest/", AssetsManifestView.as_view(), name="assets-manifest"),
]
