import os

# Import shared configuration modules from parent directory
import sys

from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from django_grep.health import AssetsHealthView, DatabaseHealthView, HealthCheckView
from django_osoul.site.utils import get_root_redirect_pattern

# Optional imports with safe fallbacks
try:
    from django_grep.contrib.debug_tools.common_urls import configure_common_urls
except Exception:
    def configure_common_urls(urlpatterns):
        return urlpatterns

try:
    from django_grep.contrib.debug_tools.error_views import (
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

# Plugin routing — must pass namespace explicitly so templates can use
# {% url 'plugins:login' %} etc.
try:
    plugin_patterns = [path("", include(("plugins.urls", "plugins"), namespace="plugins"))]
except Exception:
    plugin_patterns = []

urlpatterns += i18n_patterns(*plugin_patterns, prefix_default_language=False)

# Wagtail routing when available
if wagtail_urls and wagtailadmin_urls and wagtaildocs_urls:
    urlpatterns += [path("admin/", include(wagtailadmin_urls)), path("documents/", include(wagtaildocs_urls))]
    urlpatterns += i18n_patterns(path("", include(wagtail_urls)), prefix_default_language=False)

# Development debug URLs
if settings.DEBUG:
    try:
        from django_grep.contrib.debug_tools.dev_urls import configure_dev_urls

        urlpatterns = configure_dev_urls(urlpatterns, settings)
    except Exception:
        pass

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("assets/health/", AssetsHealthView.as_view(), name="assets-health"),
    path("health/database/", DatabaseHealthView.as_view(), name="health-database"),
] + urlpatterns

try:
    urlpatterns += [path("health_admin/", include("django_grep.health.urls"))]
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
