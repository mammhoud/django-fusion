"""
Minimal node API URL configuration for Minimal POS Portal.
Node-only edition — heartbeat and registration endpoints.

@tested pos-portal/minimal - Node API URLs (minimal)
"""

from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("heartbeat/", views.node_heartbeat, name="node-heartbeat"),
    path("register/", views.node_register, name="node-register"),
]
