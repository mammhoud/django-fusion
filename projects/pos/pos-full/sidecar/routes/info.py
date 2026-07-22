"""
Info, health, and stats route handlers.
"""

from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify

from routes import state as S
from __about__ import __version__, __service_name_full__, __service_desc_full__


def register_info_routes(app):
    """Register GET /, /health, /stats."""

    @app.get("/")
    async def index(request):
        counts = {}
        for m in S._ALL_MODELS:
            try:
                counts[m.__name__] = await S._count(m)
            except Exception:
                counts[m.__name__] = -1
        return jsonify({
            "service": __service_desc_full__,
            "version": __version__,
            "database": str(S.DB_PATH),
            "django_orm": S._DJANGO_READY,
            "pydantic": S._PYDANTIC_READY,
            "num_models": len(S._ALL_MODELS),
            "counts": counts,
        })

    @app.get("/health")
    async def health(request):
        return jsonify({
            "status": "healthy",
            "service": __service_name_full__,
            "version": __version__,
            "uptime": (datetime.now(timezone.utc) - S._start_time).total_seconds(),
            "django_orm": S._DJANGO_READY,
            "database": str(S.DB_PATH),
        })

    @app.get("/stats")
    async def stats_endpoint(request):
        @sync_to_async
        def _stats():
            stats = {}
            for m in S._ALL_MODELS:
                try:
                    stats[m.__name__] = m.objects.count()
                except Exception:
                    stats[m.__name__] = -1
            stats["nodes_online"] = S.Node.objects.filter(status="online").count()
            stats["nodes_offline"] = S.Node.objects.filter(status="offline").count()
            stats["uptime_seconds"] = (datetime.now(timezone.utc) - S._start_time).total_seconds()
            return stats
        return jsonify(await _stats())
