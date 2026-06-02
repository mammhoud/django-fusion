from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

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

# Plugin routing
try:
    plugin_patterns = [path("", include("plugins.urls"))]
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

# Ensure a basic health endpoint is always present even if the debug tools
# package or its URL wiring is unavailable.
try:
    urlpatterns += [path("health/", include("django_grep.health.urls"))]
except Exception:
    try:
        from django.http import JsonResponse

        def _basic_health(request):
            return JsonResponse({"status": "ok"})

        urlpatterns += [path("health/", _basic_health)]
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

# Static/assets health endpoint for deployment smoke tests.
try:
    from django.http import JsonResponse

    def _assets_health(request):
        static_url = getattr(settings, "STATIC_URL", "/static/")
        return JsonResponse({"status": "ok", "static_url": static_url})

    urlpatterns += [path("assets/health/", _assets_health, name="assets-health")]
except Exception:
    pass
