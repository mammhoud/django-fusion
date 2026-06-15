"""
General utilities and helper functions.

This module contains common utility functions used across the application,
including URL helpers, settings utilities, and other general-purpose helpers.
"""

from django.conf import settings
from django.urls import path
from django.views.generic import RedirectView


def get_default_language():
    """Extract the primary language code from settings."""
    if hasattr(settings, 'LANGUAGE_CODE'):
        return settings.LANGUAGE_CODE.split('-')[0]
    return 'en'


def get_root_redirect_pattern():
    """Generate the root path redirect pattern for language prefixes."""
    default_language = get_default_language()
    return path(
        "",
        RedirectView.as_view(
            url=f"/{default_language}/",
            permanent=False
        )
    )
