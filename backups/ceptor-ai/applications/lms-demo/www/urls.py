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
from django_fusion.health import DatabaseHealthView, HealthCheckView
from django_fusion.site.interface.utils import get_root_redirect_pattern
from django.views.i18n import set_language
from www.core.routes import site

# Shared cross-site redirect helper (consolidated from per-site duplicates)
from applications.www.core.redirects import LocalePreservingRedirectView

# Optional imports with safe fallbacks
try:
    from django_fusion.contrib.debug_tools.common_urls import configure_common_urls
    _common_urls_available = True
except Exception:
    def configure_common_urls(urlpatterns):
        return urlpatterns
    _common_urls_available = False

try:
    from django_fusion.contrib.debug_tools.error_views import (
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

# Health & auth accounts (top-level, before i18n/Wagtail)
urlpatterns += [
    path("health/", HealthCheckView.as_view(), name="health"),
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

# Fallback: ensure set_language is always available even when configure_common_urls
# fails to import due to circular dependencies in django_fusion.debug_tools.
if not _common_urls_available:
    urlpatterns += [
        path("set-language/", set_language, name="set_language"),
        path("i18n/", include("django.conf.urls.i18n")),
    ]


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
# ``LocalePreservingRedirectView`` is now provided by
# ``applications/www/projects/redirects.py`` (consolidated from the
# byte-identical local class that used to live in ctc + lms www/urls.py).
urlpatterns += i18n_patterns(
    path(
        "about-page/",
        LocalePreservingRedirectView.as_view(url="/about/"),
        name="redirect-about-page",
    ),
    path(
        "team-page/",
        LocalePreservingRedirectView.as_view(url="/team/"),
        name="redirect-team-page",
    ),
    path(
        "contact-page/",
        LocalePreservingRedirectView.as_view(url="/contact/"),
        name="redirect-contact-page",
    ),
    path(
        "home-page/",
        LocalePreservingRedirectView.as_view(url="/"),
        name="redirect-home-page",
    ),
    prefix_default_language=False,
)

# Routable component site (documented under docs/routable-site-urls.md)
urlpatterns += [path("fusion/", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))]

# Wagtail routing when available
if wagtail_urls and wagtailadmin_urls and wagtaildocs_urls:
    urlpatterns += [path("admin/", include(wagtailadmin_urls)), path("documents/", include(wagtaildocs_urls))]
    urlpatterns += i18n_patterns(path("", include(wagtail_urls)), prefix_default_language=False)

# Development debug URLs
if settings.DEBUG:
    try:
        from django_fusion.contrib.debug_tools.dev_urls import configure_dev_urls

        urlpatterns = configure_dev_urls(urlpatterns, settings)
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
