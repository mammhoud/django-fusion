"""
django_fusion.builder.themes
============================

Theme catalog for the landing builder.

The values are the ``data-theme`` keys of the shared theme engine
(``projects/assets/theme/``). A page stores one of these keys; the renderer
emits ``data-theme="…"`` on ``<html>`` so the active theme's ``--fu-token-*``
remap applies. ``default`` is the engine's base theme and emits no attribute.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

#: (key, label) pairs for the ``theme`` field. Keys must match the theme
#: engine's ``[data-theme]`` activation blocks.
BUILDER_THEMES = [
    ("default", _("Default")),
    ("saas", _("Modern SaaS")),
    ("enterprise", _("Enterprise")),
    ("corporate", _("Corporate")),
    ("educational", _("Educational")),
    ("retail", _("Retail")),
    ("minimal", _("Minimal")),
    ("dark", _("Dark")),
    ("contrast", _("High Contrast")),
    ("lms", _("LMS")),
    ("crm", _("CRM")),
    ("pos", _("POS")),
]

#: (key, label) pairs for the optional ``brand`` field (multi-brand support).
#: Empty key means "no brand override — use the theme's own palette".
BUILDER_BRANDS = [
    ("", _("None (theme default)")),
    ("structa", _("Structa")),
    ("precis", _("Precis")),
    ("formint", _("Formint")),
    ("loop", _("Loop")),
]

#: Theme keys that map to a real ``[data-theme]`` block (everything except
#: the base ``default`` theme).
ACTIVE_THEME_KEYS = {key for key, _ in BUILDER_THEMES if key != "default"}


def theme_choices() -> list[tuple[str, str]]:
    return list(BUILDER_THEMES)


def brand_choices() -> list[tuple[str, str]]:
    return list(BUILDER_BRANDS)


__all__ = [
    "ACTIVE_THEME_KEYS",
    "BUILDER_BRANDS",
    "BUILDER_THEMES",
    "brand_choices",
    "theme_choices",
]
