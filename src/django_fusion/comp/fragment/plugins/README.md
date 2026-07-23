# `django_fusion.comp.fragment.plugins`

Frontend-library plugins for django-fusion fragment rendering.

## Plugins

- `htmx/` — HTMX detection, request wrapper (`HtmxDetails`), SSE, and response utilities.
- `unpoly/` — Unpoly server protocol implementation and Django adapter.

## Design

Each plugin is self-contained. The middleware in
`django_fusion.infrastructure.middlewares.site` attaches the appropriate
wrappers to the request:

- `request.htmx` — `HtmxDetails`
- `request.up` — `DjangoAdapter` / `Unpoly`

Fragment detection utilities in `comp.routes.detection` and
`ci._context_mixins` combine both plugins transparently.

## Adding a new fragment plugin

1. Create a new directory under this package.
2. Implement a request wrapper and detection helper.
3. Register the wrapper in `SiteMiddleware._preprocess_request`.
4. Update `is_fragment_request` to include the new library.
