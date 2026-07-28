"""
URL configuration for ctc-research.

Plugin patterns use string-based include so Django defers the import of
plugins.urls until after django.setup() completes — preventing the
`Conflicting 'role' models` RuntimeError that occurs when
django_fusion.site is imported during URL-pattern construction.
"""
import os
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

# ── Optional tooling ────────────────────────────────────────────────────────
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

if handler400 is None:
    from django.http import HttpResponse
    from django.shortcuts import render

    def _fallback_error_view(request, exception=None, status_code=500, **kwargs):
        error_titles = {
            400: "Bad Request",
            403: "Permission Denied",
            404: "Page Not Found",
            500: "Internal Server Error",
        }
        error_title = error_titles.get(status_code, "Error")
        error_message = str(exception) if exception else "An unexpected error occurred."
        try:
            return render(
                request,
                "errors/nxx.html",
                {
                    "status_code": status_code,
                    "error_title": error_title,
                    "error_message": error_message,
                    "exception": str(exception) if exception else None,
                },
                status=status_code,
            )
        except Exception:
            # Ultimate fallback — render inline HTML, never JSON
            return HttpResponse(
                f"<html><head><title>{error_title}</title></head>"
                f"<body style='font-family:sans-serif;text-align:center;padding:4rem 2rem;'>"
                f"<h1 style='font-size:4rem;margin:0;'>{status_code}</h1>"
                f"<h2>{error_title}</h2>"
                f"<p>{error_message}</p>"
                f"<a href='/'>Go home</a>"
                f"</body></html>",
                status=status_code,
                content_type="text/html",
            )

    def handler400(request, exception=None, **kwargs):
        return _fallback_error_view(request, exception, status_code=400, **kwargs)

    def handler403(request, exception=None, **kwargs):
        return _fallback_error_view(request, exception, status_code=403, **kwargs)

    def handler404(request, exception=None, **kwargs):
        return _fallback_error_view(request, exception, status_code=404, **kwargs)

    def handler500(request, **kwargs):
        return _fallback_error_view(request, None, status_code=500, **kwargs)

try:
    from wagtail import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls
    from wagtail.documents import urls as wagtaildocs_urls
except Exception:
    wagtail_urls = wagtailadmin_urls = wagtaildocs_urls = None

# ── Health, admin & accounts ─────────────────────────────────────────────
urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("health/database/", DatabaseHealthView.as_view(), name="health-database"),
    path("accounts/", include("allauth.urls")),
]

if apps.is_installed("django.contrib.admin"):
    from django.contrib import admin
    urlpatterns.append(path("django-admin/", admin.site.urls))

# ── Common URLs (sitemaps, robots, i18n switching) ───────────────────────────
urlpatterns = configure_common_urls(urlpatterns)

# Fallback: ensure set_language is always available even when configure_common_urls
# fails to import due to circular dependencies in django_fusion.debug_tools.
# The language_selector template uses {% url 'set_language' %} which requires this.
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

# ── Plugin routing ────────────────────────────────────────────────────────────
# Use the string form "plugins.urls" so Django imports the module lazily
# at first URL resolution — after django.setup() has fully settled the
# app registry and model registration.  The app_name="plugins" declared
# inside plugins/urls.py registers the application namespace; the explicit
# namespace= kwarg here registers the instance namespace so that both
# {% url 'plugins:login' %} and reverse('plugins:login') work.
urlpatterns += i18n_patterns(
    path("", include("plugins.urls")),
    prefix_default_language=False,
)

# ── Routable component site ─────────────────────────────────────────────
# Documented under docs/routable-site-urls.md. Mount before Wagtail catch-all.
urlpatterns += [path("fusion/", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))]

# ── Old slug redirects (about-page → about, team-page → team) ──────────────
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

# ── Wagtail ───────────────────────────────────────────────────────────────────
if wagtail_urls and wagtailadmin_urls and wagtaildocs_urls:
    urlpatterns += [
        path("admin/", include(wagtailadmin_urls)),
        path("documents/", include(wagtaildocs_urls)),
    ]
    urlpatterns += i18n_patterns(
        path("", include(wagtail_urls)),
        prefix_default_language=False,
    )

# ── Development extras ────────────────────────────────────────────────────────
if settings.DEBUG:
    try:
        from django_fusion.contrib.debug_tools.dev_urls import configure_dev_urls
        urlpatterns = configure_dev_urls(urlpatterns, settings)
    except Exception:
        pass

# ── Static / media fallback ───────────────────────────────────────────────────
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(
        r"^{media_url}(?P<path>.*)$".format(media_url=settings.MEDIA_URL.lstrip("/")),
        serve,
        {"document_root": settings.MEDIA_ROOT},
    )
]

# ── Root redirect (catch-all, must be last) ───────────────────────────────────
urlpatterns += [get_root_redirect_pattern()]
