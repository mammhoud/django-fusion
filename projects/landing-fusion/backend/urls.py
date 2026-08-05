"""Landing-fusion URL configuration — Wagtail admin + document URLs + page routes."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.pages import api as pages_api

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # ── APIs — backend-driven content for the Astro frontend ──────────
    path("apis/render-mode/", pages_api.render_mode_api, name="render_mode_api"),
    path("apis/site/settings/", pages_api.site_settings_api, name="site_settings_api"),
    path("apis/navigation/", pages_api.navigation_api, name="navigation_api"),
    path("apis/contact/", pages_api.contact_api, name="contact_api"),
    path("apis/pages/", pages_api.page_list_api, name="page_list_api"),
    path("apis/pages/<slug:slug>/", pages_api.page_data_api, name="page_data_api"),
    path("apis/assets/", pages_api.assets_api, name="assets_api"),

    # ── Fragment endpoints (HTMX HTML swaps) ──────────────────────────
    path("fragment/contact/", pages_api.contact_submit_api, name="contact_submit"),
    path("api/newsletter/subscribe/", pages_api.newsletter_subscribe_api, name="newsletter_subscribe"),
    path("fragment/ping/", pages_api.htxm_ping_api, name="htmx_ping"),

    # Landing page handlers — django-fusion PageHandler views that render each
    # Wagtail page through the unified fragment/layout pipeline (HTMX-aware).
    # They sit BEFORE Wagtail's catch-all so fragments serve the same templates.
    path("", include("apps.handlers.urls")),
    # 404 — Wagtail serves unknown page paths, so this only catches admin/API misses
    path("404/", TemplateView.as_view(template_name="pages/404.html"), name="error-404"),
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
