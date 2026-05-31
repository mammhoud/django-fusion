"""
Cookie Consent Management
Handles cookie preferences, detection, and storage
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta


class CookiePreferences:
    """
    Manages cookie preferences with sensible defaults
    """
    
    COOKIE_NAME = 'vresume_cookie_consent'
    COOKIE_EXPIRY_DAYS = 365
    
    # Cookie categories
    CATEGORIES = {
        'essential': {
            'name': 'Essential Cookies',
            'description': 'Required for basic site functionality. Cannot be disabled.',
            'required': True,
            'default': True,
        },
        'analytics': {
            'name': 'Analytics Cookies',
            'description': 'Help us understand how you use our site to improve your experience.',
            'required': False,
            'default': False,
        },
        'marketing': {
            'name': 'Marketing Cookies',
            'description': 'Used to track your activity and show you relevant ads.',
            'required': False,
            'default': False,
        },
        'preferences': {
            'name': 'Preference Cookies',
            'description': 'Remember your choices and settings for a better experience.',
            'required': False,
            'default': True,
        },
    }
    
    @staticmethod
    def get_default_preferences():
        """Get default cookie preferences"""
        return {
            'essential': True,
            'analytics': False,
            'marketing': False,
            'preferences': True,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
        }
    
    @staticmethod
    def parse_cookie(cookie_value):
        """Parse cookie value from JSON string"""
        try:
            return json.loads(cookie_value)
        except (json.JSONDecodeError, TypeError):
            return CookiePreferences.get_default_preferences()
    
    @staticmethod
    def serialize_preferences(preferences):
        """Serialize preferences to JSON string"""
        return json.dumps(preferences)
    
    @staticmethod
    def is_first_visit(request):
        """Check if this is the user's first visit"""
        return CookiePreferences.COOKIE_NAME not in request.COOKIES
    
    @staticmethod
    def get_preferences(request):
        """Get user's cookie preferences"""
        cookie_value = request.COOKIES.get(CookiePreferences.COOKIE_NAME)
        if cookie_value:
            return CookiePreferences.parse_cookie(cookie_value)
        return CookiePreferences.get_default_preferences()
    
    @staticmethod
    def set_preferences_response(response, preferences):
        """Set cookie preferences in response"""
        cookie_value = CookiePreferences.serialize_preferences(preferences)
        response.set_cookie(
            CookiePreferences.COOKIE_NAME,
            cookie_value,
            max_age=CookiePreferences.COOKIE_EXPIRY_DAYS * 24 * 60 * 60,
            secure=True,
            httponly=False,  # Allow JS to read for theme detection
            samesite='Lax',
        )
        return response


def get_device_theme():
    """
    Get device theme preference
    Returns: 'light', 'dark', or 'auto'
    """
    return 'auto'  # Will be detected client-side


def detect_theme_from_request(request):
    """
    Detect theme from request headers
    Checks Accept-CH header for theme preference
    """
    # Check for prefers-color-scheme in Accept-CH header
    accept_ch = request.META.get('Accept-CH', '')
    if 'prefers-color-scheme' in accept_ch:
        # Client supports theme detection
        return 'auto'
    
    # Fallback to dark theme
    return 'dark'
