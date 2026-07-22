"""
Info, health, and stats route handlers for POS Solo.
"""

from datetime import datetime, timezone
from asgiref.sync import sync_to_async
from robyn import jsonify
from routes import state as S
from __about__ import __version__, __title_solo__, __service_name_solo__


def register_info_routes(app):
    @app.get("/")
    async def index(request):
        counts = {}
        for m in S._ALL_MODELS:
            try:
                counts[m.__name__] = await S._count(m)
            except Exception:
                counts[m.__name__] = -1
        return jsonify({
            "service": __title_solo__, "version": __version__,
            "database": str(S.DB_PATH), "django_orm": S._DJANGO_READY,
            "pydantic": S._PYDANTIC_READY, "counts": counts,
        })

    @app.get("/health")
    async def health(request):
        return jsonify({
            "status": "healthy", "service": __service_name_solo__, "version": __version__,
            "uptime": (datetime.now(timezone.utc) - S._start_time).total_seconds(),
            "django_orm": S._DJANGO_READY, "database": str(S.DB_PATH),
        })

    @app.get("/stats")
    async def stats_endpoint(request):
        @sync_to_async
        def _stats():
            return {
                "products": S._ALL_MODELS[1].objects.count() if len(S._ALL_MODELS) > 1 else 0,
                "nodes": S.Node.objects.count() if S.Node else 0,
                "nodes_online": S.Node.objects.filter(status="online").count() if S.Node else 0,
                "uptime_seconds": (datetime.now(timezone.utc) - S._start_time).total_seconds(),
            }
        return jsonify(await _stats())
