"""ComponentAssetMap — maps component template paths to their webpack chunks.

Consumes webpack-bundle-tracker stats (``bundles.json``) and produces
per-component JS/CSS dependency lists for lazy-loading.

Usage::

    from django_fusion.core.assets.component_map import ComponentAssetMap

    asset_map = ComponentAssetMap()
    entry = asset_map.get_component_assets("blocks/hero.html")
    # → {"css": ["/static/bundles/hero.css"], "js": ["/static/bundles/hero.js"]}
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ComponentAssetEntry:
    """Asset dependencies for a single component."""

    component_path: str
    css_deps: list[str] = field(default_factory=list)
    js_deps: list[str] = field(default_factory=list)
    vendor_deps: list[str] = field(default_factory=list)
    size_bytes: int = 0
    preload: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component_path,
            "css": self.css_deps,
            "js": self.js_deps,
            "vendor": self.vendor_deps,
            "size_bytes": self.size_bytes,
            "preload": self.preload,
        }


# ── helpers (reuse from post_process for consistency) ────────────────


def _find_webpack_stats(project_root: Path | str | None = None) -> Path | None:
    """Locate the webpack stats file (bundles.json or webpack-stats.json)."""
    candidates: list[Path] = []
    root = Path(project_root) if project_root else Path(".")

    candidates.extend([
        root / "static" / "bundles" / "bundles.json",
        root / "static" / "webpack-stats.json",
        root / "webpack-stats.json",
        root / "frontend" / "dist" / "webpack-stats.json",
    ])

    try:
        from django.conf import settings
        static_root = getattr(settings, "STATIC_ROOT", None)
        if static_root:
            candidates.append(Path(static_root) / "webpack-stats.json")
            candidates.append(Path(static_root) / "bundles" / "bundles.json")
    except Exception:
        pass

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _load_webpack_chunks(stats_path: Path | str) -> dict[str, list[dict[str, Any]]]:
    """Parse webpack stats into {entry_name: [{name, url, path}, ...]}.

    Handles legacy ``{\"assets\": {...}}`` and modern ``{\"chunks\": {...}}``
    formats, normalising string entries to dict form.
    """
    sp = Path(stats_path)
    try:
        payload = json.loads(sp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.info("Webpack stats unavailable at %s: %s", sp, exc)
        return {}

    result: dict[str, list[dict[str, Any]]] = {}
    chunks = payload.get("chunks", {}) if isinstance(payload, dict) else {}
    if not isinstance(chunks, dict):
        chunks = {}

    if not chunks and isinstance(payload, dict) and isinstance(payload.get("assets"), dict):
        chunks = payload["assets"]

    for bundle_name, entries in chunks.items():
        normalised: list[dict[str, Any]] = []
        for entry in (entries if isinstance(entries, list) else []):
            if isinstance(entry, dict):
                normalised.append(entry)
            elif isinstance(entry, str):
                normalised.append({"name": entry, "url": entry})
        if normalised:
            result[bundle_name] = normalised

    return result


# ── ComponentAssetMap ────────────────────────────────────────────────


class ComponentAssetMap:
    """Maps component template paths to their webpack JS/CSS chunks.

    Constructed from a webpack-bundle-tracker stats file.  Provides
    per-component lookups and page-level aggregation for lazy-loading.
    """

    def __init__(self, stats_path: Path | str | None = None):
        self._stats_path: Path | None = (
            Path(stats_path) if stats_path else _find_webpack_stats()
        )
        self._chunks: dict[str, list[dict[str, Any]]] = {}
        self._by_component: dict[str, list[str]] = {}
        self._entries: dict[str, ComponentAssetEntry] = {}

        if self._stats_path:
            self._chunks = _load_webpack_chunks(self._stats_path)
            self._build_index()

    # ── public API ──────────────────────────────────────────────

    def get_component_assets(self, component_path: str) -> ComponentAssetEntry | None:
        """Return CSS/JS dependencies for a single component path.

        ``component_path`` is a template path like ``"blocks/hero.html"``.
        """
        return self._entries.get(component_path)

    def get_page_assets(self, component_paths: list[str]) -> dict[str, Any]:
        """Return the minimal merged CSS/JS chunk set for a page's components."""
        css: list[str] = []
        js: list[str] = []
        seen_css: set[str] = set()
        seen_js: set[str] = set()

        for comp_path in component_paths:
            entry = self._entries.get(comp_path)
            if entry is None:
                continue
            for url in entry.css_deps:
                if url not in seen_css:
                    seen_css.add(url)
                    css.append(url)
            for url in entry.js_deps:
                if url not in seen_js:
                    seen_js.add(url)
                    js.append(url)

        return {"css": css, "js": js, "components": component_paths}

    def get_all_components(self) -> dict[str, dict[str, Any]]:
        """Return the full component→chunk map for API serialisation."""
        return {k: v.to_dict() for k, v in self._entries.items()}

    def to_manifest(self) -> dict[str, Any]:
        """Serializable manifest for ``window.__FUSION_COMPONENT_ASSETS__``."""
        return {
            "components": {
                k: v.to_dict() for k, v in self._entries.items()
            }
        }

    # ── internal ────────────────────────────────────────────────

    def _build_index(self):
        """Build the component→chunk reverse-lookup from webpack entries."""
        # Map component paths to their matching webpack bundle names
        for bundle_name, chunk_entries in self._chunks.items():
            # Try to match the bundle name to a component path
            comp_path = self._bundle_to_component(bundle_name)
            if comp_path:
                css: list[str] = []
                js: list[str] = []
                for entry in chunk_entries:
                    url = entry.get("url", entry.get("name", ""))
                    name = entry.get("name", "")
                    if not url:
                        continue
                    suffix = Path(name.split("?", 1)[0]).suffix.lower() if name else ""
                    if suffix == ".css":
                        css.append(url)
                    elif suffix == ".js":
                        js.append(url)
                    else:
                        js.append(url)

                self._entries[comp_path] = ComponentAssetEntry(
                    component_path=comp_path,
                    css_deps=css,
                    js_deps=js,
                    preload=self._is_critical_bundle(bundle_name),
                )

    @staticmethod
    def _bundle_to_component(bundle_name: str) -> str | None:
        """Try to map a webpack entry name back to a component template path.

        E.g. ``\"blocks_hero\"`` → ``\"blocks/hero.html\"``.
        """
        if bundle_name in ("main", "runtime", "vendor", "vendors", "common"):
            return None

        # Replace underscores with slashes, add .html extension
        candidate = bundle_name.replace("_", "/") + ".html"
        # Basic validation: should look like a template path
        if "/" in candidate:
            return candidate
        return None

    @staticmethod
    def _is_critical_bundle(bundle_name: str) -> bool:
        """Heuristic: hero/header/nav bundles are critical (above-the-fold)."""
        critical = {"hero", "header", "nav", "navbar", "masthead"}
        return any(kw in bundle_name.lower() for kw in critical)
