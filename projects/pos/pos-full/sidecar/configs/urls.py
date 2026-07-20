"""
POS Full — Django URL Configuration.

Provides Django admin panel URL routing for the master manager.
This is configured in Django settings (ROOT_URLCONF) and served
via `python manage.py runserver` on port 8000.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
