"""
URL configuration for the CRM site.
"""
import os
import sys

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django_fusion.health import AssetsHealthView, DatabaseHealthView, HealthCheckView
from django_fusion.site.interface.utils import get_root_redirect_pattern
from www.core.routes import site

# ── Optional debug tooling ──────────────────────────────────────────────────
try:
    from django_fusion.contrib.debug_tools.common_urls import configure_common_urls
except Exception:
    def configure_common_urls(urlpatterns):
        return urlpatterns

# ── Health ──────────────────────────────────────────────────────────────────
urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("assets/health/", AssetsHealthView.as_view(), name="assets-health"),
    path("health/database/", DatabaseHealthView.as_view(), name="health-database"),
]

# ── Django admin ────────────────────────────────────────────────────────────
from django.apps import apps as django_apps
if django_apps.is_installed("django.contrib.admin"):
    from django.contrib import admin
    urlpatterns.append(path("django-admin/", admin.site.urls))

# ── allauth ─────────────────────────────────────────────────────────────────
urlpatterns += [
    path("accounts/", include("allauth.urls")),
]

# ── Common URLs (sitemaps, robots, i18n) ────────────────────────────────────
urlpatterns = configure_common_urls(urlpatterns)

# ── Plugin routes (lazy string import to avoid circular import at startup) ──
urlpatterns += i18n_patterns(
    path("", include("plugins.urls")),
    prefix_default_language=False,
)

# ── Routable component site ─────────────────────────────────────────────────
# Mount with no outer namespace — routes use their app namespaces directly,
# matching the osoul convention: 'dashboard:dashboard', 'inventory:item:list'
urlpatterns += [
    path("crm/", include((site.urls[0], site.urls[1]))),
]

# ── Static / media fallback ─────────────────────────────────────────────────
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(
        r"^{media_url}(?P<path>.*)$".format(media_url=settings.MEDIA_URL.lstrip("/")),
        serve,
        {"document_root": settings.MEDIA_ROOT},
    )
]

# ── Root redirect (catch-all, must be last) ──────────────────────────────────
urlpatterns += [get_root_redirect_pattern()]
