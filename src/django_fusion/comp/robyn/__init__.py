"""
django-fusion Robyn integration (``django_fusion.comp.robyn``).

Bridges django-fusion viewsets, components, and fragment rendering to
Robyn async servers.  Lets POS sidecars mount django-fusion routes
without a full Django WSGI/ASGI stack.

Quickstart::

    from robyn import Robyn
    from django_fusion.comp.robyn import RobynAdapter, RobynRequest, RobynFusionChecker

    app = Robyn(__file__)

    # Mount a django-fusion Application
    from myapp.viewsets import POSApi
    RobynAdapter(app).mount(POSApi())

    # Fragment health check
    RobynFusionChecker().register_health_route(app)

    app.start(host="0.0.0.0", port=8765)

Modules:
    - ``request.py`` — ``RobynRequest`` wrapper (Django HttpRequest interface)
    - ``adapter.py`` — ``RobynAdapter`` for mounting viewsets/routes
    - ``checker.py`` — ``RobynFusionChecker`` for /fusion/health endpoint

See `projects/pos/docs/DJANGO_FUSION_ENHANCEMENTS_PLAN.md` for the
full POS × django-fusion integration roadmap.
"""

from django_fusion.comp.robyn.request import RobynRequest
from django_fusion.comp.robyn.adapter import RobynAdapter, register_viewset
from django_fusion.comp.robyn.checker import RobynFusionChecker

__all__ = [
    "RobynAdapter",
    "RobynRequest",
    "RobynFusionChecker",
    "register_viewset",
]
