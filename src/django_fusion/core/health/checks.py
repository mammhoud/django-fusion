"""Reusable filesystem and webpack health checks.

The checks intentionally return the historical JSON contract used by the
fusion site projects.  Project modules should import these functions rather
than copy the implementation; site-specific CDN or storage checks remain
adapters in the project layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.http import JsonResponse


_COMMON_MEDIA_DIRECTORIES = ("uploads", "images", "documents", "videos")


def _response(payload: dict[str, Any]) -> JsonResponse:
    """Build the historical health response and HTTP status code."""
    status = payload["status"]
    http_status = 200 if status in {"ok", "degraded"} else 503
    return JsonResponse(payload, status=http_status)


def media_health_check(request: Any) -> JsonResponse:
    """Check the configured media directory and its common subdirectories."""
    del request  # The check is intentionally independent of request metadata.
    media_root = Path(settings.MEDIA_ROOT)
    health_status: dict[str, Any] = {
        "status": "ok",
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    if media_root.exists() and media_root.is_dir():
        health_status["checks"]["media_root"] = {
            "status": "ok",
            "path": str(media_root),
            "readable": True,
        }
        try:
            health_status["checks"]["media_root"]["file_count"] = sum(
                path.is_file() for path in media_root.rglob("*")
            )
        except Exception as exc:  # pragma: no cover - storage-specific failure
            health_status["checks"]["media_root"]["file_count_error"] = str(exc)
    else:
        health_status["checks"]["media_root"] = {
            "status": "warning",
            "path": str(media_root),
            "readable": False,
        }
        health_status["warnings"].append(
            f"Media root directory not found: {media_root}"
        )
        health_status["status"] = "degraded"

    try:
        test_file = media_root / ".health_check"
        test_file.touch()
        test_file.unlink()
        health_status["checks"]["media_writable"] = {
            "status": "ok",
            "message": "Media volume is writable",
        }
    except Exception as exc:  # pragma: no cover - storage-specific failure
        health_status["checks"]["media_writable"] = {
            "status": "warning",
            "message": f"Media volume write test failed: {exc}",
        }
        health_status["warnings"].append(f"Media volume may not be writable: {exc}")
        if health_status["status"] == "ok":
            health_status["status"] = "degraded"

    for subdirectory in _COMMON_MEDIA_DIRECTORIES:
        path = media_root / subdirectory
        if path.exists():
            health_status["checks"][f"media_{subdirectory}"] = {
                "status": "ok",
                "path": str(path),
                "exists": True,
            }

    if health_status["errors"]:
        health_status["status"] = "unhealthy"
    elif health_status["warnings"]:
        health_status["status"] = "degraded"
    return _response(health_status)


def asset_health_check(request: Any) -> JsonResponse:
    """Check static/media roots and the configured webpack stats file."""
    del request
    static_root = Path(settings.STATIC_ROOT)
    media_root = Path(settings.MEDIA_ROOT)
    health_status: dict[str, Any] = {
        "status": "ok",
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    if static_root.exists() and static_root.is_dir():
        health_status["checks"]["static_root"] = {
            "status": "ok",
            "path": str(static_root),
            "readable": True,
        }
    else:
        health_status["checks"]["static_root"] = {
            "status": "error",
            "path": str(static_root),
            "readable": False,
        }
        health_status["errors"].append(
            f"Static root directory not found: {static_root}"
        )
        health_status["status"] = "degraded"

    if media_root.exists() and media_root.is_dir():
        health_status["checks"]["media_root"] = {
            "status": "ok",
            "path": str(media_root),
            "readable": True,
        }
    else:
        health_status["checks"]["media_root"] = {
            "status": "warning",
            "path": str(media_root),
            "readable": False,
        }
        health_status["warnings"].append(
            f"Media root directory not found: {media_root}"
        )
        if health_status["status"] == "ok":
            health_status["status"] = "degraded"

    webpack_config = getattr(settings, "WEBPACK_LOADER", {}).get("DEFAULT", {})
    stats_file = webpack_config.get("STATS_FILE")
    if stats_file:
        stats_path = Path(stats_file)
        if stats_path.exists() and stats_path.is_file():
            try:
                with stats_path.open(encoding="utf-8") as stats_handle:
                    bundle_data = json.load(stats_handle)
                health_status["checks"]["webpack_bundles"] = {
                    "status": "ok",
                    "path": str(stats_path),
                    "asset_count": len(bundle_data.get("assets", {})),
                }
            except (json.JSONDecodeError, OSError, AttributeError) as exc:
                health_status["checks"]["webpack_bundles"] = {
                    "status": "error",
                    "path": str(stats_path),
                    "error": str(exc),
                }
                health_status["errors"].append(
                    f"Failed to read webpack bundles: {exc}"
                )
                health_status["status"] = "degraded"
        else:
            health_status["checks"]["webpack_bundles"] = {
                "status": "warning",
                "path": str(stats_path),
                "exists": False,
            }
            health_status["warnings"].append(
                f"Webpack stats file not found: {stats_path}"
            )
    else:
        health_status["checks"]["webpack_bundles"] = {
            "status": "warning",
            "message": "Webpack loader not configured",
        }
        health_status["warnings"].append("Webpack loader stats file not configured")

    bundles_dir = static_root.parent / "bundles" if static_root.exists() else None
    if bundles_dir and bundles_dir.exists():
        health_status["checks"]["bundle_files"] = {
            "status": "ok",
            "path": str(bundles_dir),
            "file_count": sum(path.suffix == ".js" for path in bundles_dir.iterdir()),
        }
    else:
        health_status["checks"]["bundle_files"] = {
            "status": "warning",
            "message": "Bundles directory not found or empty",
        }
        health_status["warnings"].append("Bundle files directory not accessible")

    if health_status["errors"]:
        health_status["status"] = "unhealthy"
    elif health_status["warnings"]:
        health_status["status"] = "degraded"
    return _response(health_status)
