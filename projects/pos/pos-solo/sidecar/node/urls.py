"""
Node API URL configuration for Solo POS Portal.
Provides endpoints for node registration, heartbeat, and data sync.

@tested pos-portal/solo - Node API URLs
"""

from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("heartbeat/", views.node_heartbeat, name="node-heartbeat"),
    path("register/", views.node_register, name="node-register"),
    path("transactions/", views.node_transactions, name="node-transactions"),
    path("products/", views.node_products, name="node-products"),
]
