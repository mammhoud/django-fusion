"""Django views for fragment requests."""
from __future__ import annotations

from typing import Any

from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from .renderer import FragmentRequestRenderer
from .registry import get_fragment_component
from .page_context import resolve_page_context


class FragmentRequestView(View):
    """Render a template fragment on demand.

    Accepts the fragment name either as a URL path segment::

        /fragments/components.home.hero/

    or as a query parameter::

        /fragments/?q=components.home.sections.hero

    When the request advertises ``Accept: text/event-stream``, the
    fragment is streamed as a Server-Sent Event.  Otherwise a normal
    ``HttpResponse`` is returned, with HTMX/Unpoly headers when detected.

    Page context
    ------------
    Fragments often need the same context as the page that hosts them.
    The view resolves page context from one of (in order):

    * ``HX-Current-URL`` request header (sent by HTMX)
    * ``page_path`` query parameter
    * ``page_url`` query parameter

    For Wagtail pages, ``page.get_context(request)`` is merged into the
    fragment context. For regular Django class-based views,
    ``get_context_data()`` is used.

    Wiring example in ``ROOT_URLCONF``::

        from django.urls import path, include

        urlpatterns = [
            path("fragments/", include("django_fusion.fragments.urls")),
        ]

    Example requests::

        # path-style
        curl http://localhost:8000/fragments/components.home.hero/

        # query-style
        curl "http://localhost:8000/fragments/?q=components.home.hero"

        # SSE
        curl -H "Accept: text/event-stream" \\
             http://localhost:8000/fragments/components.home.hero/

        # fragment with explicit host page context
        curl "http://localhost:8000/fragments/?q=components.home.hero&page_path=/"
    """

    http_method_names = ["get", "head"]

    def get(self, request, *, fragment_name: str | None = None) -> HttpResponse:
        if not fragment_name:
            fragment_name = request.GET.get("q", "")

        if not fragment_name:
            return HttpResponseBadRequest("Fragment name is required (via path or ?q=).")

        page_context = resolve_page_context(request)

        # First try to route to a registered FragmentComponent.  If no
        # component is registered, fall back to a plain template render.
        component_class = get_fragment_component(fragment_name)
        if component_class is not None:
            # Bypass the normal HTTP header check so /fragments/ always
            # renders the fragment, even for non-HTMX clients.
            view = component_class()
            view.setup(request)
            context = view.get_fragment_context()
            context.update(page_context)
            return view.render_fragment_response(context)

        renderer = FragmentRequestRenderer(request, context=page_context)
        return renderer.render(fragment_name)
