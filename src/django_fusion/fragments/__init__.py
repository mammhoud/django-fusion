"""django_fusion.fragments

URL-driven fragment rendering for Django, HTMX, and SSE.

This package provides a lightweight way to request any template
fragment by a dotted name over HTTP:

* ``/fragments/<dotted.name>/`` — render a fragment as an HTML response.
* ``/fragments/?q=<dotted.name>`` — query-style fragment request.
* ``Accept: text/event-stream`` — receive the same fragment over SSE.

Core classes:
  - ``FragmentRequestRenderer``: resolves a fragment name to a template,
    renders it, and returns the correct HTTP response.
  - ``SSHTMXFragmentStreamer``: wraps a rendered fragment in an SSE event.
  - ``FragmentRequestView``: Django view wired to ``/fragments/``.

Usage::

    from django_fusion.fragments import FragmentRequestRenderer

    renderer = FragmentRequestRenderer(request)
    response = renderer.render("components.home.hero")
"""

from __future__ import annotations

from .page_context import resolve_page_context
from .renderer import FragmentRequestRenderer
from .registry import (
    clear_fragment_components,
    get_fragment_component,
    register_fragment_component,
    unregister_fragment_component,
)
from .sse import SSHTMXFragmentStreamer
from .views import FragmentRequestView

__all__ = [
    "FragmentRequestRenderer",
    "SSHTMXFragmentStreamer",
    "FragmentRequestView",
    "clear_fragment_components",
    "get_fragment_component",
    "register_fragment_component",
    "resolve_page_context",
    "unregister_fragment_component",
]
