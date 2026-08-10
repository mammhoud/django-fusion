"""POST /api/analyzer/ -> JsonResponse in the spec shape."""

from __future__ import annotations

import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views import View

from .parser import CompUsage, parse_template
from .post_process import enrich_pages
from .scanner import MAX_DEPTH, scan
from .schemas import (
    AnalyzeRequest,
    Block,
    Component,
    Page,
    PageComponentUsage,
    Section,
    Template,
    website_header,
)
import re as _re

logger = logging.getLogger(__name__)


def _slug(text: str) -> str:
    """Slugify a string into a URL-safe fragment.

    Used to derive stable Section ``id`` values from
    ``"<template_path_slug>--<section_name_slug>"``. Lowercases, replaces
    any non-alphanumeric run with a single dash, and strips edges so
    the slug never starts/ends with a dash.
    """
    return _re.sub(r"[\W_]+", "-", text.lower()).strip("-")


def _section_id(template_path: str, section_name: str) -> str:
    """Stable cross-commit ID for a section.

    Page/Template IDs are random UUIDs (uniqify on each request);
    Section IDs are deliberately deterministic so frontend / doc
    tooling can diff analyzer output across rebuilds.
    """
    return f"sec--{_slug(template_path)}--{_slug(section_name)}"

__all__ = ["AnalyzeView"]


def _coerce_depth(raw: object) -> int:
    """Safely coerce a payload value to a bounded depth int.

    Accepts ints and numeric strings; rejects everything else with the default.
    Floored at 1, capped at MAX_DEPTH so a malicious client cannot request a
    full / infinite filesystem walk.
    """
    try:
        depth = int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 3
    return max(1, min(depth, MAX_DEPTH))


def _coerce_bool(raw: object, default: bool) -> bool:
    """Defensive bool coercion.

    Truthy set: real bools are returned as-is. Strings in {1, true, yes, on}
    (case-insensitive, stripped) coerce to True. Ambiguous strings (not in
    the truthy set) follow their Python truthiness when default is False
    (so "any" or a non-empty label coerces to True), but fall back to
    default when default is True (so callers cannot be tricked into enabling
    features by sending arbitrary string payloads).
    """
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        stripped = raw.strip().lower()
        if stripped in {"1", "true", "yes", "on"}:
            return True
        # Ambiguous string -- when caller provided a permissive default,
        # honour it; otherwise fall back to Python's bool() so non-empty
        # strings count as truthy (matches test contract).
        return default if default else bool(raw)
    return bool(raw) if default is False else default


def _coerce_filters(raw: object) -> dict:
    """Ensure filters is a dict-shaped object even if payload is malformed."""
    if not isinstance(raw, dict):
        return {}
    out: dict = {}
    exclude = raw.get("exclude_patterns")
    if isinstance(exclude, list):
        out["exclude_patterns"] = [str(x) for x in exclude if isinstance(x, (str, int))]
    exts = raw.get("include_extensions")
    if isinstance(exts, list):
        out["include_extensions"] = [str(x) for x in exts if isinstance(x, (str, int))]
    return out


def _category_for(rel_path: str) -> str:
    parts = rel_path.split("/")
    if len(parts) >= 2:
        return parts[0].title()
    return "Misc"


def _humanize(name: str) -> str:
    return name.replace("_", " ").replace(".html", "").strip().title()


