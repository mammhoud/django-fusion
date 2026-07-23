"""Template and component analyzer — scans the workspace for template usage.

Sub-modules
-----------
comp.analyzer.parser     Parses template files: extracts ``{% comp %}`` usages, includes,
                    and block structure into ``ParsedTemplate`` objects.
comp.analyzer.scanner    Walks directories and collects ``ScannedFile`` metadata.
comp.analyzer.schemas    Pydantic schemas for analyzer output.
comp.analyzer.views      Django views exposing analyzer results as JSON endpoints.
comp.analyzer.urls       URL configuration for the analyzer app.

Django app
----------
Add to ``INSTALLED_APPS`` to enable the ``/analyzer/`` REST endpoint::

    INSTALLED_APPS += ["django_fusion.comp.analyzer.apps.AnalyzerAppConfig"]

Usage::

    from django_fusion.comp.analyzer import parse_template, scan
    parsed = parse_template(template_string)
    files = scan(template_dirs=["/path/to/templates"])
"""

from .parser import parse_template
from .scanner import scan

__all__ = ["parse_template", "scan"]
