from __future__ import annotations

import hashlib
import json
import logging
from enum import Enum
from pathlib import Path

from django.conf import settings

from django_fusion.config.assets import AssetPipelineOptions, get_asset_pipeline_options

logger = logging.getLogger(__name__)

_manifest_cache: dict[
    str, tuple[tuple[int, int, str], dict[str, list[str]]]
] = {}


class PathPrefix(str, Enum):
    """Path prefixes used for normalizing template paths."""

    PKG = "pkg:"
    APP = "app:"
    EXT = "ext:"

    def prepend_to(self, path: str) -> str:
        """Generate a prefixed path string by prepending this prefix to a path.

        Args:
            path: The path to prefix

        Returns:
            str: A string with this prefix and the path
        """
        return f"{self.value}{path}"

    @classmethod
    def has_prefix(cls, path: str) -> bool:
        """Check if a path already has one of the recognized prefixes.

        Args:
            path: The path to check

        Returns:
            bool: True if the path starts with any of the recognized prefixes
        """
        return any(path.startswith(prefix.value) for prefix in cls)


def normalize_path(path: str) -> str:
    """Normalize a template path to remove system-specific information.

    Args:
        path: The template path to normalize

    Returns:
        str: A normalized path without system-specific details
    """
    if PathPrefix.has_prefix(path):
        return path

    if "site-packages" in path:
        parts = path.split("site-packages/")
        if len(parts) > 1:
            return PathPrefix.PKG.prepend_to(parts[1])

    if hasattr(settings, "BASE_DIR") and settings.BASE_DIR:  # type: ignore[misc]
        base_dir = Path(settings.BASE_DIR).resolve()  # type: ignore[misc]
        abs_path = Path(path).resolve()
        try:
            if str(abs_path).startswith(str(base_dir)):
                rel_path = abs_path.relative_to(base_dir)
                return PathPrefix.APP.prepend_to(str(rel_path))
        except ValueError:
            # Path is not relative to BASE_DIR
            pass

    if path.startswith("/"):
        hash_val = hashlib.md5(path.encode()).hexdigest()[:8]
        filename = Path(path).name
        return PathPrefix.EXT.prepend_to(f"{hash_val}/{filename}")

    # Return as is if it's already a relative path
    return path


def load_component_manifest() -> dict[str, list[str]] | None:
    """Load asset manifest from the default location.

    Returns a simple dict mapping template paths to lists of component names.
    If the manifest cannot be loaded, returns None and falls back to runtime scanning.

    Returns:
        dict[str, list[str]] | None: Manifest data or None if not found or invalid
    """
    options = get_asset_pipeline_options()
    manifest_path = options.component_manifest_path or default_manifest_path()
    if not manifest_path.exists():
        return None

    try:
        stat = manifest_path.stat()
        content = manifest_path.read_bytes()
    except OSError as exc:
        logger.info("Asset manifest unavailable at %s: %s", manifest_path, exc)
        return None

    cache_path = str(manifest_path.resolve())
    signature = (stat.st_mtime_ns, stat.st_size, hashlib.sha256(content).hexdigest())
    cached = _manifest_cache.get(cache_path)
    if cached is not None and cached[0] == signature:
        return cached[1]

    try:
        manifest_data = json.loads(content)
        if not isinstance(manifest_data, dict):
            logger.warning("Asset manifest at %s is not a JSON object", manifest_path)
            return None
        # Keep one entry per path. Rebuilds replace the prior signature
        # instead of growing a process-wide cache indefinitely.
        _manifest_cache[cache_path] = (signature, manifest_data)
        return manifest_data
    except json.JSONDecodeError:
        logger.warning(
            f"Asset manifest at {manifest_path} contains invalid JSON. Falling back to registry."
        )
        return None
    except (OSError, PermissionError) as exc:
        logger.warning(
            f"Error reading asset manifest at {manifest_path}: {exc!s}. Falling back to registry."
        )
        return None


def clear_asset_manifest_cache() -> None:
    """Clear cached component manifests after a build or deployment."""
    _manifest_cache.clear()




def load_asset_manifest() -> dict[str, list[str]] | None:
    """Load the component usage manifest used by component asset tags.

    This name remains the canonical component-manifest API. The merged
    pipeline is exposed separately by :func:`load_merged_asset_manifest` so
    template component lookup cannot accidentally consume webpack metadata.
    """
    return load_component_manifest()


def _dedupe(values: list[str]) -> list[str]:
    """Deduplicate links while preserving configured/build order."""
    return list(dict.fromkeys(value for value in values if value))


