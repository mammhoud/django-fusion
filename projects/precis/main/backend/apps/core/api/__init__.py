"""Fusion LMS REST API — URL configuration and shared endpoint wiring.

The health/branding views live in django-fusion (``django_fusion.contrib.api``);
the old bolt-pattern adapter modules (data_adapter, bolt_apis, pages, blog,
courses, products) were removed — use the app-specific ``apps.pages.*.api``
modules instead.
"""
