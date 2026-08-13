"""Canonical asset-pipeline options for django-fusion.

The options object is the single runtime contract between Django settings,
webpack output, component manifests, API views, and template tags. It keeps
source assets, generated webpack bundles, and ``collectstatic`` output as
separate filesystem roots while allowing their public links to be merged.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings

from django_fusion.config.conf import resolve_render_first_setting


def _pipeline_settings() -> dict[str, Any]:
    """Return the ``FUSION_PIPELINE`` dict (old ``FUSION_ASSET_PIPELINE`` name accepted)."""
    configured = getattr(settings, "FUSION_PIPELINE", None)
    if configured is None:
        configured = getattr(settings, "FUSION_ASSET_PIPELINE", {})
    return deepcopy(configured or {})


@dataclass(frozen=True, slots=True)
class AssetPipelineOptions:
    """Resolved configuration for the unified component/static asset pipeline."""

    enabled: bool = True
    webpack_enabled: bool = True
    component_manifest_enabled: bool = True
    webpack_stats_file: Path | None = None
    webpack_bundle_dir: str = ""
    static_url: str = "/static/"
    component_manifest_path: Path | None = None
    configured_assets: dict[str, Any] | None = None
    #: Effective render-first mode (``FUSION_RENDER_FIRST``, legacy names
    #: accepted). Lets asset serving branch on the same variable the render
    #: roads use — one source of truth for mode + assets.
    fusion_render_first: bool = True
    #: Optional gate: when True, webpack/skeleton links are only merged into
    #: the manifest while render-first is active (data-api mode trims the
    #: Django-road bundles). Opt-in via ``FUSION_PIPELINE["render_first_gates_assets"]``.
    render_first_gates_assets: bool = False

    @property
    def render_first(self) -> bool:
        """Short alias for ``fusion_render_first`` (easier call sites)."""
        return self.fusion_render_first

    @classmethod
    def from_django_settings(cls) -> AssetPipelineOptions:
        """Resolve package options from Django settings without importing site code."""
        pipeline = _pipeline_settings()
        webpack = pipeline.get("webpack", {}) or {}
        components = pipeline.get("components", {}) or {}
        loader = (getattr(settings, "WEBPACK_LOADER", {}) or {}).get("DEFAULT", {})

        stats_file = webpack.get("stats_file") or loader.get("STATS_FILE")
        bundle_dir = webpack.get("bundle_dir") or loader.get("BUNDLE_DIR_NAME", "")
        manifest_path = components.get("manifest_path")
        if manifest_path is None:
            static_root = getattr(settings, "STATIC_ROOT", None)
            manifest_path = (
                Path(static_root) / "components" / "manifest.json"
                if static_root
                else None
            )

        return cls(
            enabled=bool(pipeline.get("enabled", True)),
            webpack_enabled=bool(webpack.get("enabled", True)),
            component_manifest_enabled=bool(components.get("enabled", True)),
            webpack_stats_file=Path(stats_file) if stats_file else None,
            webpack_bundle_dir=str(bundle_dir or ""),
            static_url=str(
                pipeline.get("static_url", getattr(settings, "STATIC_URL", "/static/"))
            ),
            component_manifest_path=(Path(manifest_path) if manifest_path else None),
            configured_assets=deepcopy(getattr(settings, "FUSION_ASSETS", {}) or {}),
            fusion_render_first=resolve_render_first_setting(default=True),
            render_first_gates_assets=bool(pipeline.get("render_first_gates_assets", False)),
        )

    def public_url(self, path: str) -> str:
        """Return a stable public URL for a relative generated asset path."""
        if path.startswith(("/", "http://", "https://")):
            return path
        prefix = self.static_url.rstrip("/")
        return f"{prefix}/{path.lstrip('/')}"


def get_asset_pipeline_options() -> AssetPipelineOptions:
    """Return the current settings-derived pipeline options."""
    return AssetPipelineOptions.from_django_settings()


def get_component_asset_options() -> dict[str, Any]:
    """Return the ``FUSION_COMPONENT_ASSETS`` settings with defaults.

    Controls per-component JS/CSS lazy-loading.  All features are disabled
    by default.

    Example (production)::

        FUSION_COMPONENT_ASSETS = {
            "ENABLED": True,
            "PRELOAD_CRITICAL": True,
            "LAZY_LOAD_BELOW_FOLD": True,
            "CHUNK_SIZE_WARNING": 102400,  # 100 KB
        }
    """
    defaults: dict[str, Any] = {
        "ENABLED": False,
        "BUNDLES_JSON_PATH": None,
        "COMPONENT_MANIFEST_PATH": None,
        "PRELOAD_CRITICAL": True,
        "LAZY_LOAD_BELOW_FOLD": True,
        "CHUNK_SIZE_WARNING": 100 * 1024,
    }
    try:
        from django.conf import settings
        user = (
            getattr(settings, "FUSION_COMPONENTS", None)
            or getattr(settings, "FUSION_COMPONENT_ASSETS", None)
            or {}
        )
    except Exception:
        user = {}
    return {**defaults, **{k: v for k, v in user.items() if k in defaults}}
