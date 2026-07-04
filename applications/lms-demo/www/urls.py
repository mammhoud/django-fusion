import os

# Import shared configuration modules from parent directory
import sys

from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from django.views.static import serve

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from django_osoul.health import AssetsHealthView, DatabaseHealthView, HealthCheckView
from django_osoul.site.utils import get_root_redirect_pattern
from www.core.routes import site

# Optional imports with safe fallbacks
try:
    from django_osoul.contrib.debug_tools.common_urls import configure_common_urls
except Exception:
    def configure_common_urls(urlpatterns):
        return urlpatterns

try:
    from django_osoul.contrib.debug_tools.error_views import (
        handler400,
        handler403,
        handler404,
        handler500,
    )
except Exception:
    handler400 = handler403 = handler404 = handler500 = None

try:
    from wagtail import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls
    from wagtail.documents import urls as wagtaildocs_urls
except Exception:
    wagtail_urls = wagtailadmin_urls = wagtaildocs_urls = None


# Build a robust module-level urlpatterns regardless of optional imports
urlpatterns = []

# Health endpoints + allauth URLs (registered at top-level so they work
# before i18n/Wagtail and are NOT gated by Wagtail availability — mirrors
# applications/ctc-research/www/urls.py for /accounts/login/ parity).
# Localized /en/accounts/login/ etc. are out of scope for this site: a
# `prefix_default_language=False` i18n mirror would either collide with
# Wagtail's localized catch-all or duplicate URL names, and CTC's
# non-localized accounts/ tree is the structural baseline we follow.
urlpatterns += [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("assets/health/", AssetsHealthView.as_view(), name="assets-health"),
    path("health/database/", DatabaseHealthView.as_view(), name="health-database"),
    path("accounts/", include("allauth.urls")),
]  # pragma: no cover -- declarative URL list

# Only add Django admin if installed (avoids "No installed app with label 'admin'" errors)
try:
    if apps.is_installed("django.contrib.admin"):
        from django.contrib import admin

        urlpatterns.append(path("django-admin/", admin.site.urls))
except Exception:
    # If anything goes wrong, skip binding the admin route.
    pass

# Language switching, sitemaps, robots.txt (from debug_tools if available)
urlpatterns = configure_common_urls(urlpatterns)


# Redirect duplicated sitemap crawler noise before the CMS catch-all handles it.
urlpatterns += [
    path(
        "sitemap.xml/sitemap.xml",
        RedirectView.as_view(url="/sitemap.xml", permanent=True),
        name="redirect-duplicated-sitemap-index",
    ),
    path(
        "sitemap-news.xml/sitemap-news.xml",
        RedirectView.as_view(url="/sitemap-news.xml", permanent=True),
        name="redirect-duplicated-sitemap-news",
    ),
]

# Plugin routing — must pass namespace explicitly so templates can use
# {% url 'plugins:login' %} etc.
try:
    plugin_patterns = [path("", include(("plugins.urls", "plugins"), namespace="plugins"))]
except Exception:
    plugin_patterns = []

urlpatterns += i18n_patterns(*plugin_patterns, prefix_default_language=False)

# Wagtail slug-change redirects — old /about-page/ → /about/, /team-page/ → /team/
# These sit before the Wagtail catch-all so they take priority.  Wagtail's built-in
# RedirectMiddleware also has the same redirects in the database, but its
# process_response hook does not reliably intercept 404s in this version stack.
class _LocalePreservingRedirectView(RedirectView):
    """Preserve the active i18n language prefix on permanent redirects.

    Without this, a request to ``/de/about-page/`` activates the 'de'
    locale via ``i18n_patterns`` but then redirects to ``/about/``
    (default locale) instead of ``/de/about/``.
    """
    permanent = True
    url = None  # subclass must set url

    def get_redirect_url(self, *args, **kwargs):
        from django.utils.translation import get_language
        from django.conf import settings
        lang = get_language()
        if lang and lang != settings.LANGUAGE_CODE:
            return f"/{lang}{self.url}"
        return self.url


urlpatterns += i18n_patterns(
    path(
        "about-page/",
        _LocalePreservingRedirectView.as_view(url="/about/"),
        name="redirect-about-page",
    ),
    path(
        "team-page/",
        _LocalePreservingRedirectView.as_view(url="/team/"),
        name="redirect-team-page",
    ),
    path(
        "contact-page/",
        _LocalePreservingRedirectView.as_view(url="/contact/"),
        name="redirect-contact-page",
    ),
    path(
        "home-page/",
        _LocalePreservingRedirectView.as_view(url="/"),
        name="redirect-home-page",
    ),
    prefix_default_language=False,
)

# Routable component site (documented under docs/routable-site-urls.md)
urlpatterns += [path("osoul/", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))]

# Wagtail routing when available
if wagtail_urls and wagtailadmin_urls and wagtaildocs_urls:
    urlpatterns += [path("admin/", include(wagtailadmin_urls)), path("documents/", include(wagtaildocs_urls))]
    urlpatterns += i18n_patterns(path("", include(wagtail_urls)), prefix_default_language=False)

# Development debug URLs
if settings.DEBUG:
    try:
        from django_osoul.contrib.debug_tools.dev_urls import configure_dev_urls

        urlpatterns = configure_dev_urls(urlpatterns, settings)
    except Exception:
        pass

try:
    urlpatterns += [path("health_admin/", include("django_osoul.health.urls"))]
except Exception:
    pass

# Serve collected static files and uploaded media from Django as a fallback when
# a dedicated media/static server is not mounted in front of the active website.
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(
        r"^{media_url}(?P<path>.*)$".format(media_url=settings.MEDIA_URL.lstrip("/")),
        serve,
        {"document_root": settings.MEDIA_ROOT},
    )
]

# Root path redirect to default language (MUST be at the end as catch-all fallback)
urlpatterns += [get_root_redirect_pattern()]
