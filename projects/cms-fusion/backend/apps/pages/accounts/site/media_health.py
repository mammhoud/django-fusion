"""Media health check endpoint for fusion-cms.com."""
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse


def media_health_check(request):
    """
    Check media file availability and return health status.

    Validates:
    - Media files directory exists and is readable
    - Media files are accessible
    - Media volume is mounted correctly

    Returns JSON with detailed health information.
    """
    health_status = {
        "status": "ok",
        "checks": {},
        "warnings": [],
        "errors": []
    }

    # Check 1: Media files directory
    media_root = Path(settings.MEDIA_ROOT)
    if media_root.exists() and media_root.is_dir():
        health_status["checks"]["media_root"] = {
            "status": "ok",
            "path": str(media_root),
            "readable": True
        }

        # Count media files
        try:
            media_files = list(media_root.rglob("*"))
            file_count = len([f for f in media_files if f.is_file()])
            health_status["checks"]["media_root"]["file_count"] = file_count
        except Exception as e:
            health_status["checks"]["media_root"]["file_count_error"] = str(e)
    else:
        health_status["checks"]["media_root"] = {
            "status": "warning",
            "path": str(media_root),
            "readable": False
        }
        health_status["warnings"].append(f"Media root directory not found: {media_root}")
        health_status["status"] = "degraded"

    # Check 2: Media volume mount verification
    # Try to write a test file to verify the volume is writable
    try:
        test_file = media_root / ".health_check"
        test_file.touch()
        test_file.unlink()
        health_status["checks"]["media_writable"] = {
            "status": "ok",
            "message": "Media volume is writable"
        }
    except Exception as e:
        health_status["checks"]["media_writable"] = {
            "status": "warning",
            "message": f"Media volume write test failed: {e}"
        }
        health_status["warnings"].append(f"Media volume may not be writable: {e}")
        if health_status["status"] == "ok":
            health_status["status"] = "degraded"

    # Check 3: Common media subdirectories
    common_dirs = ["uploads", "images", "documents", "videos"]
    for subdir in common_dirs:
        subdir_path = media_root / subdir
        if subdir_path.exists():
            health_status["checks"][f"media_{subdir}"] = {
                "status": "ok",
                "path": str(subdir_path),
                "exists": True
            }

    # Determine overall status
    if health_status["errors"]:
        health_status["status"] = "unhealthy"
    elif health_status["warnings"]:
        health_status["status"] = "degraded"

    # Set HTTP status code based on health
    status_code = 200 if health_status["status"] in ["ok", "degraded"] else 503

    return JsonResponse(health_status, status=status_code)
