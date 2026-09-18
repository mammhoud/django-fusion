"""Precis auth — django-allauth headless API adapters.

The headless API (/api/auth/browser/v1/auth/*) is the primary auth path
consumed by the Alpine login modal on both render roads (Astro frontend and
Django templates). Server-rendered /accounts/* pages fall back to allauth's
built-in pages with the existing HTMX fragment adapter.

The account adapter extends the existing HTMX-aware RegistrationAdapter so
headless (JSON) and server-rendered (fragment) flows share one behaviour.
"""
