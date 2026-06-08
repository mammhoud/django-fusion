"""Health check endpoint for structa.cloud."""
from django.http import JsonResponse


def health_check(request):
    """Return HTTP 200 with status ok."""
    return JsonResponse({"status": "ok"}, status=200)
