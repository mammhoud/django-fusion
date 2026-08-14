"""
Formint — Django Ninja API entry point (server API layer).

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

from formint.components_api import ComponentsController
from formint.controllers import ALL_CONTROLLERS
from formint.sync_api import SyncController

api = NinjaExtraAPI(
    title="Formint POS API",
    version="1.0.0",
    description=(
        "Formint POS Professional — merged POS Full + POS Solo REST API. "
        "Django Ninja + ninja-extra with django-fusion encoder/decoder.\n\n"
        "## Authentication\n\n"
        "All `/api/v1/` endpoints require an API key passed in the "
        "`X-API-Key` header. Keys are scoped — a key with `products:read` "
        "can only GET product endpoints, while `*:*` grants full access.\n\n"
        "**Scoped API keys** are managed at `POST /api-keys/` — each key "
        "maps to resource:action scopes (e.g., `products:read`, `sales:*`). "
        "Keys can be revoked or rotated.\n\n"
        "**Example:** `curl -H 'X-API-Key: sk_abc123...' http://localhost:8767/api/v1/products/`"
    ),
    renderer=JSONRenderer(),
    urls_namespace="formint-api",
)

# ── OpenAPI security scheme: X-API-Key header ──
# NinjaExtraAPI supports adding security schemes via the OpenAPI extra config.
# We inject it into the generated schema so Swagger UI / ReDoc show the auth.
try:
    api._openapi_extra = {
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": (
                        "Scoped API key for the /api/v1/ contract. "
                        "Create keys via POST /api-keys/. "
                        "Scopes follow resource:action format (e.g., products:read, sales:*)."
                    ),
                },
            },
        },
        "security": [{"ApiKeyAuth": []}],
    }
except Exception:
    pass  # OpenAPI extra not supported in this ninja-extra version


@api_controller("", tags=["system"], auto_import=False)
class SystemController:
    """Health, schema and stats endpoints for the server API."""

    @http_get("/health/")
    def health(self, request: HttpRequest):
        from django.apps import apps

        cfg = apps.get_app_config("formint")
        return {
            "status": "ok",
            "product": "formint-pos",
            "service": "formint-server",
            "editions": ["pos-full", "pos-solo"],
            "phase": 2,
            "models": len(list(cfg.get_models())),
        }

    @http_get("/stats/")
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

    @http_get("/render-mode/")
    def render_mode(self, request: HttpRequest):
        """Report the active fusion render mode (mirrors landing-fusion /apis/render-mode/).

        ``X-Fusion-Render-First: true|false`` overrides the configured default
        for a single request.
        """
        from formint.fusion import render_mode_payload

        return render_mode_payload(request)

    @http_get("/navigation/")
    def navigation(self, request: HttpRequest):
        """Nav items from FormintModule (single source of truth for POS nav)."""
        from formint.fusion import navigation_payload

        return navigation_payload(request)

    @http_get("/assets/")
    def assets(self, request: HttpRequest):
        """FUSION_ASSETS manifest for frontend bundle parity."""
        from formint.fusion import assets_payload

        return assets_payload(request)


# Register every merged model controller (CRUD surface) + system + sync + components.
api.register_controllers(*ALL_CONTROLLERS, SystemController, SyncController, ComponentsController)
