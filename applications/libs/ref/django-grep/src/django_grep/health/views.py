"""Health check views for monitoring application status."""
import os
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.test import Client
from django.views import View


class HealthCheckView(View):
    """
    Comprehensive health check endpoint.

    Returns HTTP 200 if the application is running and home page is accessible.

    **Endpoint**: ``GET /health/``

    **Response**::

        {
            "status": "healthy",
            "service": "django-app",
            "version": "1.0.0",
            "homepage": {
                "status": "ok",
                "status_code": 200,
                "has_content": true
            }
        }
    """

    def get(self, request):
        """Return comprehensive health status including homepage check."""
        health_data = {
            "status": "healthy",
            "service": getattr(settings, "SERVICE_NAME", "django-app"),
            "version": getattr(settings, "VERSION", "1.0.0"),
        }

        # Check homepage accessibility
        try:
            client = Client()
            response = client.get("/", follow=True)
            has_content = len(response.content) > 100  # Basic content check

            health_data["homepage"] = {
                "status": "ok" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "has_content": has_content,
                "content_length": len(response.content)
            }

            if response.status_code != 200 or not has_content:
                health_data["status"] = "degraded"

        except Exception as e:
            health_data["homepage"] = {
                "status": "error",
                "error": str(e)
            }
            health_data["status"] = "degraded"

        status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
        return JsonResponse(health_data, status=status_code)


class DatabaseHealthView(View):
    """
    Database connectivity health check.

    Returns HTTP 200 if database connection is working, HTTP 503 if not.

    **Endpoint**: ``GET /health/database/``

    **Success Response**::

        {
            "status": "healthy",
            "database": "connected"
        }

    **Error Response** (HTTP 503)::

        {
            "status": "unhealthy",
            "database": "disconnected",
            "error": "connection refused"
        }
    """

    def get(self, request):
        """Check database connectivity."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return JsonResponse({
                "status": "healthy",
                "database": "connected",
            })
        except Exception as e:
            return JsonResponse({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            }, status=503)


class AssetsHealthView(View):
    """
    Comprehensive static assets health check.

    Returns HTTP 200 if static files directory exists and critical assets are present,
    HTTP 503 if not.

    **Endpoint**: ``GET /health/assets/``

    **Success Response**::

        {
            "status": "healthy",
            "static_root": "/path/to/static",
            "exists": true,
            "checks": {
                "static_root": {"status": "ok", "path": "..."},
                "webpack_bundles": {"status": "ok", "asset_count": 10},
                "bundle_files": {"status": "ok", "file_count": 5}
            }
        }

    **Error Response** (HTTP 503)::

        {
            "status": "unhealthy",
            "static_root": "/path/to/static",
            "exists": false,
            "errors": ["Static root directory not found"]
        }
    """

    def get(self, request):
        """Check static files directory and critical assets."""
        health_status = {
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": []
        }

        # Check 1: Static files directory
        static_root = getattr(settings, "STATIC_ROOT", None)
        if static_root and os.path.exists(static_root):
            static_path = Path(static_root)
            file_count = sum(1 for _ in static_path.rglob("*") if _.is_file())
            health_status["static_root"] = static_root
            health_status["exists"] = True
            health_status["checks"]["static_root"] = {
                "status": "ok",
                "path": str(static_root),
                "file_count": file_count
            }
        else:
            health_status["static_root"] = static_root
            health_status["exists"] = False
            health_status["checks"]["static_root"] = {
                "status": "error",
                "path": str(static_root) if static_root else "not configured"
            }
            health_status["errors"].append("Static root directory not found")
            health_status["status"] = "unhealthy"

        # Check 2: Webpack bundles.json
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
                    if health_status["status"] == "healthy":
                        health_status["status"] = "degraded"
            else:
                health_status["checks"]["webpack_bundles"] = {
                    "status": "warning",
                    "path": str(stats_path),
                    "exists": False
                }
                health_status["warnings"].append("Webpack stats file not found")
        else:
            health_status["checks"]["webpack_bundles"] = {
                "status": "info",
                "message": "Webpack loader not configured"
            }

        # Check 3: Bundle files directory
        if static_root and os.path.exists(static_root):
            static_path = Path(static_root)
            bundles_dir = static_path.parent / "bundles"
            if bundles_dir.exists():
                bundle_files = list(bundles_dir.rglob("*.js"))
                css_files = list(bundles_dir.rglob("*.css"))
                health_status["checks"]["bundle_files"] = {
                    "status": "ok",
                    "path": str(bundles_dir),
                    "js_count": len(bundle_files),
                    "css_count": len(css_files)
                }
            else:
                health_status["checks"]["bundle_files"] = {
                    "status": "warning",
                    "message": "Bundles directory not found"
                }
                health_status["warnings"].append("Bundle files directory not accessible")

        # Determine overall status
        if health_status["errors"]:
            health_status["status"] = "unhealthy"
        elif health_status["warnings"] and health_status["status"] == "healthy":
            health_status["status"] = "degraded"

        status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
        return JsonResponse(health_status, status=status_code)


class MediaHealthView(View):
    """
    Media files health check.

    Returns HTTP 200 if media directory exists and is accessible,
    HTTP 503 if not.

    **Endpoint**: ``GET /health/media/``

    **Success Response**::

        {
            "status": "healthy",
            "media_root": "/path/to/media",
            "exists": true
        }

    **Error Response** (HTTP 503)::

        {
            "status": "unhealthy",
            "media_root": "/path/to/media",
            "exists": false
        }
    """

    def get(self, request):
        """Check media files directory."""
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.exists(media_root):
            return JsonResponse({
                "status": "healthy",
                "media_root": media_root,
                "exists": True,
            })
        return JsonResponse({
            "status": "unhealthy",
            "media_root": media_root,
            "exists": False,
        }, status=503)
