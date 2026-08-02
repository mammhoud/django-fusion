# `django_fusion.plugins.unpoly`

Unpoly plugin for django-fusion fragments.

## API

- `Unpoly` — Main request wrapper implementing the Unpoly server protocol.
- `Layer` — Represents a Unpoly overlay layer.
- `BaseAdapter` — Framework-agnostic adapter interface.
- `DjangoAdapter` — Django request/response adapter.

## Example

```python
from django_fusion.plugins.unpoly import DjangoAdapter


def my_view(request):
    request.up = DjangoAdapter(request)
    request.up.set_title("My Page")
    if request.up.layer.is_overlay:
        request.up.layer.accept()
```

Use the canonical `django_fusion.plugins.unpoly` imports above. Legacy package
paths are not part of the public API.
