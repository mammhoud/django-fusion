"""URL patterns for the canonical django-fusion asset manifest API."""

from django.urls import path

from .views import AssetsBottomView, AssetsManifestView, AssetsTopView

app_name = "fusion-assets"

urlpatterns = [
    path("top/", AssetsTopView.as_view(), name="assets-top"),
    path("bottom/", AssetsBottomView.as_view(), name="assets-bottom"),
    path("manifest/", AssetsManifestView.as_view(), name="assets-manifest"),
]
