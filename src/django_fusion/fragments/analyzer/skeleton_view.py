"""GET /api/analyzer/skeleton/{page_path}/ — per-page skeleton manifest.

Returns the ordered skeleton entries for a single page template so the
frontend can render skeleton placeholders before real content arrives.

.. code-block:: json

    {
      "status": "success",
      "page": {
        "title": "Home",
        "path": "pages/home.html",
        "components": [
          {"variant": "hero-section", "component": "blocks/hero.html",
           "order": 0, "props": {}},
          {"variant": "stats-row", "component": "sections/stats.html",
           "order": 1, "props": {}}
        ]
      }
    }

The ``variant`` is resolved in order:

1. Explicit ``{# @skeleton: <name> #}`` comment annotations.
2. Naming-convention fallback (e.g. ``blocks/hero.html`` → ``"hero-section"``)
   — enabled via ``FUSION_ANALYZER["SKELETON_AUTO_DETECT"]``.
3. Default fallback (``"line"``) — controlled via
   ``FUSION_ANALYZER["SKELETON_DEFAULT_VARIANT"]``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views import View

from .parser import parse_template
from .scanner import scan
from .schemas import Component


def _humanize(name: str) -> str:
    """Convert a dotted/snake-case name to a readable title."""
    return name.replace("_", " ").replace(".html", "").strip().title()

logger = logging.getLogger(__name__)

# ── naming-convention skeleton mapping (Priority 2) ────────────────────
_NAME_TO_VARIANT: dict[str, str] = {
    "hero": "hero-section",
    "stats": "stats-row",
    "features": "features-grid",
    "testimonial": "testimonial",
    "testimonials": "testimonials-carousel",
    "pricing": "pricing-grid",
    "faq": "faq-list",
    "cta": "cta-banner",
    "contact": "contact-form",
    "team": "team-grid",
    "blog": "blog-grid",
    "timeline": "timeline",
    "section-header": "section-header",
    "card": "card",
}

# ── path-directory → default variant (Priority 3) ─────────────────────
_CATEGORY_DEFAULT: dict[str, str] = {
    "components": "card",
    "layout": "line",
}


def _resolve_skeleton_variant(
    component: Component,
    *,
    auto_detect: bool = True,
    default_variant: str = "line",
) -> str:
    """Resolve the skeleton variant for a component using three priorities.

    Priority 1: explicit skeleton field (set by parser from comment annotations).
    Priority 2: naming-convention pattern matching (requires ``auto_detect``).
    Priority 3: path-directory-based default, then Component.category, then
                the global *default_variant*.
    """
    # Priority 1 — explicit skeleton from comment or component metadata
    if component.skeleton:
        return component.skeleton

    if not auto_detect:
        return default_variant

    # Priority 2 — naming convention.
    # Match the component path stem ("hero" from "blocks/hero.html"),
    # the parent directory name ("blocks"), or the composite slug
    # ("blocks_hero").
    stem = Path(component.path).stem.lower()
    dir_part = Path(component.path).parent.name.lower()

    # Check longest keys first so e.g. "testimonials" matches before
    # "testimonial" when processing a stem like "testimonials".
    for name, variant in sorted(
        _NAME_TO_VARIANT.items(), key=lambda kv: -len(kv[0])
    ):
        if name in stem or name in dir_part or f"{dir_part}_{stem}" == name:
            return variant

    # Priority 3 — path-directory → category default
    dir_cat = Path(component.path).parent.name.lower() if component.path else ""
    if dir_cat in _CATEGORY_DEFAULT:
        return _CATEGORY_DEFAULT[dir_cat]
    if component.category.lower() in _CATEGORY_DEFAULT:
        return _CATEGORY_DEFAULT[component.category.lower()]

    return default_variant


def _get_analyzer_options() -> dict[str, Any]:
    """Return the current ``FUSION_ANALYZER`` settings as a dict.

    Delegates to :class:`~django_fusion.config.analyzer.AnalyzerOptions`
    when Django is configured; falls back to hard-coded defaults otherwise.
    """
    defaults: dict[str, Any] = {
        "ENABLED": False,
        "SKELETON_AUTO_DETECT": True,
        "SKELETON_DEFAULT_VARIANT": "line",
        "EMIT_SKELETON_MANIFEST": True,
        "CACHE_DURATION": 3600,
        "ANALYZE_DEPTH": 3,
        "ANALYZE_FILTERS": {},
    }
    try:
        from django_fusion.config.analyzer import AnalyzerOptions  # noqa: PLC0415

        opts = AnalyzerOptions.from_django_settings()
        return {
            "ENABLED": opts.enabled,
            "SKELETON_AUTO_DETECT": opts.skeleton_auto_detect,
            "SKELETON_DEFAULT_VARIANT": opts.skeleton_default_variant,
            "EMIT_SKELETON_MANIFEST": opts.emit_skeleton_manifest,
            "CACHE_DURATION": opts.cache_duration,
            "ANALYZE_DEPTH": opts.analyze_depth,
            "ANALYZE_FILTERS": opts.analyze_filters,
        }
    except Exception:
        return defaults


class SkeletonManifestView(View):
    """Return the skeleton manifest for a single page template path.

    Configurable via ``FUSION_ANALYZER`` Django setting.
    """

    http_method_names = ["get", "head", "options"]

    def options(self, request: HttpRequest, *args, **kwargs):
        return JsonResponse({}, status=204)

    def get(self, request: HttpRequest, page_path: str, *args, **kwargs):
        analyzer_cfg = _get_analyzer_options()

        if not analyzer_cfg["ENABLED"]:
            return JsonResponse(
                {
                    "status": "error",
                    "message": (
                        "Analyzer skeleton endpoint is disabled. "
                        "Set FUSION_ANALYZER['ENABLED'] = True in Django settings."
                    ),
                },
                status=503,
            )

        # Delegate to SkeletonResolver (Phase 2.1) for the actual
        # scan → parse → resolve → serialise pipeline.
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver  # noqa: PLC0415

        resolver = SkeletonResolver()
        entries = resolver.resolve_page_skeleton(page_path)

        if not entries:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"No components or template not found: {page_path}",
                },
                status=404,
            )

        payload = resolver.to_json(entries)
        resp: dict[str, Any] = {
            "status": "success",
            "page": {
                "title": _humanize(Path(page_path).stem),
                "path": resolver._normalise_path(page_path),
                "components": payload["skeletons"],
            },
            "meta": {
                "auto_detect": analyzer_cfg["SKELETON_AUTO_DETECT"],
                "default_variant": analyzer_cfg["SKELETON_DEFAULT_VARIANT"],
            },
        }
        return JsonResponse(resp)
