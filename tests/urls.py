"""
Minimal URL configuration for tests that don't need full app URLs.
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
