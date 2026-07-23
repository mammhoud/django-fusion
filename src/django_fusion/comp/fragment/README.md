# `django_fusion.comp.fragment`

> Part of **django-fusion** — Fragment / partial-page rendering layer

`comp.fragment` is the single place for HTMX and Unpoly fragment handling.
It exposes request wrappers, detection utilities, and plugin modules for each
frontend library.

## Contents

- `plugins/`   — HTMX and Unpoly plugins
- `renderer.py` — Fragment request renderer
- `registry.py` — Fragment component registry

## Plugins

### HTMX

`django_fusion.comp.fragment.plugins.htmx` provides:

- `is_htmx_request(request)`
- `supports_htmx(request)`
- `HtmxDetails`
- `ServerSentEvent`, `SSEMixin`
- `push_url`, `replace_url`, `trigger_client_event`

### Unpoly

`django_fusion.comp.fragment.plugins.unpoly` provides:

- `Unpoly`
- `Layer`
- `BaseAdapter`, `DjangoAdapter`

## Usage

```python
from django_fusion.comp.fragment.plugins.htmx import HtmxDetails, is_htmx_request


def my_view(request):
    if is_htmx_request(request):
        target = request.htmx.target
        ...
```

```python
from django_fusion.comp.fragment.plugins.unpoly import DjangoAdapter


def my_view(request):
    request.up = DjangoAdapter(request)
    request.up.set_title("My Page")
```

## Backward compatibility

The old import paths still work:

- `django_fusion.ci.plugins.HtmxDetails`
- `django_fusion.ci.adapters.main.DjangoAdapter`
- `django_fusion.comp.loader.up.Unpoly`

New code should prefer the paths above.
