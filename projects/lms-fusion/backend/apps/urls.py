"""
URL configuration for lms-fusion.

App patterns use string-based include so Django defers the import of
apps.pages.urls until after django.setup() completes.
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
try:
    from django_fusion.core.assets import urls as assets_urls
except ImportError:
    assets_urls = None
from django_fusion.core.health.views import AssetsHealthView, DatabaseHealthView, HealthCheckView
from django_fusion.core.utils import get_root_redirect_pattern
from apps.core.routes import site
from apps.pages.pages import landing_api

# ── Optional tooling ────────────────────────────────────────────────────────
try:
    from django_fusion.contrib.debug_tools.common_urls import configure_common_urls
except Exception:
    def configure_common_urls(urlpatterns):
        return urlpatterns

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
    from django.http import HttpResponse, JsonResponse
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
            try:
                return JsonResponse(
                    {
                        "status": "error",
                        "status_code": status_code,
                        "error_title": error_title,
                        "error_message": error_message,
                    },
                    status=status_code,
                )
            except Exception:
                return HttpResponse(f"Error {status_code}: {error_title}", status=status_code)

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

# ── Health & admin ───────────────────────────────────────────────────────────
urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    # Astro/AHA landing contract. The existing LMS `/api/` contract remains
    # untouched; these `/apis/` and `/fragment/` routes are additive.
    path("apis/render-mode/", landing_api.render_mode_api, name="landing-render-mode"),
    path("apis/site/settings/", landing_api.site_settings_api, name="landing-site-settings"),
    path("apis/navigation/", landing_api.navigation_api, name="landing-navigation"),
    path("apis/contact/", landing_api.contact_api, name="landing-contact"),
    path("apis/pages/", landing_api.page_list_api, name="landing-page-list"),
    path("apis/pages/<str:slug>/", landing_api.page_data_api, name="landing-page-data"),
    path("apis/assets/", landing_api.assets_api, name="landing-assets"),
    path("fragment/contact/", landing_api.contact_submit_api, name="landing-contact-submit"),
    path("fragment/ping/", landing_api.htmx_ping_api, name="landing-ping"),
    path("api/newsletter/subscribe/", landing_api.newsletter_subscribe_api, name="landing-newsletter"),
    path("assets/health/", AssetsHealthView.as_view(), name="assets-health"),
    path("health/database/", DatabaseHealthView.as_view(), name="health-database"),
    path("accounts/", include("allauth.urls")),
]

if assets_urls is not None:
    urlpatterns += [
        path("fusion/assets/", include(assets_urls)),
    ]

if apps.is_installed("django.contrib.admin"):
    from django.contrib import admin
    urlpatterns.append(path("django-admin/", admin.site.urls))

# ── Common URLs (sitemaps, robots, i18n switching) ───────────────────────────
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

# ── App routing ────────────────────────────────────────────────────────────
urlpatterns += i18n_patterns(
    path("", include("apps.pages.urls", namespace="plugins")),
    prefix_default_language=False,
)

# ── Cart & Checkout ──────────────────────────────────────────────────────
urlpatterns += i18n_patterns(
    path("cart/", include("apps.core.urls", namespace="cart")),
    prefix_default_language=False,
)

# ── Privacy & Terms ──────────────────────────────────────────────────────
urlpatterns += i18n_patterns(
    path("legal/", include("apps.handlers.urls", namespace="legal")),
    prefix_default_language=False,
)

# ── REST API ────────────────────────────────────────────────────────
urlpatterns += [
    path("api/", include("apps.core.api.urls")),
]

# ── Routable component site ─────────────────────────────────────────────
urlpatterns += [path("osoul/", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))]

# ── Old slug redirects (about-page → about, team-page → team) ──────────────
class _LocalePreservingRedirectView(RedirectView):
    """RedirectView subclass that preserves the active i18n language prefix."""
    permanent = True
    url = None

    def get_redirect_url(self, *args, **kwargs):
        redirect_url = super().get_redirect_url(*args, **kwargs)
        from django.utils.translation import get_language
        current_lang = get_language()
        default_lang = settings.LANGUAGE_CODE
        if current_lang and current_lang != default_lang and redirect_url:
            redirect_url = f"/{current_lang}{redirect_url}"
        return redirect_url


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
