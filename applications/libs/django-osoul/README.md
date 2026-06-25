# django-osoul

`django-osoul` is the merged Django helper library for Structa Cloud. Source code uses the `src/` layout under `src/django_osoul/`.

Former `django-osoul` functionality is merged into `django_osoul`. A minimal deprecated `django_osoul` compatibility shim remains and will be removed in a future release.

## Editable install

```bash
pip install -e applications/libs/django-osoul
```

## Features

- Cached model managers in `django_osoul.cache`.
- Component error logging middleware in `django_osoul.core.middlewares.component_error`.
- Smart loader decorator in `django_osoul.smart_loader`.
