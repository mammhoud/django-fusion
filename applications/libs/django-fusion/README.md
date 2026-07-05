# django-fusion

`django-fusion` is the merged Django helper library for Structa Cloud. Source code uses the `src/` layout under `src/django_fusion/`.

Former `django-fusion` functionality is merged into `django_fusion`. A minimal deprecated `django_fusion` compatibility shim remains and will be removed in a future release.

## Editable install

```bash
pip install -e applications/libs/django-fusion
```

## Features

- Cached model managers in `django_fusion.cache`.
- Component error logging middleware in `django_fusion.core.middlewares.component_error`.
- Smart loader decorator in `django_fusion.smart_loader`.
