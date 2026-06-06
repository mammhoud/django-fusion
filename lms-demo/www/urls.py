import os

# Import shared configuration modules from parent directory
import sys

from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve
from django_grep.contrib.debug_tools.common_urls import configure_common_urls
from django_grep.contrib.debug_tools.error_views import (
    handler400,
    handler403,
    handler404,
    handler500,
)
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from proxy import assets_health as _assets_health
from proxy import health as _health
from utilities import get_root_redirect_pattern

urlpatterns = [
    path("health/", _health, name="health"),
    path("assets/health/", _assets_health, name="assets-health"),
    path("health/assets/", _assets_health, name="health-assets"),
    path("django-admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("auth/login/", LoginView.as_view(), name="account_login"),
    path("auth/logout/", LogoutView.as_view(), name="account_logout"),
    path("auth/register/", SignupView.as_view(), name="account_signup"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="account_reset_password"),
]

# Language switching, sitemaps, robots.txt
urlpatterns = configure_common_urls(urlpatterns)

urlpatterns += i18n_patterns(path("", include("plugins.urls")), prefix_default_language=False)
urlpatterns += [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]
urlpatterns += i18n_patterns(path("", include(wagtail_urls)), prefix_default_language=False)

if settings.DEBUG:
    try:
        from django_grep.contrib.debug_tools.dev_urls import configure_dev_urls
        urlpatterns = configure_dev_urls(urlpatterns, settings)
    except Exception:
        pass

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
