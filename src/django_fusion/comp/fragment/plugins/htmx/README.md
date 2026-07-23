# `django_fusion.comp.fragment.plugins.htmx`

HTMX plugin for django-fusion fragments.

## API

- `is_htmx_request(request)` — True when the request carries `HX-Request: true`.
- `supports_htmx(request)` — Alias for `is_htmx_request`.
- `supports_sse(request)` — True when `Accept: text/event-stream`.
- `HtmxDetails` — Request wrapper exposing `target`, `trigger`, `boosted`, etc.
- `ServerSentEvent`, `SSEMixin` — SSE helpers.
- `push_url(response, url)`, `replace_url(response, url)` — History helpers.
- `trigger_client_event(...)` — Emit HTMX client events via response headers.

## Example

```python
from django_fusion.comp.fragment.plugins.htmx import is_htmx_request, HtmxDetails


def article_list(request):
    if is_htmx_request(request):
        target = request.htmx.target
        ...
```

## Backward compatibility

`django_fusion.ci.plugins` still re-exports these symbols.
