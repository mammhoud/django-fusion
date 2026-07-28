# Component & Template Analyzer (django_fusion.analyzer)

> **Related Code**
> * **Domain:** Static analysis API
> * **Paths:**
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/__init__.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/parser.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/scanner.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/schemas.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/views.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/urls.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/apps.py`
> * **Submodules:** parser, scanner, schemas, views, urls

The analyzer is a `DjangoTemplates`-aware static analyzer. It walks the configured template directories, parses every file in scope, and returns a single JSON document describing each template's `extends` chain, `{% block %}` declarations, `{% comp %}` invocations, and analyzable "sections" (see `architecture/templates_sections.md`).

## Install

```python
# applications/<site>/settings.py
INSTALLED_APPS += ["django_fusion.analyzer.apps.AnalyzerAppConfig"]
```

## Endpoints

| Method  | Path                  | Returns                                  |
|---------|-----------------------|------------------------------------------|
| `POST`  | `/api/analyzer/`      | The full JSON spec (see schema below).    |
| `OPTIONS` | `/api/analyzer/`   | 204 No Content (CORS preflight).         |

URLs come from `applications/libs/django-fusion/src/django_fusion/analyzer/urls.py`:

```python
path("analyze/", AnalyzeView.as_view(), name="analyzer_analyze"),
```

## Request schema

`AnalyzeRequest` dataclass (in `schemas.py`) — constructed directly in the view from validated POST JSON:

```python
AnalyzeRequest(
    website_slug=None,           # str | None
    url=None,                    # str | None
    include_components=True,     # bool
    include_templates=True,      # bool
    depth=3,                     # int (clamped to [1, MAX_DEPTH=10])
    filters={},                  # dict
)
```

## Response schema (top-level)

```json
{
  "status": "success",
  "website": {
    "name": "<slug|Website>",
    "slug": "<slug|default>",
    "base_url": "<url|''>",
    "analyzed_at": "2026-07-07T00:00:00Z"
  },
  "components": [
    {"id": "comp_<uuid>", "name": "Card", "path": "components/card.html", "category": "Components", "props": [], "slots": []}
  ],
  "templates": [
    {
      "id": "tpl_<uuid>",
      "name": "Contact",
      "path": "contact/form_field.html",
      "category": "Contact",
      "extends": "base.html",
      "blocks": [
        {"name": "content", "description": "", "optional": false}
      ],
      "sections": [
        {"id": "sec--contact-form-field-html--field-icon", "name": "Field Icon", "marker_type": "comment", "line": 17}
      ]
    }
  ],
  "pages": [
    {"id": "page_<uuid>", "title": "Contact", "path": "contact.html", "template": "base.html", "components": [{"component_id": "comp_<uuid>", "props": {"title": "Hello"}}]}
  ],
  "summary": {
    "total_components": 1,
    "total_templates": 1,
    "total_pages": 1
  }
}
```

## Programmatic use

```python
from django_fusion.analyzer import parse_template, scan

parsed = parse_template(template_string)
print(parsed.sections)
# [SectionMarker(name='Hero', marker_type='comment', line=4), ...]

files = scan(template_dirs=['/home/structa.cloud/applications/assets/templates'], depth=3)
for f in files:
    print(f.relative_path, len(parse_template(f.content).comps))
```

## Concurrency

The view is stateless and thread-safe. Cap the `depth` field at 10 server-side (`MAX_DEPTH = 10`) to prevent malicious clients from triggering infinite filesystems walks. `Scan()` also enforces this cap regardless of whether you go through the view.

## See also

* [`../architecture/templates_analyzer_integration.md`](../../reference/architecture/templates_analyzer_integration.md) — how templates integrate with the analyzer.
* [`../architecture/templates_sections.md`](../../reference/architecture/templates_sections.md) — section marker conventions.
