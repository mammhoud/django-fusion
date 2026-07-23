"""Request context processors and context data builders.

Modules
-------
context.auth        Injects authentication state and user role into template context.
context.cookies     Reads and normalises cookie consent state.
context.htmx        Provides HTMX request metadata (hx-target, hx-trigger, etc.).
context.languages   Builds language switcher data for i18n-enabled sites.
context.settings    Exposes selected Django settings as template variables.

Usage::

    # In TEMPLATES context_processors:
    "django_fusion.site.context.auth.auth_context",
    "django_fusion.site.context.htmx.htmx_context",
    "django_fusion.site.context.languages.language_context",
"""
