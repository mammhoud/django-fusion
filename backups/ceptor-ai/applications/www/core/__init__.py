"""Shared ``www.core`` package — moved from per-site duplicates.

Historically, ``applications/ctc-research/www/projects/`` and
``applications/lms-demo/www/projects/`` carried near-mirror copies of the
same app config, email service, and redirect view. They now live here
so the sites only differ in their site-specific pages, models, and
plugins.
"""

from __future__ import annotations

__all__: list[str] = []
