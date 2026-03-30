from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.i18n import set_language
from django.views.static import serve
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import index, sitemap
from wagtail.documents import urls as wagtaildocs_urls

# from wagtail_transfer import urls as wagtailtransfer_urls

# Create an empty sitemaps dictionary for Django sitemaps
sitemaps_dict = {}


def health_check(request):
    """Health check endpoint — returns HTTP 200 when server is operational."""
    return JsonResponse({"status": "healthy"})


urlpatterns = [
    # Health check (language-neutral, no auth required)
    path("health/", health_check, name="health-check"),
    # Admin interfaces (language-neutral)
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Language switching
    path("set-language/", set_language, name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
    # Content transfer
    # path("content-transfer/", include(wagtailtransfer_urls)),
    # Wagtail sitemaps
    path("sitemap.xml", index, name="wagtail-sitemap-index"),
    path("sitemap-<section>.xml", sitemap, name="wagtail-sitemap"),
    # Django sitemaps (empty by default, can be populated with models)
    path(
        "site.xml",
        sitemap_views.index,
        {"sitemaps": sitemaps_dict},
        name="django-sitemap-index",
    ),
    path(
        "site-<section>.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps_dict},
        name="django-sitemap",
    ),
    # Robots.txt (language-neutral, important for SEO)
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    # Chrome DevTools configuration (in production, served by web server)
    # This pattern is enabled in DEBUG mode below, but the path is defined here
    # for clarity and to avoid 404s in production
]

# Internationalized URL patterns - these will have language prefixes
# When prefix_default_language=False, URLs without language prefix use active language
urlpatterns += i18n_patterns(
    # Your custom apps with i18n support
    path("", include("apps.urls")),
    path("", include("django_grep.pipelines.urls")),
    # Wagtail pages (will automatically handle i18n if WAGTAIL_I18N_ENABLED = True)
    path("", include(wagtail_urls)),
    # Allow URLs without language prefix to use active language
    prefix_default_language=False,
)

# DEBUG mode specific configurations
if settings.DEBUG:
    from django_grep.contrib.debug_tools import configure_urls  # noqa
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Add debug toolbar
    urlpatterns = configure_urls(urlpatterns)

    # Error pages for debugging during development
    urlpatterns += [
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
        path(
            "500/",
            default_views.server_error,
            name="error-500",
        ),
        path("502/", TemplateView.as_view(template_name="errors/502.html"), name="error-502"),
        path("503/", TemplateView.as_view(template_name="errors/503.html"), name="error-503"),
        path("504/", TemplateView.as_view(template_name="errors/504.html"), name="error-504"),

        # # Chrome DevTools configuration file (development only)
        # re_path(
        #     r"^\.well-known/appspecific/com\.chrome\.devtools\.json$",
        #     serve,
        #     {
        #         "document_root": settings.ASSETS_DIR,
        #         "path": ".well-known/appspecific/com.chrome.devtools.json",
        #     },
        #     name="chrome_devtools_json",
        # ),
    ]

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # # Serve .well-known directory for development
    # urlpatterns += static(
    #     "/.well-known/",
    #     document_root=settings.ASSETS_DIR + "/.well-known/",
    # )

# Unified custom error view
import sys, traceback
from django.shortcuts import render

def custom_error_view(request, exception=None, status_code=500):
    error_title = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Permission Denied",
        404: "Page Not Found",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout"
    }.get(status_code, "Error")

    error_message = getattr(exception, "message", str(exception)) if exception else "An unexpected error occurred."

    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_logs = ""
    if exc_traceback:
        error_logs = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    return render(request, "errors/nxx.html", {
        "status_code": status_code,
        "error_title": error_title,
        "error_message": error_message,
        "error_logs": error_logs,
        "exception": str(exception) if exception else None,
    }, status=status_code)

def custom_page_not_found(request, exception, *args, **kwargs):
    return custom_error_view(request, exception, status_code=404)

def custom_server_error(request, *args, **kwargs):
    return custom_error_view(request, None, status_code=500)

def custom_bad_request(request, exception, *args, **kwargs):
    return custom_error_view(request, exception, status_code=400)

def custom_permission_denied(request, exception, *args, **kwargs):
    return custom_error_view(request, exception, status_code=403)

handler404 = custom_page_not_found
handler500 = custom_server_error
handler400 = custom_bad_request
handler403 = custom_permission_denied
