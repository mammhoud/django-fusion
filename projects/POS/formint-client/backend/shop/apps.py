"""
Shop — Django app config.

On ``ready()`` the shop fragment templates under ``shop/templates/shop/fragments/``
are pre-registered as path-style components via
``django_fusion.comp.registry.register_include_paths`` (mirrors formint's
``apps.py`` and precis-landing's ``apps/pages/apps.py``). This gives fragment
templates stable component identity for the ``{% comp %}`` tag.
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.apps import AppConfig

logger = logging.getLogger(__name__)

# Fragment template paths (relative to ``shop/templates/``) that become
# registered include-path components.
_REGISTER_ROOTS = ("shop/fragments",)


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
    verbose_name = "Shop — storefront, cart & orders"

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
                    "shop: registered %d/%d include-path components",
                    len(registered),
                    len(paths),
                )
            except Exception as exc:  # pragma: no cover - startup guard
                logger.warning("shop: include-path registration skipped: %s", exc)
