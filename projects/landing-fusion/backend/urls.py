"""Landing-fusion URL configuration — Wagtail admin + document URLs + page routes."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.content.views import BroadcastEmailView
from apps.pages import api as pages_api

urlpatterns = [
    path("django-admin/", admin.site.urls),
    # Newsletter broadcast — staff-only, registered BEFORE the wagtail admin
    # include so the fixed path wins. Linked from the NewsletterSubscriber
    # snippet index header button ("Email subscribers").
    path(
        "admin/newsletter/broadcast/",
        BroadcastEmailView.as_view(),
        name="wagtailadmin_newsletter_broadcast",
    ),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # ── Auth — django-allauth headless API (/api/auth/login, session, …)
    # Consumed by the Alpine login modal (both render roads). Social provider
    # redirects: /api/auth/provider/login?provider=github …
    path("api/auth/", include("allauth.headless.urls")),

    # ── Auth — server-rendered allauth pages (/accounts/login/, signup,
    #    password reset, email management, email confirmation…). Mirrors the
    #    headless API flows with full pages for no-JS + management screens.
    path("accounts/", include("allauth.urls")),

    # ── APIs — backend-driven content for the Astro frontend ──────────
    path("apis/render-mode/", pages_api.render_mode_api, name="render_mode_api"),
    path("apis/site/settings/", pages_api.site_settings_api, name="site_settings_api"),
    path("apis/navigation/", pages_api.navigation_api, name="navigation_api"),
    path("apis/contact/", pages_api.contact_api, name="contact_api"),
    path("apis/pricing/", pages_api.pricing_api, name="pricing_api"),
    path("apis/brand/", pages_api.brand_api, name="brand_api"),
    path("apis/pages/", pages_api.page_list_api, name="page_list_api"),
    path("apis/pages/<slug:slug>/", pages_api.page_data_api, name="page_data_api"),
    path("apis/assets/", pages_api.assets_api, name="assets_api"),

    # ── Auth (allauth — login, register, password reset, social) ─────
    path("accounts/", include("allauth.urls")),
    path("apis/auth/status/", pages_api.auth_status_api, name="auth_status_api"),

    # ── Fragment endpoints (HTMX HTML swaps) ──────────────────────────
    path("fragment/contact/", pages_api.contact_submit_api, name="contact_submit"),
    path("api/newsletter/subscribe/", pages_api.newsletter_subscribe_api, name="newsletter_subscribe"),
    path("api/newsletter/status/", pages_api.newsletter_status_api, name="newsletter_status"),
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
