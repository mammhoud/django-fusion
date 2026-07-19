"""
Canonical portal URL configuration using django-fusion viewsets.
Shared across all editions (solo, minimal, full).

Used in each edition's urls.py via:
    path("", include("shared.portal_urls")),

@tested pos/shared - Portal URLs shared by all editions
"""

from __future__ import annotations

from django.urls import path

from .portal_viewsets import PortalDashboard, PortalMenuItems, PortalMenuView

urlpatterns = [
    path("", PortalDashboard.as_view(), name="portal-dashboard"),
    path("menu/", PortalMenuItems.as_view(), name="portal-menu"),
    path("menu/<slug:slug>/", PortalMenuView.as_view(), name="portal-menu-detail"),
]
