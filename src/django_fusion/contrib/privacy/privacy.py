"""
Privacy Policy utilities for django_fusion.

This module provides utilities for loading, caching, and rendering
privacy policy content from markdown files.

Functions:
    get_privacy_html: Load and render privacy_policy.md from BASE_DIR.

The module uses file mtime for cache invalidation and provides a
fallback default message if the privacy policy file is missing.

Usage::

    from django_fusion.contrib.privacy.privacy import get_privacy_html
    html = get_privacy_html()
"""

import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)

_cached_html = None
_cached_mtime = 0


def get_privacy_html():
    """
    Load and render privacy_policy.md from BASE_DIR.
    Uses file mtime for cache invalidation.
    Falls back to a minimal default if file is missing.
    """
    global _cached_html, _cached_mtime

    md_path = os.path.join(settings.BASE_DIR, "privacy_policy.md")

    if not os.path.exists(md_path):
        logger.warning(f"[Privacy] privacy_policy.md not found at {md_path}")
        return "<p>Privacy policy content is being prepared. Please check back later.</p>"

    mtime = os.path.getmtime(md_path)
    if _cached_html and mtime == _cached_mtime:
        return _cached_html

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        # Try to use markdown library
        try:
            import markdown
            html = markdown.markdown(md_text, extensions=["extra", "toc"])
        except ImportError:
            # Fallback: basic conversion without markdown lib
            import re
            html = md_text.replace("\n\n", "</p><p>")
            html = re.sub(r"^# (.+)$", r"<h1></h1>", html, flags=re.MULTILINE)
            html = re.sub(r"^## (.+)$", r"<h2></h2>", html, flags=re.MULTILINE)
            html = re.sub(r"^### (.+)$", r"<h3></h3>", html, flags=re.MULTILINE)
            html = re.sub(r"\*\*(.+?)\*\*", r"<strong></strong>", html)
            html = f"<p>{html}</p>"

        _cached_html = html
        _cached_mtime = mtime
        return html

    except Exception as e:
        logger.error(f"[Privacy] Failed to render privacy_policy.md: {e}", exc_info=True)
        return "<p>An error occurred loading the privacy policy.</p>"
