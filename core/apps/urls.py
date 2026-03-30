from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.i18n import set_language
from django.views.static import serve
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import index, sitemap
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Your custom apps with i18n support
    path("lms/", include("apps.LMS.urls")),
    path("", include("apps.handlers.urls")),
]
