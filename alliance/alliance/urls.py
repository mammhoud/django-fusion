from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from django_rseal.contrib.debug_tools.common_urls import configure_common_urls
from django_rseal.contrib.debug_tools.error_views import (
    handler400, handler403, handler404, handler500,
)

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

# Language switching, sitemaps, robots.txt — all from django-grep
urlpatterns = configure_common_urls(urlpatterns)

urlpatterns += i18n_patterns(
    # apps.urls includes django_rseal.pipelines.urls (health + auth routes)
    path("", include("apps.urls")),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

if settings.DEBUG:
    from django_rseal.contrib.debug_tools.dev_urls import configure_dev_urls
    urlpatterns = configure_dev_urls(urlpatterns, settings)
