"""Minimal URL configuration for API smoke tests.

Imports the real API URL patterns from apps.core.api.urls so that
the test client can exercise the actual endpoint code paths.
"""

from __future__ import annotations

from django.urls import include, path

from django_fusion.core.assets import urls as assets_urls
from apps.pages.blog import api as blog_api
from apps.pages.pages import landing_api

urlpatterns = [
    path("apis/site/settings/", landing_api.site_settings_api),
    path("apis/navigation/", landing_api.navigation_api),
    path("apis/content/languages/", landing_api.content_languages_api),
    path("apis/research/publications/", landing_api.research_publications_api),
    path("apis/contact/", landing_api.contact_api),
    path("apis/auth/status/", landing_api.auth_status_api),
    path("apis/blog/<slug:slug>/comments/", blog_api.blog_comments_api),
    path("apis/pages/", landing_api.page_list_api),
    path("apis/pages/<str:slug>/", landing_api.page_data_api),
    path("apis/assets/", landing_api.assets_api),
    path("fragment/ping/", landing_api.htmx_ping_api),
    path("fragment/pages/<slug:slug>/", landing_api.page_fragment_api),
    path("api/", include("apps.core.api.urls")),
    path("fusion/assets/", include(assets_urls)),
    # Language switching + page/auth namespaces referenced by the shared
    # landing header (partials/language_selector.html → set_language;
    # partials/auth_buttons.html → plugins:* / plugins:profile:*).
    path("i18n/setlang/", landing_api.set_language_api, name="set_language"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.pages.urls", namespace="plugins")),
]
