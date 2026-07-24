"""Template and component analyzer — scans the workspace for template usage.

Sub-modules
-----------
fragments.analyzer.parser     Parses template files: extracts ``{% comp %}`` usages, includes,
                         and block structure into ``ParsedTemplate`` objects.
fragments.analyzer.scanner    Walks directories and collects ``ScannedFile`` metadata.
fragments.analyzer.schemas    Pydantic schemas for analyzer output.
fragments.analyzer.views      Django views exposing analyzer results as JSON endpoints.
fragments.analyzer.urls       URL configuration for the analyzer app.

Django app
----------
Add to ``INSTALLED_APPS`` to enable the ``/analyzer/`` REST endpoint::

    INSTALLED_APPS += ["django_fusion.fragments.analyzer.apps.AnalyzerAppConfig"]

Usage::

    from django_fusion.fragments.analyzer import parse_template, scan
    parsed = parse_template(template_string)
    files = scan(template_dirs=["/path/to/templates"])
"""

from .parser import parse_template
from .scanner import scan

__all__ = ["parse_template", "scan"]
