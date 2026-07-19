"""
Canonical portal URL configuration using django-fusion viewsets.
Shared across all editions (vresume, solo, minimal, full).

Usage in each edition's urls.py:
    from shared.portal_urls import urlpatterns as portal_patterns
    path("", include(portal_patterns)),

@tested pos-portal/shared - Portal URLs shared by all editions
"""

from __future__ import annotations

from django.urls import path

from .portal_viewsets import PortalDashboard, PortalMenuItems, PortalMenuView

urlpatterns = [
    path("", PortalDashboard.as_view(), name="portal-dashboard"),
    path("menu/", PortalMenuItems.as_view(), name="portal-menu"),
    path("menu/<slug:slug>/", PortalMenuView.as_view(), name="portal-menu-detail"),
]
