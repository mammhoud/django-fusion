"""
POS Full — Django URL Configuration.

Provides Django admin panel URL routing for the master manager.
The admin index page is replaced by the custom Unfold dashboard
(via UNFOLD["DASHBOARD"] in configs/__init__.py).

The django-bolt API routes are registered for reverse URL resolution via
``django_bolt.urls``. They are actually served by the Rust-backed runbolt
server (``python -m django_bolt runbolt`` or ``manage.py runbolt``), not by
Django's URL resolver.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # django-bolt reverse-only URLs (so reverse()/{% url %} work)
    path("", include("django_bolt.urls")),
]
