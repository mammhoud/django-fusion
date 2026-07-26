"""CMS Fusion REST API — URL configuration."""

from django.urls import path

from . import fusion_health, pages

app_name = "api"

urlpatterns = [
    path("fusion/health", fusion_health.fusion_health, name="fusion_health"),
    path("pages/", pages.page_list, name="page_list"),
    path("pages/<slug:slug>/", pages.page_detail, name="page_detail"),
    path("pages/<slug:slug>/fragment/", pages.page_fragment, name="page_fragment"),
    path("pages/<slug:slug>/data/", pages.page_data, name="page_data"),
]
