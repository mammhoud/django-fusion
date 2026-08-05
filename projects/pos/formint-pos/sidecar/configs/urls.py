"""
Formint — Django URL Configuration (merged sidecar).

Provides the Unfold-themed Django admin panel (master manager) plus the
merged formint app routes:

* ``/admin/``                 — Unfold admin (dashboard via UNFOLD settings)
* ``/health/``, ``/htmx/*``, ``/fusion/*`` — formint views (HTMX fragments,
  fusion render-mode contract)
* ``/api/v1/``                — Django Ninja + ninja-extra API (django-fusion
  encoder/decoder, auto-discovered controllers)

django-bolt is optional: when installed, its reverse-only URLs are included
so ``reverse()`` / ``{% url %}`` resolve, and the django-fusion ``apis``
plugin can mount Application viewsets as bolt routes.
"""

import importlib.util

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # ── Formint app (merged from backend/) ──
    path("", include("formint.urls")),
]

# django-bolt reverse-only URLs (so reverse()/{% url %} work).
# Only included when django_bolt is installed and ships a urls module.
if importlib.util.find_spec("django_bolt.urls"):
    urlpatterns.append(path("", include("django_bolt.urls")))
