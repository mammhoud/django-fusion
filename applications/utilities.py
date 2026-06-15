"""Shared utilities for the workspace website projects."""

from django.conf import settings
from django.urls import path
from django.views.generic import RedirectView

try:
    from django_osoul.site.utils import (
        bytes_to_mib,
        file_generate_local_upload_url,
        file_generate_name,
        file_generate_upload_path,
        get_files_from_dirs,
        unique_ordered,
        viewprop,
    )
except ImportError:  # pragma: no cover
    # Fallback: the shared helpers are optional outside of django-osoul / django-rseal contexts.
    bytes_to_mib = None
    file_generate_local_upload_url = None
    file_generate_name = None
    file_generate_upload_path = None
    get_files_from_dirs = None
    unique_ordered = None
    viewprop = None


def get_default_language():
    """Extract the primary language code from settings."""
    if hasattr(settings, "LANGUAGE_CODE"):
        return settings.LANGUAGE_CODE.split("-")[0]
    return "en"


def get_root_redirect_pattern():
    """Generate the root path redirect pattern for language prefixes."""
    default_language = get_default_language()
    return path("", RedirectView.as_view(url=f"/{default_language}/", permanent=False))
