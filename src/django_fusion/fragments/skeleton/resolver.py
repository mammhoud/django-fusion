"""SkeletonResolver — resolves skeleton placeholders for page components.

Consumes the analyzer's scanner/parser/variant-resolution pipeline and
produces ordered :class:`SkeletonEntry` lists ready for serialisation
to the frontend.

Usage from views / template tags::

    from django_fusion.fragments.skeleton.resolver import SkeletonResolver

    resolver = SkeletonResolver()
    entries = resolver.resolve_page_skeleton("pages/home.html")
    json_payload = resolver.to_json(entries)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django_fusion.fragments.analyzer.parser import parse_template
from django_fusion.fragments.analyzer.scanner import scan
from django_fusion.fragments.analyzer.schemas import Component
from django_fusion.fragments.analyzer.skeleton_view import (
    _resolve_skeleton_variant,
    _get_analyzer_options,
)


@dataclass
class SkeletonEntry:
    """One skeleton placeholder for a single component on a page."""

    variant: str
    component_path: str
    props: dict[str, Any] = field(default_factory=dict)
    skeleton_config: dict[str, Any] = field(default_factory=dict)
    order: int = 0


class SkeletonResolver:
    """Resolves which skeleton variant to show for each component on a page.

    Configuration is read from ``FUSION_ANALYZER`` (the same settings
    used by :class:`~django_fusion.fragments.analyzer.skeleton_view.SkeletonManifestView`).
    """

    def __init__(self):
        self._cfg = _get_analyzer_options()

    # ── public API ──────────────────────────────────────────────

    def resolve_page_skeleton(self, page_path: str) -> list[SkeletonEntry]:
        """Return ordered skeleton entries for *page_path*.

        *page_path* is a Django template path (e.g. ``"pages/home.html"``).
        The resolver scans ``TEMPLATES_DIRS``, parses the matching
        template, and resolves a skeleton variant for every ``{% comp %}``
        it contains.
        """
        if not self._cfg["ENABLED"]:
            return []

        normalised = self._normalise_path(page_path)
        matched = self._find_template(normalised)
        if matched is None:
            return []

        parsed = parse_template(matched.content)

        auto_detect = bool(self._cfg["SKELETON_AUTO_DETECT"])
        default_variant = str(self._cfg["SKELETON_DEFAULT_VARIANT"])

        entries: list[SkeletonEntry] = []
        seen: set[str] = set()

        for idx, usage in enumerate(parsed.comps):
            if usage.path in seen:
                continue
            seen.add(usage.path)

            comp = Component(
                name=usage.path,
                path=usage.path,
                skeleton=usage.skeleton,
                skeleton_config=usage.skeleton_config,
            )
            variant = _resolve_skeleton_variant(
                comp,
                auto_detect=auto_detect,
                default_variant=default_variant,
            )
            entries.append(
                SkeletonEntry(
                    variant=variant,
                    component_path=usage.path,
                    props=usage.kwargs or {},
                    skeleton_config=usage.skeleton_config or {},
                    order=idx,
                )
            )

        return entries

    def to_json(self, entries: list[SkeletonEntry]) -> dict[str, Any]:
        """Serialise skeleton entries for embedding as a ``<script>`` block."""
        return {
            "skeletons": [
                {
                    "variant": e.variant,
                    "component": e.component_path,
                    "order": e.order,
                    "props": e.props,
                    "skeleton_config": e.skeleton_config,
                }
                for e in entries
            ]
        }

    def resolve_component_variant(self, component_path: str) -> str:
        """Resolve the skeleton variant for a single component by its path."""
        comp = Component(name=component_path, path=component_path)
        return _resolve_skeleton_variant(
            comp,
            auto_detect=bool(self._cfg["SKELETON_AUTO_DETECT"]),
            default_variant=str(self._cfg["SKELETON_DEFAULT_VARIANT"]),
        )

    # ── internal ────────────────────────────────────────────────

    @staticmethod
    def _normalise_path(page_path: str) -> str:
        p = page_path.lstrip("/")
        if not p.endswith(".html"):
            p += ".html" if "." not in p else ""
        return p

    @staticmethod
    def _find_template(normalised: str):
        scanned = scan(
            depth=3,
            filters={},
        )
        for sf in scanned:
            if sf.relative_path == normalised:
                return sf

        # Stem fallback — only when exactly one match
        target_stem = Path(normalised).stem.lower()
        stem_matches = [sf for sf in scanned if sf.path.stem.lower() == target_stem]
        if len(stem_matches) == 1:
            return stem_matches[0]

        return None
