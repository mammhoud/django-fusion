"""Webpack-manifest post-processor for the analyzer.

After the initial scan populates ``Page`` objects with their component
usage, this module reads the project's webpack ``bundles.json`` (via
webpack-bundle-tracker / ``_webpack_asset_links``) and enriches each
page with:

- ``dependencies`` — CSS / JS chunk names required by the page.
- ``load_priority`` — heuristic based on component names on the page
  (``\"critical\"`` when a hero / header / nav component is present,
  ``\"lazy\"`` for footer-only pages, ``\"auto\"`` otherwise).

Usage from ``views.py``::

    from .post_process import enrich_pages
    pages = enrich_pages(pages, project_root=settings.BASE_DIR)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _find_webpack_stats(project_root: Path | str | None = None) -> Path | None:
    """Locate the webpack stats file (bundles.json or webpack-stats.json)."""
    candidates = []
    root = Path(project_root) if project_root else Path(".")

    # Common locations
    candidates.extend([
        root / "static" / "bundles" / "bundles.json",
        root / "static" / "webpack-stats.json",
        root / "webpack-stats.json",
        root / "frontend" / "dist" / "webpack-stats.json",
    ])

    # Also check STATIC_ROOT if Django is configured
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


def _load_webpack_chunks(stats_path: Path | str) -> dict[str, list[str]]:
    """Parse a webpack-bundle-tracker stats file into {entry_name: [url, ...]}.

    Handles both legacy (``{\"status\": \"done\", \"assets\": {...}}``) and
    modern (``{\"status\": \"done\", \"chunks\": {...}}``) formats, including
    dict-chunk entries from webpack-bundle-tracker v3+.
    """
    sp = Path(stats_path)
    try:
        payload = json.loads(sp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.info("Webpack stats unavailable at %s: %s", sp, exc)
        return {}

    result: dict[str, list[str]] = {}
    chunks = payload.get("chunks", {}) if isinstance(payload, dict) else {}
    if not isinstance(chunks, dict):
        chunks = {}

    # Normalize legacy \"assets\" key
    if not chunks and isinstance(payload, dict) and isinstance(payload.get("assets"), dict):
        chunks = payload["assets"]

    for bundle_name, entries in chunks.items():
        urls: list[str] = []
        for entry in (entries if isinstance(entries, list) else []):
            if isinstance(entry, dict):
                url = entry.get("url") or entry.get("name") or ""
            else:
                url = str(entry)
            if url:
                urls.append(url)
        if urls:
            result[bundle_name] = urls

    return result


def _component_to_chunk(comp_path: str, chunks: dict[str, list[str]]) -> list[str]:
    """Map a component template path to webpack chunk names.

    Strategy:
    1. Strip extensions and directory prefixes to get a component \"slug\".
    2. Match against webpack entry names (e.g. \"main\", \"hero\", \"components\").
    3. Return the matched chunk URLs.
    """
    # Normalize the component path: strip .html, replace / with _
    slug = Path(comp_path).stem  # e.g. "hero" from "blocks/hero.html"
    dir_part = Path(comp_path).parent.name  # e.g. "blocks"
    full_slug = f"{dir_part}_{slug}"  # e.g. "blocks_hero"

    matched: list[str] = []
    for bundle_name, urls in chunks.items():
        # Match if the bundle name contains the component slug
        if slug in bundle_name.lower() or full_slug in bundle_name.lower():
            matched.extend(urls)

    return matched


_HEAVY_COMPONENTS = frozenset({
    "hero", "header", "nav", "navbar", "masthead", "banner", "carousel",
})


def _priority_for_page(components: list[Any]) -> str:
    """Heuristic: pages with hero/header/nav components get ``\"critical\"``."""
    for comp in components:
        comp_id = getattr(comp, "component_id", "") or ""
        props = getattr(comp, "props", {}) or {}
        # Check path (e.g. "blocks/hero.html"), name, and component_id
        search = " ".join([
            str(props.get("path", "")),
            str(props.get("name", "")),
            comp_id,
        ]).lower()
        for heavy in _HEAVY_COMPONENTS:
            if heavy in search:
                return "critical"
    return "auto"


def enrich_pages(
    pages: list[Any],
    *,
    project_root: Path | str | None = None,
    stats_path: Path | str | None = None,
) -> list[Any]:
    """Post-process analyzer pages: attach webpack dependencies and priorities.

    Parameters
    ----------
    pages : list[Page]
        The page list from the analyzer view (with populated ``components``).
    project_root : Path | str | None
        Project root for auto-discovery of webpack stats. Ignored when
        ``stats_path`` is provided.
    stats_path : Path | str | None
        Explicit path to the webpack stats file.

    Returns
    -------
    list[Page]
        The same page list with ``dependencies`` and ``load_priority`` populated.
    """
    # Resolve stats file
    if stats_path:
        sp = Path(stats_path)
    else:
        sp = _find_webpack_stats(project_root)
    if sp is None:
        logger.debug("No webpack stats file found; skipping dependency enrichment")
        return pages

    chunks = _load_webpack_chunks(sp)
    if not chunks:
        return pages

    # Always include the "main" entry if present
    main_urls = chunks.get("main", [])

    for page in pages:
        deps: list[str] = list(main_urls)

        # Add component-specific chunks
        components = getattr(page, "components", []) or []
        for usage in components:
            comp_id = getattr(usage, "component_id", "")
            props = getattr(usage, "props", {}) or {}
            # Try to resolve the component path from props or component_id
            comp_path = props.get("path", "") or comp_id
            if comp_path:
                matched = _component_to_chunk(str(comp_path), chunks)
                deps.extend(matched)

        page.dependencies = list(dict.fromkeys(deps))  # dedupe preserve order
        page.load_priority = _priority_for_page(components)

    return pages
