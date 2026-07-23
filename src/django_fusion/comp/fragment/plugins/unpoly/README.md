# `django_fusion.comp.fragment.plugins.unpoly`

Unpoly plugin for django-fusion fragments.

## API

- `Unpoly` — Main request wrapper implementing the Unpoly server protocol.
- `Layer` — Represents a Unpoly overlay layer.
- `BaseAdapter` — Framework-agnostic adapter interface.
- `DjangoAdapter` — Django request/response adapter.

## Example

```python
from django_fusion.comp.fragment.plugins.unpoly import DjangoAdapter


def my_view(request):
    request.up = DjangoAdapter(request)
    request.up.set_title("My Page")
    if request.up.layer.is_overlay:
        request.up.layer.accept()
```

## Backward compatibility

- `django_fusion.comp.loader.up.Unpoly`
- `django_fusion.ci.adapters.main.DjangoAdapter`

still work. New code should prefer the paths above.
