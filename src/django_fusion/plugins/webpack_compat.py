# ============================================================
# Webpack Loader Compatibility Patch
# ============================================================
# django-webpack-loader v3.2.3 expects flat-string chunks but
# webpack-bundle-tracker v3+ outputs dict chunks like
# {"name": "foo.js", "path": "...", "url": "..."}, causing:
#   TypeError: expected string or bytes-like object, got 'dict'
# in filter_chunks.
#
# This module monkey-patches WebpackLoader at import time so all
# sites that load django-fusion benefit without duplicating the
# fix. The patch is invoked from ``CoreExtAppConfig.ready()``
# (see ``django_fusion/comp/apps.py``).
#
# Settings:
#   STATS_FILE is read dynamically from ``self.config["STATS_FILE"]``
#   inside ``_patched_load_assets`` so each site can override the
#   stats file path via its own ``WEBPACK_LOADER`` config block.
# ============================================================
from __future__ import annotations

from typing import Any


def _patch_webpack_loader() -> bool:
    """Patch django-webpack-loader's WebpackLoader to handle dict/string chunks.

    Returns True if the patch was applied, False if django-webpack-loader
    is not importable (e.g. dev env without it). Idempotent: safe to call
    multiple times — the ``_patched`` sentinel short-circuits re-entry.
    """
    try:
        from webpack_loader.loaders import WebpackLoader
        import webpack_loader.utils
    except ImportError:
        return False

    # Guard BEFORE any rebindings so re-imports don't partially re-patch
    # (e.g. re-bind _filter_by_extension but not the load_assets closure
    # that captured _bundles_json only once at import time).
    if hasattr(WebpackLoader, "_patched"):
        return True

    def _patched_filter_chunks(self: Any, chunks: list | None) -> list:
        filtered_chunks: list = []
        for chunk in (chunks or []):
            # Normalise string chunks to dict form so downstream code
            # that accesses chunk['name'] / chunk['url'] works correctly.
            if isinstance(chunk, str):
                chunk = {"name": chunk, "url": chunk}
            chunk_name = chunk.get("name", "") or ""
            ignore = any(
                regex.match(chunk_name) for regex in self.config["ignores"]
            )
            if not ignore:
                filtered_chunks.append(chunk)
        return filtered_chunks

    def _patched_filter_by_extension(bundle: list, extension: str) -> list:
        # _filter_by_extension expects dict chunks with ['name'], but
        # webpack-bundle-tracker may output plain string chunks.
        result: list = []
        for chunk in bundle:
            chunk_name = chunk["name"] if isinstance(chunk, dict) else chunk
            if chunk_name.endswith(f".{extension}"):
                result.append(chunk)
        return result

    def _patched_load_assets(self: Any) -> dict:
        # Read the stats file path directly from this loader's config
        # (which Django populates from WEBPACK_LOADER[<bundle>]["STATS_FILE"]).
        # This makes the patch per-site correct without relying on a
        # module-level closure capture.
        import json as _json

        _stats_file = self.config.get("STATS_FILE")
        if not _stats_file:
            raise IOError(
                "WebpackLoader config is missing STATS_FILE. "
                "Set WEBPACK_LOADER['DEFAULT']['STATS_FILE'] in settings."
            )

        try:
            with open(_stats_file, encoding="utf-8") as f:
                stats = _json.load(f)
        except IOError:
            raise IOError(
                "Error reading {0}. Are you sure webpack has generated "
                "the file and the path is correct?".format(_stats_file)
            )

        # Older webpack-bundle-tracker (<2.x) wrote ``{"status": "done",
        # "assets": {...}}``; newer versions write ``{"status": "done",
        # "chunks": {...}}``. Normalise the legacy key so the rest of the
        # pipeline only has to know about ``chunks``. Only rename when the
        # legacy value is actually a dict — otherwise the rename would
        # overwrite a missing/empty ``chunks`` with garbage and produce a
        # less-informative crash downstream.
        if (
            isinstance(stats, dict)
            and isinstance(stats.get("assets"), dict)
            and "chunks" not in stats
        ):
            stats["chunks"] = stats.pop("assets")

        # Normalise string chunks to dicts at the source so every downstream
        # caller (``utils.get_as_url_to_tag_dict``, ``filter_chunks``,
        # ``_filter_by_extension``) can safely do ``chunk['name']`` /
        # ``chunk['url']``. The ``url`` is built from BUNDLE_DIR_NAME so the
        # browser requests the correct path under STATIC_URL.
        if isinstance(stats, dict) and isinstance(stats.get("chunks"), dict):
            bundle_dir = self.config.get("BUNDLE_DIR_NAME", "") or ""
            for bundle_name, chunks in stats["chunks"].items():
                stats["chunks"][bundle_name] = [
                    {"name": c, "url": f"{bundle_dir}{c}", "path": c}
                    if isinstance(c, str) else c
                    for c in (chunks or [])
                ]
        return stats

    # ── get_bundle patch (critical — the chokepoint for ALL template rendering) ──
    # In django-webpack-loader v3.2.3, `get_bundle()` accesses `self._assets`
    # directly and does NOT call `get_assets()`.  That means the `get_assets`
    # patch above is dead code when CACHE=True — the cached data with raw
    # string chunks flows straight into `_get_bundle` → `_filter_by_extension`.
    #
    # By intercepting `get_bundle()` (the single chokepoint that every
    # `{% render_bundle %}` call eventually hits), we guarantee that every
    # downstream consumer (``filter_chunks``, ``_filter_by_extension``,
    # ``get_as_url_to_tag_dict``) receives dict-form chunks with ``name``,
    # ``url`` and ``path`` keys.
    if not hasattr(WebpackLoader, "get_bundle"):
        # Future compatibility: if get_bundle is renamed or removed,
        # fall through to the get_assets patch below.
        pass
    else:
        _original_get_bundle = WebpackLoader.get_bundle

        def _patched_get_bundle(self: Any, bundle_name: str) -> list:
            chunks = _original_get_bundle(self, bundle_name)
            # Normalise each chunk in the returned list.  String chunks (produced
            # by webpack-bundle-tracker v3+) become dicts; dict chunks get their
            # URL rewritten to include the /static/ prefix so they match the
            # Nginx shared-media server path.
            bundle_dir = self.config.get("BUNDLE_DIR_NAME", "") or ""
            result: list = []
            for c in chunks or []:
                if isinstance(c, str):
                    result.append({"name": c, "url": f"{bundle_dir}{c}", "path": c})
                else:
                    # Dict chunks from webpack-bundle-tracker v3+ have a 'url'
                    # field that may not include the /static/ prefix even though
                    # publicPath in bundles.json says /static/bundles/...  Rebuild
                    # the URL using BUNDLE_DIR_NAME to guarantee correctness.
                    name = c.get("name", "") or ""
                    c = dict(c)
                    c["url"] = f"{bundle_dir}{name}"
                    result.append(c)
            return result

        WebpackLoader.get_bundle = _patched_get_bundle

    # Also keep get_assets / load_assets / filter_chunks patches so that
    # any code path that DOES go through those methods also gets normalized
    # data.  (Belt-and-suspenders.)
    _original_get_assets = WebpackLoader.get_assets

    def _patched_get_assets(self: Any) -> dict:
        assets = _original_get_assets(self)
        if isinstance(assets, dict) and isinstance(assets.get("chunks"), dict):
            bundle_dir = self.config.get("BUNDLE_DIR_NAME", "") or ""
            for bundle_name, chunks in assets["chunks"].items():
                assets["chunks"][bundle_name] = [
                    {"name": c, "url": f"{bundle_dir}{c}", "path": c}
                    if isinstance(c, str) else c
                    for c in (chunks or [])
                ]
        return assets

    WebpackLoader.get_assets = _patched_get_assets

    # Bind the patched filter onto the module (legacy safety) AND onto the
    # class so that the class-bound call site (self._filter_by_extension(...))
    # picks it up.
    webpack_loader.utils._filter_by_extension = _patched_filter_by_extension
    WebpackLoader._filter_by_extension = _patched_filter_by_extension
    WebpackLoader.load_assets = _patched_load_assets
    WebpackLoader.filter_chunks = _patched_filter_chunks
    WebpackLoader._patched = True
    return True
