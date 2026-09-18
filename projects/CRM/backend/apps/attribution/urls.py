from django.urls import path

from apps.core.api import resource_api

urlpatterns = [
    path("touchpoints/", resource_api, {"resource": "touchpoints"}, name="touchpoints_api"),
    path("reports/", resource_api, {"resource": "touchpoints"}, name="reports_api"),
]
