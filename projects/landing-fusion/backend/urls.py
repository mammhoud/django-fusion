"""Landing-fusion URL configuration — Wagtail admin + document URLs + page routes."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from django_fusion.designer import urls as fusion_designer_urls
from django_fusion.tasks.views import TaskCenterView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.content.views import BroadcastEmailView
from apps.handlers.fusion import landing_pages_application
from apps.learning.fusion import learning_application
from apps.pages import api as pages_api

# ── Fusion introspection (plugin map + component usage + render tracker) ──
try:
    from django_fusion.plugins.debug_tools.introspection import (
        fusion_introspection_urls,
    )
except ImportError:  # pragma: no cover - older django-fusion
    fusion_introspection_urls = None

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("fusion/mcp/designer/", include(fusion_designer_urls)),
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
    # Browsers commonly probe the legacy ICO path even when the document
    # advertises the shared SVG favicon. Keep that probe quiet on both roads.
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.svg", permanent=False)),

    # ── Auth — django-allauth headless API (/api/auth/login, session, …)
    # Consumed by the Alpine login modal (both render roads). Social provider
    # redirects: /api/auth/provider/login?provider=github …
    path("api/auth/", include("allauth.headless.urls")),

    # ── Learning — django-fusion Application (dual-mode HTMX surface) ──
    # Mounts LearningApplication at /learning/ with the ``learning``
    # namespace (the same namespace apps.learning.urls exposed, so
    # reverse("learning:course") and {% url 'learning:...' %} keep resolving).
    # Authenticated mutations use the same allauth session cookie as the
    # Astro header/profile.
    path(
        "learning/",
        # Mount the Application's declared patterns with the ``learning``
        # namespace (same namespace apps.learning.urls exposed, so
        # reverse("learning:course") keeps resolving).
        include((learning_application.urlpatterns, "learning"), namespace="learning"),
    ),

    # ── Auth — server-rendered allauth pages (/accounts/login/, signup,
    #    password reset, email management, email confirmation…). Mirrors the
    #    headless API flows with full pages for no-JS + management screens.
    path("accounts/", include("allauth.urls")),

    # ── APIs — backend-driven content for the Astro frontend ──────────
    path("apis/render-mode/", pages_api.render_mode_api, name="render_mode_api"),
    path("apis/site/settings/", pages_api.site_settings_api, name="site_settings_api"),
    path("apis/navigation/", pages_api.navigation_api, name="navigation_api"),
    path("apis/content/languages/", pages_api.content_languages_api, name="content_languages_api"),
    path("apis/contact/", pages_api.contact_api, name="contact_api"),
    path("apis/pricing/", pages_api.pricing_api, name="pricing_api"),
    path("apis/products/", pages_api.products_api, name="products_api"),
    path("apis/courses/", pages_api.courses_api, name="courses_api"),
    path("apis/brand/", pages_api.brand_api, name="brand_api"),
    path("apis/pages/", pages_api.page_list_api, name="page_list_api"),
    path("apis/pages/<slug:slug>/", pages_api.page_data_api, name="page_data_api"),
    path("apis/blog/<slug:slug>/comments/", pages_api.blog_comments_api, name="blog_comments"),
    path("fragment/pages/<slug:slug>/", pages_api.page_fragment_api, name="page_fragment_api"),
    path("apis/assets/", pages_api.assets_api, name="assets_api"),

    # ── Auth status (allauth pages are registered once above) ─────────
    path("apis/auth/status/", pages_api.auth_status_api, name="auth_status_api"),

    # ── Task Center — authenticated background-job history ────────────
    path(
        "tasks/",
        TaskCenterView.as_view(site_name="landing-fusion", template_name="tasks/task_center.html"),
        name="tasks",
    ),

    # ── Fragment endpoints (HTMX HTML swaps) ──────────────────────────
    path("fragment/contact/", pages_api.contact_submit_api, name="contact_submit"),
    path("api/newsletter/subscribe/", pages_api.newsletter_subscribe_api, name="newsletter_subscribe"),
    path("api/newsletter/status/", pages_api.newsletter_status_api, name="newsletter_status"),
    path("fragment/ping/", pages_api.htxm_ping_api, name="htmx_ping"),

    # Landing page handlers — django-fusion LandingPagesApplication: the same
    # PageHandler views rendered through the unified fragment/layout pipeline
    # (HTMX-aware), now registered with menu metadata (name/icon/title). It
    # sits BEFORE Wagtail's catch-all so fragments serve the same templates.
    path(
        "",
        # LandingPagesApplication — the PageHandler routes with menu metadata,
        # mounted at the site root with the ``pages`` namespace.
        include((landing_pages_application.urlpatterns, "pages"), namespace="pages"),
    ),
    # 404 — Wagtail serves unknown page paths, so this only catches admin/API misses
    path("404/", TemplateView.as_view(template_name="pages/404.html"), name="error-404"),
]

# These finder routes must precede Wagtail's catch-all: otherwise a request
# for /static/... is treated as a page path and Wagtail returns its 404. The
# finder route is kept available in every mode for deterministic health checks
# and local fallback; production proxies should still serve STATIC_ROOT
# directly after collectstatic.
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ── Fusion introspection dashboard + API (plugin map, tracker) ──────────
if fusion_introspection_urls is not None:
    urlpatterns += fusion_introspection_urls()

# Wagtail is deliberately last because it owns the remaining document paths.
urlpatterns += [path("", include(wagtail_urls))]