class AnalyzeView(View):
    """Accepts a POST JSON spec request and returns the analyzer JSON response."""

    http_method_names = ["post", "options"]

    def options(self, request: HttpRequest, *args, **kwargs):
        return JsonResponse({}, status=204)

    def post(self, request: HttpRequest, *args, **kwargs):
        # ── FUSION_ANALYZER master gate ──────────────────────────────
        analyzer_cfg = self._get_analyzer_cfg()
        if not analyzer_cfg.get("ENABLED", True):
            return JsonResponse(
                {
                    "status": "error",
                    "message": (
                        "Analyzer is disabled. "
                        "Set FUSION_ANALYZER['ENABLED'] = True in Django settings."
                    ),
                },
                status=503,
            )

        # Reject empty body explicitly -- otherwise `b""` would be silently
        # coerced to `{}` and the request would 200 with an empty analysis
        # (the contract the spec promises is 400 + a clear error).
        if not request.body:
            return JsonResponse(
                {"status": "error", "message": "Empty request body"},
                status=400,
            )
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError as e:
            return JsonResponse(
                {"status": "error", "message": f"Invalid JSON: {e}"},
                status=400,
            )
        if not isinstance(payload, dict):
            return JsonResponse(
                {"status": "error", "message": "Payload must be a JSON object"},
                status=400,
            )

        # Merge request payload with settings overrides.
        # Settings-supplied ANALYZE_DEPTH and ANALYZE_FILTERS act as
        # defaults — the request payload can override them.
        request_depth = payload.get("depth")
        request_filters = payload.get("filters")

        spec = AnalyzeRequest(
            website_slug=payload.get("website_slug") if isinstance(payload.get("website_slug"), str) else None,
            url=payload.get("url") if isinstance(payload.get("url"), str) else None,
            include_components=_coerce_bool(payload.get("include_components"), True),
            include_templates=_coerce_bool(payload.get("include_templates"), True),
            depth=(
                _coerce_depth(request_depth)
                if request_depth is not None
                else analyzer_cfg.get("ANALYZE_DEPTH", 3)
            ),
            filters=(
                _coerce_filters(request_filters)
                if request_filters is not None
                else analyzer_cfg.get("ANALYZE_FILTERS", {})
            ),
        )

        scanned = scan(depth=spec.depth, filters=spec.filters)

        components: dict[str, Component] = {}
        templates: list[Template] = []
        pages: list[Page] = []

        for sf in scanned:
            parsed = parse_template(sf.content)
            rel = sf.relative_path

            if spec.include_templates:
                tpl = Template(
                    name=_humanize(sf.path.name),
                    path=rel,
                    category=_category_for(rel),
                    extends=parsed.extends,
                    blocks=[Block(name=b) for b in parsed.blocks],
                    sections=[
                        Section(
                            name=marker.name,
                            id=_section_id(rel, marker.name),
                            marker_type=marker.marker_type,
                            line=marker.line,
                        )
                        for marker in parsed.sections
                    ],
                )
                templates.append(tpl)

                # Emitting one "page" per top-level template that extends base
                if parsed.extends or sf.path.name == "base.html":
                    pages.append(
                        Page(
                            title=_humanize(sf.path.name),
                            path=rel,
                            template=parsed.extends or rel,
                            components=[],
                        )
                    )

            if spec.include_components:
                for usage in parsed.comps:
                    key = usage.path
                    if key in components:
                        continue
                    components[key] = Component(
                        name=_humanize(key),
                        path=key,
                        category=_category_for(key),
                        description=f"Component referenced from {sf.relative_path}",
                        skeleton=usage.skeleton,
                        skeleton_config=usage.skeleton_config,
                    )

                    # attach usage to last page if available
                    if pages and usage.kwargs:
                        pages[-1].components.append(
                            PageComponentUsage(
                                component_id=components[key].to_dict()["id"],
                                props=usage.kwargs,
                            )
                        )

        # Phase 2 — enrich pages with webpack dependency metadata
        try:
            from django.conf import settings
            project_root = getattr(settings, "BASE_DIR", None)
        except Exception:
            project_root = None
        pages = enrich_pages(pages, project_root=project_root)

        resp = {
            "status": "success",
            "website": website_header(spec.website_slug, spec.url, spec.website_slug),
            "components": [c.to_dict() for c in components.values()],
            "templates": [t.to_dict() for t in templates],
            "pages": [p.to_dict() for p in pages],
            "summary": {
                "total_components": len(components),
                "total_templates": len(templates),
                "total_pages": len(pages),
            },
        }
        return JsonResponse(resp)

    @staticmethod
    def _get_analyzer_cfg() -> dict:
        """Return the current ``FUSION_ANALYZER`` settings dict with defaults.

        Defaults to enabled (``ENABLED: True``) for backward compatibility —
        the analyzer POST endpoint worked before the settings existed.
        When ``FUSION_ANALYZER`` IS explicitly configured, the user's
        ``ENABLED`` value is respected.
        """
        defaults: dict = {
            "ENABLED": True,
            "SKELETON_AUTO_DETECT": True,
            "SKELETON_DEFAULT_VARIANT": "line",
            "EMIT_SKELETON_MANIFEST": True,
            "CACHE_DURATION": 3600,
            "ANALYZE_DEPTH": 3,
            "ANALYZE_FILTERS": {},
        }
        try:
            from django.conf import settings
            from django_fusion.config.analyzer import AnalyzerOptions  # noqa: PLC0415

            user_configured = hasattr(settings, "FUSION_ANALYZER")
            opts = AnalyzerOptions.from_django_settings()
            return {
                # Backward compat: if FUSION_ANALYZER is not explicitly
                # configured, the POST endpoint stays enabled.
                "ENABLED": opts.enabled if user_configured else True,
                "SKELETON_AUTO_DETECT": opts.skeleton_auto_detect,
                "SKELETON_DEFAULT_VARIANT": opts.skeleton_default_variant,
                "EMIT_SKELETON_MANIFEST": opts.emit_skeleton_manifest,
                "CACHE_DURATION": opts.cache_duration,
                "ANALYZE_DEPTH": opts.analyze_depth,
                "ANALYZE_FILTERS": opts.analyze_filters,
            }
        except Exception:
            return defaults
