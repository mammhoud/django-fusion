from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.i18n import set_language
from django.views.static import serve
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps import Sitemap
from wagtail.contrib.sitemaps.views import index, sitemap
from wagtail.documents import urls as wagtaildocs_urls

from core import views as core_views

# from wagtail_transfer import urls as wagtailtransfer_urls

# Wagtail sitemap registry used by Wagtail sitemap index/detail views.
sitemaps_dict = {"pages": Sitemap}

urlpatterns = [
    # Admin interfaces (language-neutral)
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Health check (used by Docker/load balancers)
    path("health/", core_views.health_check, name="health_check"),
    path("media-health/", core_views.media_health_check, name="media_health_check"),
    # Language switching
    path("set-language/", set_language, name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
    # API endpoints for cookies and theme
    path(
        "api/cookies/set-preferences/",
        core_views.set_cookie_preferences,
        name="set_cookie_preferences",
    ),
    path(
        "api/cookies/get-preferences/",
        core_views.get_cookie_preferences,
        name="get_cookie_preferences",
    ),
    path("api/theme/set/", core_views.set_theme, name="set_theme"),
    path("api/theme/get/", core_views.get_theme, name="get_theme"),
    path("api/csrf-token/", core_views.get_csrf_token, name="get_csrf_token"),
    # Wagtail sitemaps
    path(
        "sitemap.xml",
        index,
        {"sitemaps": sitemaps_dict},
        name="wagtail-sitemap-index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap,
        {"sitemaps": sitemaps_dict},
        name="wagtail-sitemap",
    ),
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
    path("", include("pages.urls")),
    # Wagtail pages (will automatically handle i18n if WAGTAIL_I18N_ENABLED = True)
    path("", include(wagtail_urls)),
    # Allow URLs without language prefix to use active language
    prefix_default_language=False,
)

# ── Media files — served by Django in all environments ──────────────
# WhiteNoise handles /static/ but NOT /media/. Since there is no
# separate nginx container for assets, Django must serve media directly.
from django.conf.urls.static import static

# Serve media files in all environments (not just DEBUG)
# WhiteNoise will optimize this in production
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(
        r"^{media_url}(?P<path>.*)$".format(media_url=settings.MEDIA_URL.lstrip("/")),
        serve,
        {"document_root": settings.MEDIA_ROOT},
    )
]

# DEBUG mode specific configurations
if settings.DEBUG:
    # Error pages for debugging during development
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
            name="error-400",
        ),
        path("401/", TemplateView.as_view(template_name="401.html"), name="error-401"),
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
        path("429/", TemplateView.as_view(template_name="429.html"), name="error-429"),
        path(
            "500/",
            default_views.server_error,
            name="error-500",
        ),
        path("502/", TemplateView.as_view(template_name="502.html"), name="error-502"),
        path("503/", TemplateView.as_view(template_name="503.html"), name="error-503"),
        path("504/", TemplateView.as_view(template_name="504.html"), name="error-504"),
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

    # # Serve .well-known directory for development
    # urlpatterns += static(
    #     "/.well-known/",
    #     document_root=settings.ASSETS_DIR + "/.well-known/",
    # )
