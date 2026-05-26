"""
Test URL configuration for blog app tests.
Wraps blog URLs with the 'blog' namespace.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls", namespace="blog")),
]
