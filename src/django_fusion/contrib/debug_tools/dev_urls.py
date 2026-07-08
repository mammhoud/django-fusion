"""
Development URL helpers for Django projects.

``configure_dev_urls(urlpatterns, settings)`` adds:
  - Debug error pages (400/401/403/404/429/500/502/503/504)
  - Static and media file serving
  - Debug toolbar / Silk / Livereload URLs (via configure_urls)

Usage in urls.py::

    if settings.DEBUG:
        from django_fusion.contrib.debug_tools.dev_urls import configure_dev_urls
        urlpatterns = configure_dev_urls(urlpatterns, settings)
"""

from django.conf import settings as django_settings
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from .urls import configure_urls


def configure_dev_urls(urlpatterns: list, settings=None) -> list:
    """
    Extend *urlpatterns* with all development-only URL patterns.

    Adds debug error pages, static/media serving, and debug tool URLs
    (debug_toolbar, Silk, Livereload).

    Args:
        urlpatterns: The existing URL patterns list.
        settings: The Django settings module (defaults to django.conf.settings).

    Returns:
        Updated urlpatterns list.
    """
    if settings is None:
        settings = django_settings

    updated = list(urlpatterns)

    # ----------------------------------------------------------------
    # Debug error pages
    # ----------------------------------------------------------------
    updated += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
            name="error-400",
        ),
        path("401/", TemplateView.as_view(template_name="errors/401.html"), name="error-401"),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied!")},
            name="error-403",
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found!")},
            name="error-404",
        ),
        path("429/", TemplateView.as_view(template_name="errors/429.html"), name="error-429"),
        path("500/", default_views.server_error, name="error-500"),
        path("502/", TemplateView.as_view(template_name="errors/502.html"), name="error-502"),
        path("503/", TemplateView.as_view(template_name="errors/503.html"), name="error-503"),
        path("504/", TemplateView.as_view(template_name="errors/504.html"), name="error-504"),
    ]

    # ----------------------------------------------------------------
    # Static and media file serving
    # ----------------------------------------------------------------
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    updated += staticfiles_urlpatterns()
    updated += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # ----------------------------------------------------------------
    # Debug toolbar / Silk / Livereload URLs
    # ----------------------------------------------------------------
    updated = configure_urls(updated)

    return updated
