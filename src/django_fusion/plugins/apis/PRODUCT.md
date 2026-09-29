---
id: plugin.apis
title: Typed API Helpers
summary: Typed API helpers — schema registry, model-to-schema mapping, OpenAPI output, and an optional Bolt (Rust-backed) route bridge.
capabilities: [api, bolt, schemas, serialization]
signals: [api-request, fragment-request]
requires: []
provides: [api, schemas]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/apis/schemas.py
    what: The schema registry and the model-to-schema mapping.
  - path: libs/django-fusion/src/django_fusion/plugins/apis/views.py
    what: The API view mixin and its render-first/data-mode response contract.
  - path: libs/django-fusion/src/django_fusion/plugins/apis/viewsets.py
    what: Viewset integration that exposes the same resource on both roads.
  - path: libs/django-fusion/src/django_fusion/plugins/apis/openapi.py
    what: OpenAPI document generation from the registered schemas.
  - path: libs/django-fusion/src/django_fusion/plugins/apis/bolt.py
    what: The django-bolt bridge (optional dependency) that mounts viewsets as Rust-backed routes.
limits:
  - "The Bolt road needs `django-bolt`, which the library declares only for Python 3.12+, and it must be installed separately (`django-fusion[bolt]`). Without it only the Django road exists."
  - "Does not generate client SDKs."
  - "Does not own authentication: `auth.py` provides the integrations, but the site's auth configuration decides who may call what."
  - "Does not version APIs — versioning is a routing decision per site."
---

# Typed API Helpers

## What it does

- Keeps one schema registry per project, so a resource's shape is declared once
  and reused by validation, serialization, and documentation.
- Maps Django models onto schemas, including the field-coercion cases the
  products actually needed.
- Serves the **same** resource on two roads: an HTML fragment (render-first) or a
  JSON payload (data mode), chosen by the request.
- Emits an OpenAPI document from the registered schemas.
- Optionally bridges viewsets to django-bolt's Rust-backed routes.

## What it does not do

- It does not implement the API layer for the whole framework: the routes
  contract (`django_fusion.routes`) still owns routing.
- It does not generate client code (SDKs, typed fetch wrappers) from the schemas.
- It is not a substitute for the product's own authorization rules.
