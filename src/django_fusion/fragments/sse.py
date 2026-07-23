"""Server-Sent Events transport for fragment requests.

Provides a lightweight SSE streamer that renders a Django template and
emits it as a single ``fragment`` event.  Clients such as the HTMX
SSE extension can listen for this event and swap it into the DOM.
"""
from __future__ import annotations

from django.template.loader import render_to_string


class SSHTMXFragmentStreamer:
    """Stream a rendered fragment as an SSE event.

    The rendered HTML is emitted as a single ``fragment`` event.  This is
    compatible with the HTMX ``sse-ext`` extension, which can listen for
    named events and swap their data into a target element.
    """

    def __init__(self, request, template_name: str, context: dict, *, event_name: str = "fragment") -> None:
        self.request = request
        self.template_name = template_name
        self.context = context
        self.event_name = event_name

    def _render(self) -> str:
        return render_to_string(self.template_name, self.context, request=self.request)

    def stream(self):
        """Yield SSE formatted lines for the rendered fragment."""
        html = self._render().replace("\n", "")
        yield f"event: {self.event_name}\n"
        yield f"data: {html}\n\n"
