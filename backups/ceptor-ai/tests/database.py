"""
Database utilities and helpers.

This module contains database-related utilities for connectivity checks,
transactions, and other database operations.
"""

from django.http import JsonResponse


def database_health_check(request):
    """Health check endpoint for database connectivity with detailed diagnostics."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
        http_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
        http_status = "degraded"

    return JsonResponse({
        "status": http_status,
        "database": db_status
    })
