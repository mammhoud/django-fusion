"""
VResume Core Views
Handles cookie consent, theme switching, and other core functionality
"""

import json
import os

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .cookies import CookiePreferences


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Docker / load-balancer probes.
    Returns 200 OK when the app and database are reachable.
    """
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "degraded", "db": db_ok}, status=status)


@require_http_methods(["GET"])
def media_health_check(request):
    """
    Health endpoint to verify media settings and access for troubleshooting.
    """
    try:
        media_root = settings.MEDIA_ROOT
        media_url = settings.MEDIA_URL
        media_root_exists = os.path.isdir(media_root)
        return JsonResponse(
            {
                "status": "ok",
                "media_url": media_url,
                "media_root": media_root,
                "media_root_exists": media_root_exists,
            },
            status=200,
        )
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "message": str(exc)},
            status=500,
        )


@require_http_methods(["POST"])
@csrf_exempt
def set_cookie_preferences(request):
    """
    API endpoint to set cookie preferences
    Expects JSON: {
        "essential": true,
        "analytics": false,
        "marketing": false,
        "preferences": true
    }
    """
    try:
        data = json.loads(request.body)

        # Validate preferences
        preferences = {
            'essential': data.get('essential', True),  # Always true
            'analytics': data.get('analytics', False),
            'marketing': data.get('marketing', False),
            'preferences': data.get('preferences', True),
            'timestamp': data.get('timestamp', None),
            'version': '1.0',
        }

        # Create response
        response = JsonResponse({
            'status': 'success',
            'message': 'Cookie preferences saved',
            'preferences': preferences,
        })

        # Set cookie
        response = CookiePreferences.set_preferences_response(response, preferences)

        return response

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON',
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_cookie_preferences(request):
    """
    API endpoint to get current cookie preferences
    """
    preferences = CookiePreferences.get_preferences(request)
    is_first_visit = CookiePreferences.is_first_visit(request)

    return JsonResponse({
        'status': 'success',
        'preferences': preferences,
        'is_first_visit': is_first_visit,
        'categories': CookiePreferences.CATEGORIES,
    })


@require_http_methods(["POST"])
@csrf_exempt
def set_theme(request):
    """
    API endpoint to set user's theme preference
    Expects JSON: {"theme": "classic-dark"}
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'classic-dark')

        # Validate theme
        valid_themes = ['classic-light', 'classic-dark', 'ocean-light', 'ocean-dark']
        if theme not in valid_themes:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid theme. Must be one of: {", ".join(valid_themes)}',
            }, status=400)

        response = JsonResponse({
            'status': 'success',
            'message': 'Theme preference saved',
            'theme': theme,
        })

        # Set theme cookie (1 year expiry)
        response.set_cookie(
            'vresume_theme',
            theme,
            max_age=365 * 24 * 60 * 60,
            secure=True,
            httponly=False,
            samesite='Lax',
        )

        return response

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON',
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@require_http_methods(["GET"])
def get_theme(request):
    """
    API endpoint to get current theme preference
    """
    theme = request.COOKIES.get('vresume_theme', 'classic-dark')

    return JsonResponse({
        'status': 'success',
        'theme': theme,
    })


@require_http_methods(["GET"])
def get_csrf_token(request):
    """
    API endpoint to get CSRF token
    """
    token = get_token(request)
    return JsonResponse({
        'status': 'success',
        'csrf_token': token,
    })