def _webpack_asset_links(options: AssetPipelineOptions) -> dict[str, list[str]]:
    """Read webpack stats and convert generated chunks into public links."""
    result = {"css": [], "js": []}
    if not options.webpack_enabled or options.webpack_stats_file is None:
        return result

    try:
        payload = json.loads(options.webpack_stats_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.info("Webpack asset stats unavailable: %s", exc)
        return result

    chunks = payload.get("chunks", {}) if isinstance(payload, dict) else {}
    entries: list[object] = []
    if isinstance(chunks, dict):
        for values in chunks.values():
            entries.extend(values if isinstance(values, list) else [])
    elif isinstance(chunks, list):
        entries = chunks

    # webpack-bundle-tracker versions expose either chunks or assets.
    if not entries and isinstance(payload, dict) and isinstance(payload.get("assets"), dict):
        entries = list(payload["assets"].keys())

    for entry in entries:
        if isinstance(entry, dict):
            raw_path = entry.get("url") or entry.get("name") or entry.get("path")
        else:
            raw_path = entry
        if not isinstance(raw_path, str):
            continue
        path = raw_path
        bundle_dir = options.webpack_bundle_dir.strip().strip("/")
        normalized_path = path.lstrip("/")
        static_prefix = options.static_url.rstrip("/") or "/"
        if path.startswith(("http://", "https://")):
            url = path
        elif path.startswith("/"):
            # A root-relative webpack URL may be `/bundles/...` rather than
            # `/static/bundles/...`; only preserve it when it already uses
            # the configured public static prefix. Protocol-relative CDN URLs
            # must remain external URLs.
            if path.startswith("//"):
                url = path
            elif static_prefix == "/":
                url = path
            else:
                url = (
                    path
                    if path == static_prefix or path.startswith(f"{static_prefix}/")
                    else f"{static_prefix}/{path.lstrip('/')}"
                )
        else:
            if not (
                bundle_dir and normalized_path == bundle_dir
                or bundle_dir and normalized_path.startswith(f"{bundle_dir}/")
            ):
                normalized_path = f"{bundle_dir}/{normalized_path}" if bundle_dir else normalized_path
            url = options.public_url(normalized_path)
        suffix = Path(raw_path.split("?", 1)[0]).suffix.lower()
        if suffix == ".css":
            result["css"].append(url)
        elif suffix == ".js":
            result["js"].append(url)

    return {key: _dedupe(value) for key, value in result.items()}


def load_merged_asset_manifest() -> dict[str, object]:
    """Merge configured links, component usage, and webpack output metadata."""
    options = get_asset_pipeline_options()
    if not options.enabled:
        configured = options.configured_assets or {}
        return {
            "version": 1,
            "top": dict(configured.get("top", {}) or {}),
            "bottom": dict(configured.get("bottom", {}) or {}),
            "components": {},
            "webpack": {"enabled": False, "stats_file": None, "bundle_dir": ""},
        }
    configured = options.configured_assets or {}
    top = dict(configured.get("top", {}) or {})
    bottom = dict(configured.get("bottom", {}) or {})
    webpack = _webpack_asset_links(options)

    top["css"] = _dedupe(list(top.get("css", []) or []) + webpack["css"])
    bottom["js"] = _dedupe(list(bottom.get("js", []) or []) + webpack["js"])
    top.setdefault("fonts", [])
    top.setdefault("preconnect", [])
    top.setdefault("inline_css", [])
    bottom.setdefault("inline_js", [])

    component_manifest = (
        load_component_manifest() if options.component_manifest_enabled else None
    )
    return {
        "version": 1,
        "top": top,
        "bottom": bottom,
        "components": component_manifest or {},
        "webpack": {
            "enabled": options.webpack_enabled,
            "stats_file": str(options.webpack_stats_file) if options.webpack_stats_file else None,
            "bundle_dir": options.webpack_bundle_dir,
        },
    }


def generate_asset_manifest() -> dict[str, list[str]]:
    """Generate a manifest by scanning templates for component usage.

    Returns:
        dict[str, list[str]]: A dictionary mapping template paths to lists of component names.
    """
    from django_fusion.comp.loader.templates import gather_block_tag_template_usage

    template_component_map: dict[str, set[str]] = {}

    for template_path, component_names in gather_block_tag_template_usage():
        # Convert Path objects to strings for JSON and normalize
        original_path = str(template_path)
        normalized_path = normalize_path(original_path)
        template_component_map[normalized_path] = component_names

    manifest: dict[str, list[str]] = {
        template: sorted(list(components))
        for template, components in template_component_map.items()
    }

    return manifest


def save_asset_manifest(manifest_data: dict[str, list[str]], path: Path | str) -> None:
    """Save asset manifest to a file.

    Args:
        manifest_data: The manifest data to save
        path: Path where to save the manifest
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(path_obj, "w") as f:
        json.dump(manifest_data, f, indent=2)


def default_manifest_path() -> Path:
    """Get the default manifest path.

    Returns:
        Path: The default path for the asset manifest file
    """
    if hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
        return Path(settings.STATIC_ROOT) / "components" / "manifest.json"
    else:
        # Fallback for when STATIC_ROOT is not set
        return Path("components-asset-manifest.json")
