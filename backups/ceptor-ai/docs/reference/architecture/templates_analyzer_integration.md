# Templates ↔ Analyzer Integration

> **Related Code**
> * **Domain:** Static analysis / Template instrumentation
> * **Paths:**
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/__init__.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/parser.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/scanner.py`
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/views.py`
> * **Submodules:** parser, scanner, schemas, views, urls

The analyzer walks the workspace templates and emits a single JSON document describing what it found. Templates with sections (see `templates_sections.md`) emit a `sections: list[Section]` field that lets frontend tooling map page structure back to source.

## Data flow

```
1. POST /api/analyzer/        (django-fusion.analyzer.views.AnalyzeView)
     ↓
2. scan(roots, depth, filters)         (analyzer.scanner.scan)
     lists files matching include_extensions / exclude_patterns
     ↓
3. for each file: parse_template(content)  (analyzer.parser.parse_template)
     extracts extends, blocks, comps, sections
     ↓
4. Template dataclass ← SectionMarker list    (schemas.Section)
     with stable cross-commit id = sec--<path_slug>--<name_slug>
     ↓
5. JsonResponse {website, components, templates[], pages[], summary}
```

## What gets emitted per Template

| Field         | Source                                            | Stable across commits? |
|---------------|---------------------------------------------------|:---------------------:|
| `id`          | `_id("tpl")` UUID                                 | NO                     |
| `name`        | `_humanize(sf.path.name)` (`contact.html` → `Contact`) | PATH-derived, yes |
| `path`        | relative path from TEMPLATES_DIRS root            | YES                    |
| `category`    | first URL segment (`contact` → `Contact`)        | PATH-derived           |
| `extends`     | `{% extends "X" %}`                               | YES                    |
| `blocks`      | `{% block NAME %}` names dedup'd                  | YES                    |
| **`sections`**| `{@section: name #}` + `data-section-id="n"`     | YES via `id` slug      |

## Pages

One `Page` is emitted per top-level template (extends base OR named `base.html`). Components' usages (`PageComponentUsage`) attach to the most recent Page encountered in source order — useful for diffing a page's component density across commits.

## Validation against `dictionaries/`

Run `python3 -c "import json; json.loads(open('/api/analyzer/').read())"` (or POST via curl) to validate the JSON contract. The `AnalyzeRequest` dataclass accepts:

```json
{
  "website_slug": "ctc-research",
  "url": "https://ctc-research.com",
  "include_components": true,
  "include_templates": true,
  "depth": 3,
  "filters": {"exclude_patterns": ["admin"], "include_extensions": [".html"]}
}
```

## Common integration patterns

* **Per-website page catalog**: feed the analyzer JSON to a docsify custom plugin to auto-generate "Pages by category" sections.
* **Coverage reports**: count `sections` per template → emit a markdown "Sections without components" gap report.
* **Refactor scanner**: pre-migration snapshots + post-migration snapshots → diff `sections` lists to confirm logical-region preservation.

See `docs/development/analyzer.md` for installation, configuration, and endpoint URL setup.
