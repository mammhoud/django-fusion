from django.urls import path, re_path

from .skeleton_view import SkeletonManifestView
from .views import AnalyzeView


urlpatterns = [
    path("analyze/", AnalyzeView.as_view(), name="analyzer_analyze"),
    # Both trailing-slash and no-trailing-slash variants accept template
    # paths like "pages/home.html" or "pages/home.html/".
    re_path(
        r"^skeleton/(?P<page_path>.+)/?$",
        SkeletonManifestView.as_view(),
        name="analyzer_skeleton_manifest",
    ),
]
