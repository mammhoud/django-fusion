"""
Formint — Django app config.

On ``ready()`` the formint template files under ``formint/templates/formint/``
are pre-registered as path-style components via
``django_fusion.comp.registry.register_include_paths``. This bridges the
``{% include %}`` world and the ``{% comp %}`` component registry so
fragment templates get stable component identity (and ``data-block-*``
attributes when ``COMPONENTS_ENABLE_BLOCK_ATTRS`` is enabled).
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.apps import AppConfig

logger = logging.getLogger(__name__)

# Template subdirectories (relative to ``formint/templates/``) whose *.html
# files become registered include-path components.
_REGISTER_ROOTS = ("formint",)


class FormintConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'formint'

    def ready(self) -> None:
        from django_fusion.comp.registry import register_include_paths

        templates_root = Path(__file__).resolve().parent / "templates"
        paths: list[str] = []
        for root in _REGISTER_ROOTS:
            root_dir = templates_root / root
            if not root_dir.is_dir():
                continue
            for html in sorted(root_dir.rglob("*.html")):
                paths.append(str(html.relative_to(templates_root)))

        if paths:
            try:
                registered = register_include_paths(paths)
                logger.info(
                    "formint: registered %d/%d include-path components",
                    len(registered),
                    len(paths),
                )
            except Exception as exc:  # pragma: no cover - startup guard
                logger.warning("formint: include-path registration skipped: %s", exc)
