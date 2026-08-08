"""POS Cloud Sidecar — django-fusion API-first feature routes.

Implements the django-fusion render-mode contract served over the sidecar:
the frontend asks the sidecar which render mode is active, fetches the
navigation tree, and can toggle the session mode. This mirrors the
`/fusion/*` endpoints the Django backend exposes, so the Astro frontend
works identically against the sidecar or the Django server.
"""

from __future__ import annotations

from datetime import datetime, timezone

from robyn import jsonify


def register_fusion_routes(app):
    """Register /fusion/* routes (render mode, nav, session, health)."""

    @app.get("/fusion/health")
    async def fusion_health(request):
        return jsonify({
            "status": "healthy",
            "service": "pos-cloud",
            "fusion": True,
            "render_modes": ["data-api", "fusion-render"],
            "version": "1.0",
        })

    @app.get("/fusion/render-mode")
    async def render_mode(request):
        return jsonify({
            "render_first": False,
            "render_mode": "data-api",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

    @app.get("/fusion/nav")
    async def fusion_nav(request):
        """Navigation tree for the POS Cloud shell (sidecar contract)."""
        return jsonify({
            "language": "en",
            "nav_items": [
                {"label": "Dashboard", "href": "/", "icon": "dashboard"},
                {"label": "Organizations", "href": "/organizations", "icon": "corporate_fare"},
                {"label": "Branches", "href": "/branches", "icon": "store"},
                {"label": "CRM", "href": "/crm", "icon": "handshake"},
                {"label": "Sync", "href": "/sync", "icon": "sync"},
                {"label": "Admin", "href": "/admin", "icon": "admin"},
            ],
        })

    @app.post("/fusion/session-mode")
    async def session_mode(request):
        body = request.json() or {}
        mode = body.get("mode", "data-api")
        return jsonify({
            "mode": mode if mode in ("data-api", "fusion-render") else "data-api",
            "saved": True,
        })

    @app.get("/fusion/assets")
    async def fusion_assets(request):
        return jsonify({
            "css": ["/static/css/fusion.css"],
            "js": [],
        })
