"""
Formint — Django Ninja API entry point (sidecar API layer).

Uses **ninja-extra** controllers for the CRUD surface and the
**django-fusion encoder** (``JSONRenderer``) for every response, so all
payloads follow the canonical fusion shape::

    {
        "status": 200,
        "message": "Success",
        "data": { ... }
    }

Schemas (decoder) come from ``django_fusion.routes.schemas.model_schema``
(ModelSchema) via ``formint.schemas``; rendering (encoder) comes from
``django_fusion.core.encoder.encoder.JSONRenderer``.

Exposed under ``/api/v1/`` (see ``formint/urls.py``).  Auto-discovers
controllers from ``formint.controllers``.
"""

from __future__ import annotations

from django.db.models import Count
from django.http import HttpRequest

from django_fusion.core.encoder.encoder import JSONRenderer
from ninja_extra import NinjaExtraAPI, api_controller, http_get

from formint.controllers import ALL_CONTROLLERS

api = NinjaExtraAPI(
    title="Formint POS API",
    version="1.0.0",
    description=(
        "Formint POS Professional — merged POS Full + POS Solo REST API. "
        "Django Ninja + ninja-extra with django-fusion encoder/decoder."
    ),
    renderer=JSONRenderer(),
    urls_namespace="formint-api",
)


@api_controller("", tags=["system"], auto_import=False)
class SystemController:
    """Health, schema and stats endpoints for the sidecar API."""

    @http_get("/health")
    def health(self, request: HttpRequest):
        from django.apps import apps

        cfg = apps.get_app_config("formint")
        return {
            "status": "ok",
            "product": "formint-pos",
            "service": "formint-sidecar",
            "editions": ["pos-full", "pos-solo"],
            "phase": 2,
            "models": len(list(cfg.get_models())),
        }

    @http_get("/stats")
    def stats(self, request: HttpRequest):
        """Quick KPI counts across the merged POS domain."""
        from django.db import connection

        from formint.models import (
            Category, ClientCategory, Customer, LoyaltyTransaction,
            Node, Product, Sale, UserSettings,
        )

        result = {
            "products": Product.objects.count(),
            "categories": Category.objects.count(),
            "customers": Customer.objects.count(),
            "sales": Sale.objects.count(),
            "nodes": Node.objects.count(),
            "client_categories": ClientCategory.objects.count(),
            "loyalty_transactions": LoyaltyTransaction.objects.count(),
            "user_settings": UserSettings.objects.count(),
        }
        total = Sale.objects.aggregate(total=Count("id"))
        result["sale_total_count"] = total["total"]
        return result

    @http_get("/render-mode")
    def render_mode(self, request: HttpRequest):
        """Report the active fusion render mode (mirrors landing-fusion /apis/render-mode/).

        ``X-Fusion-Render-First: true|false`` overrides the configured default
        for a single request.
        """
        from formint.fusion import render_mode_payload

        return render_mode_payload(request)

    @http_get("/navigation")
    def navigation(self, request: HttpRequest):
        """Nav items from FormintSite (single source of truth for POS nav)."""
        from formint.fusion import navigation_payload

        return navigation_payload(request)

    @http_get("/assets")
    def assets(self, request: HttpRequest):
        """FUSION_ASSETS manifest for frontend bundle parity."""
        from formint.fusion import assets_payload

        return assets_payload(request)


# Register every merged model controller (CRUD surface) + the system controller.
api.register_controllers(*ALL_CONTROLLERS, SystemController)
