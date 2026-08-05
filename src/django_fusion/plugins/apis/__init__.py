"""
APIs plugin for django-fusion
=============================

Auto-generates schemas from Django models and provides ``Application``-based
view classes that answer each request either as a render-first component
(server-rendered HTML) or as a codec-encoded JSON API response — the dual-mode
contract of django-fusion.

Core pieces:

* :func:`django_fusion.plugins.apis.schemas.generate_schema` — build a
  ``ModelSchema`` subclass from a Django model (fields auto-introspected,
  cached in :class:`~django_fusion.plugins.apis.schemas.SchemaRegistry`).
* :func:`django_fusion.plugins.apis.schemas.generate_schemas_for_app` —
  generate schemas for every model of a Django app config.
* :class:`django_fusion.plugins.apis.views.APISViewMixin` — render-first
  default option + per-view ``render_first_mapping`` + ``respond()`` that
  returns either a rendered component or a codec JSON payload.
* :class:`django_fusion.plugins.apis.views.APIApplication` — a ready-made
  ``Application`` subclass wired with the mixin.
* :mod:`django_fusion.plugins.apis.bolt` — django-bolt bridge: auto-generates
  msgspec structs from models and mounts ``Application`` viewsets as bolt
  routes that answer with the *same* dual-mode contract (component fragment
  HTML with data ↔ codec JSON API). Degrades gracefully when django-bolt is
  not installed.

Usage::

    from django_fusion.plugins.apis import APIApplication, generate_schema

    class ProductsAPI(APIApplication):
        title = "Products"
        fusion_render_first = True            # default option
        render_first_mapping = {"products/export/": False}  # per-view override

    ProductSchema = generate_schema(Product)

    # Optional django-bolt bridge (no-op when django-bolt is absent):
    from django_fusion.plugins.apis.bolt import build_bolt_api, mount_model_crud

    api = build_bolt_api(prefix="/bolt")
    if api is not None:
        mount_model_crud(api, Product)
"""

from __future__ import annotations

from django_fusion.plugins.apis.schemas import (
    SchemaRegistry,
    generate_schema,
    generate_schemas_for_app,
    get_schema,
)
from django_fusion.plugins.apis.views import APIApplication, APISViewMixin

from . import bolt  # noqa: F401 - expose the bolt bridge submodule

__all__ = [
    "SchemaRegistry",
    "generate_schema",
    "generate_schemas_for_app",
    "get_schema",
    "APIApplication",
    "APISViewMixin",
    "bolt",
]
