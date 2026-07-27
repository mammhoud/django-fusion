"""
Health check view for django-grep.
Provides a lightweight /health/ endpoint that returns HTTP 200
when the application is operational.
"""

from django.http import JsonResponse


def health_check(request):
    """Return HTTP 200 with JSON status when the application is running."""
    return JsonResponse({"status": "ok"}, status=200)
