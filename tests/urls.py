"""
URL configuration for django-fusion tests.

Kept minimal — only imports what is available in the test conftest's
INSTALLED_APPS so we avoid ``LookupError`` during configure-time.
"""
from django.urls import path

urlpatterns: list = []
