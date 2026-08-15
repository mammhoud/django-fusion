"""Rendering helpers for django-fusion routes.

Canonical render-mode resolution (:mod:`render_mode`), response builders
(:mod:`renderers`), the session/codec helpers (:mod:`session`), template
resolution (:mod:`template_resolver`), and the function-view dual-mode
decorator (:mod:`decorators`).
"""

from __future__ import annotations

from django_fusion.routes.rendering.decorators import dual_mode, fusion_view
from django_fusion.routes.rendering.render_mode import (
    header_render_first,
    resolve_render_first,
    session_render_first,
)
from django_fusion.routes.rendering.renderers import (
    FusionJSONEncoder,
    FusionJSONRenderer,
    fusion_json_response,
)
from django_fusion.routes.rendering.session import (
    CODEC_VERSION,
    FusionCodec,
    SESSION_KEY,
)

__all__ = [
    "CODEC_VERSION",
    "FusionCodec",
    "FusionJSONEncoder",
    "FusionJSONRenderer",
    "SESSION_KEY",
    "dual_mode",
    "fusion_json_response",
    "fusion_view",
    "header_render_first",
    "resolve_render_first",
    "session_render_first",
]
