"""Asset health check endpoint for fusion-cms.com."""
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse


def asset_health_check(request):
    """
    Check asset availability and return health status.

    Validates:
    - Static files directory exists and is readable
    - Media files directory exists and is readable
    - Webpack bundles.json exists and is valid
    - Critical static assets are present

    Returns JSON with detailed health information.
    """
    health_status = {
        "status": "ok",
        "checks": {},
        "warnings": [],
        "errors": []
    }

    # Check 1: Static files directory
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists() and static_root.is_dir():
        health_status["checks"]["static_root"] = {
            "status": "ok",
            "path": str(static_root),
            "readable": True
        }
    else:
        health_status["checks"]["static_root"] = {
            "status": "error",
            "path": str(static_root),
            "readable": False
        }
        health_status["errors"].append(f"Static root directory not found: {static_root}")
        health_status["status"] = "degraded"

    # Check 2: Media files directory
    media_root = Path(settings.MEDIA_ROOT)
    if media_root.exists() and media_root.is_dir():
        health_status["checks"]["media_root"] = {
            "status": "ok",
            "path": str(media_root),
            "readable": True
        }
    else:
        health_status["checks"]["media_root"] = {
            "status": "warning",
            "path": str(media_root),
            "readable": False
        }
        health_status["warnings"].append(f"Media root directory not found: {media_root}")
        if health_status["status"] == "ok":
            health_status["status"] = "degraded"

    # Check 3: Webpack bundles.json
    webpack_config = getattr(settings, "WEBPACK_LOADER", {}).get("DEFAULT", {})
    stats_file = webpack_config.get("STATS_FILE")

    if stats_file:
        stats_path = Path(stats_file)
        if stats_path.exists() and stats_path.is_file():
            try:
                import json
                with open(stats_path, 'r') as f:
                    bundle_data = json.load(f)
                    asset_count = len(bundle_data.get("assets", {}))
                    health_status["checks"]["webpack_bundles"] = {
                        "status": "ok",
                        "path": str(stats_path),
                        "asset_count": asset_count
                    }
            except (json.JSONDecodeError, IOError) as e:
                health_status["checks"]["webpack_bundles"] = {
                    "status": "error",
                    "path": str(stats_path),
                    "error": str(e)
                }
                health_status["errors"].append(f"Failed to read webpack bundles: {e}")
                health_status["status"] = "degraded"
        else:
            health_status["checks"]["webpack_bundles"] = {
                "status": "warning",
                "path": str(stats_path),
                "exists": False
            }
            health_status["warnings"].append(f"Webpack stats file not found: {stats_path}")
    else:
        health_status["checks"]["webpack_bundles"] = {
            "status": "warning",
            "message": "Webpack loader not configured"
        }
        health_status["warnings"].append("Webpack loader stats file not configured")

    # Check 4: Critical static assets (bundles directory)
    bundles_dir = static_root.parent / "bundles" if static_root.exists() else None
    if bundles_dir and bundles_dir.exists():
        bundle_files = list(bundles_dir.glob("*.js"))
        health_status["checks"]["bundle_files"] = {
            "status": "ok",
            "path": str(bundles_dir),
            "file_count": len(bundle_files)
        }
    else:
        health_status["checks"]["bundle_files"] = {
            "status": "warning",
            "message": "Bundles directory not found or empty"
        }
        health_status["warnings"].append("Bundle files directory not accessible")

    # Determine overall status
    if health_status["errors"]:
        health_status["status"] = "unhealthy"
    elif health_status["warnings"]:
        health_status["status"] = "degraded"

    # Set HTTP status code based on health
    status_code = 200 if health_status["status"] in ["ok", "degraded"] else 503

    return JsonResponse(health_status, status=status_code)
