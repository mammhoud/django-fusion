"""
Context processors for django_rseal.

Provides common template context variables across all views.
"""
from django.conf import settings as django_settings


def LANGUAGES(request):
    """Inject available languages and current language into template context."""
    from django.utils import translation
    return {
        "LANGUAGES": getattr(django_settings, "LANGUAGES", []),
        "LANGUAGE_CODE": translation.get_language() or getattr(django_settings, "LANGUAGE_CODE", "en"),
    }


def COOKIES(request):
    """Inject cookie consent / cookie settings into template context."""
    return {
        "COOKIES_ACCEPTED": request.COOKIES.get("cookies_accepted", False),
    }


def AUTH_SETTINGS(request):
    """Inject auth-related settings into template context."""
    return {
        "AUTH_SETTINGS": {
            "LOGIN_URL": getattr(django_settings, "LOGIN_URL", "/accounts/login/"),
            "LOGOUT_URL": getattr(django_settings, "LOGOUT_URL", "/accounts/logout/"),
        }
    }


def CONTEXT(request):
    """Inject general site context into template context."""
    return {
        "SITE_NAME": getattr(django_settings, "SITE_NAME", ""),
        "SITE_URL": getattr(django_settings, "SITE_URL", ""),
    }


def SETTINGS(request):
    """Inject safe public settings into template context."""
    return {
        "DEBUG": getattr(django_settings, "DEBUG", False),
        "ENVIRONMENT": getattr(django_settings, "SERVER_ENV", "production"),
    }
