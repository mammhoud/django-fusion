"""
Proxy and health check endpoints.

This module contains health check views and proxy-related utilities
for monitoring application status and connectivity.
"""

from django.conf import settings
from django.http import JsonResponse


def health(request):
    """Basic health check endpoint for monitoring."""
    return JsonResponse({
        "status": "ok",
        "site": getattr(settings, "WEBSITE_NAME", "unknown")
    })


def assets_health(request):
    """Health check endpoint for static assets."""
    static_url = getattr(settings, "STATIC_URL", "/static/")
    return JsonResponse({
        "status": "ok",
        "static_url": static_url
    })


def database_health(request):
    """Health check endpoint for database connectivity."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = str(e)

    return JsonResponse({
        "status": "ok",
        "database": db_status
    })
