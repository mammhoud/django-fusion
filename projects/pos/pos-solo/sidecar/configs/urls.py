"""
POS Full — Django URL Configuration.

Provides Django admin panel URL routing for the master manager.
The admin index page is replaced by the custom Unfold dashboard
(via UNFOLD[\"DASHBOARD\"] in configs/__init__.py).

Usage:
    python manage.py runserver 0.0.0.0:8000
    → http://localhost:8000/admin/  (Unfold dashboard with KPIs)
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
