# Design: Core

## Overview

Web layer — allauth adapters, auth backends, view mixins, and rendering.

## Directory

Path: `django_fusion/core`


### Modules
- `rendering.py`

## Architecture

```mermaid
flowchart LR
    Request --> core
    {package_name} --> Response
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.core.rendering import TemplateRenderer

renderer = TemplateRenderer.get_default()

# Render a template to a string
html = renderer.render("emails/welcome.html", {"name": "Alice"}, request)

# Render an email bundle (HTML + text + subject)
email = renderer.render_email(
    "emails/welcome.html",
    context={"name": "Alice"},
    subject="Welcome!",
)

# Return an HttpResponse
response = renderer.render_to_response("pages/home.html", {"title": "Home"}, request)
```

## Commands / Entry Points

*No management commands are defined here by default.*

If this package exposes management commands, list them below:

```bash
python manage.py <command_name>
```

## Related Documentation

- [Django docs](https://docs.djangoproject.com/)
- [Wagtail docs](https://docs.wagtail.io/)
- Other `django_fusion` packages: see the root `design.md`.
