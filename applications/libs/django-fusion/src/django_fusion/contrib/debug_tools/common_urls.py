"""
Common URL patterns for django_fusion.

This module provides common URL patterns shared across Django/Wagtail
projects including language switching, sitemaps, and robots.txt.

Functions:
    configure_common_urls: Append language-switching, sitemap, and robots.txt URL patterns.

Usage in urls.py::

    from django_fusion.contrib.debug_tools.common_urls import configure_common_urls

    urlpatterns = [...]
    urlpatterns = configure_common_urls(urlpatterns)
"""

from django.contrib.sitemaps import views as sitemap_views
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import set_language

try:
    from wagtail.contrib.sitemaps.views import index as wagtail_sitemap_index
    from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap
    _wagtail_sitemaps = True
except ImportError:
    _wagtail_sitemaps = False


def configure_common_urls(urlpatterns: list, sitemaps: dict | None = None) -> list:
    """
    Append language-switching, sitemap, and robots.txt URL patterns.

    Args:
        urlpatterns: Existing URL patterns list.
        sitemaps: Optional dict of Django sitemap classes for site.xml.
                  Defaults to an empty dict (no Django sitemaps).

    Returns:
        Updated urlpatterns list.
    """
    if sitemaps is None:
        sitemaps = {}

    updated = list(urlpatterns)

    # Language switching
    updated += [
        path("set-language/", set_language, name="set_language"),
        path("i18n/", include("django.conf.urls.i18n")),
    ]

    # Wagtail sitemaps
    if _wagtail_sitemaps:
        updated += [
            path("sitemap.xml", wagtail_sitemap_index, name="wagtail-sitemap-index"),
            path("sitemap-<section>.xml", wagtail_sitemap, name="wagtail-sitemap"),
        ]

    # Django sitemaps
    updated += [
        path("site.xml", sitemap_views.index, {"sitemaps": sitemaps}, name="django-sitemap-index"),
        path("site-<section>.xml", sitemap_views.sitemap, {"sitemaps": sitemaps}, name="django-sitemap"),
    ]

    # robots.txt
    updated += [
        path(
            "robots.txt",
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
            name="robots_txt",
        ),
    ]

    return updated
