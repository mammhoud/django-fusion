"""cms-full REST API — unified URL configuration.

All API endpoints are served under both /api/ and /apis/ prefixes.
Imports from the lms/cms API modules which contain the comprehensive
endpoint implementations.
"""
from django.urls import path

# Re-use the comprehensive API views from lms/cms
from www.api.data_adapter import bolt_view, fusion_response  # noqa
from www.api.fusion_health import fusion_health
from www.api.pages import page_data, page_detail, page_fragment

app_name = "api"

urlpatterns = [
    # ── Fusion Health ──
    path("fusion/health", fusion_health, name="fusion_health"),
    # ── Pages ──
    path("pages/<slug:slug>/", page_detail, name="page_detail"),
    path("pages/<slug:slug>/fragment/", page_fragment, name="page_fragment"),
    path("pages/<slug:slug>/data/", page_data, name="page_data"),
]
