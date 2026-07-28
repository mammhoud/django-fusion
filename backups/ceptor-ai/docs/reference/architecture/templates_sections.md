# Templates Sections — Concluded-Section Pattern

> **Related Code**
> * **Domain:** Templates / Section markers
> * **Paths:**
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/parser.py` (`SECTION_COMMENT_RE`, `SECTION_HTML_RE`)
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/schemas.py` (`Section` dataclass)
>   * `applications/libs/django-fusion/src/django_fusion/analyzer/views.py` (`_section_id`, `_slug`)
> * **Module:** `django_fusion.analyzer`

A "section" is a logical region of a page that the analyzer can track across commits. Sections are how `{% comp %}`-based compositions become queryable — the analyzer returns them per template so frontend tools and docs can map sections back to source code without parsing HTML at runtime.

## Two accepted forms

### Form A — Django comment (analyzer-only, invisible at render)

```django
{# @section: Hero Banner #}
<div class="hero">…</div>
{# @section: Contact Form #}
<form>…</form>
```

The `@section:` keyword shoulder is REQUIRED so plain visual separators (`{# ---- Title ---- #}`) are NOT picked up.

### Form B — HTML wrapper (frontend-visible, analyzer-tracked)

```html
<section data-section-id="contact-form">
  <form>…</form>
</section>
```

The `data-section-id="<name>"` attribute is the authoritative markup. Frontends can target it for HTMX swaps, focus management, and analytics.

## Hybrid resolution

When both forms declare the same name in the same template:

* The HTML form WINS for `marker_type`.
* The HTML form WINS for `line` (the analyzer surfaces the HTML wrapper line so consumers jump to the markup, not the comment).

Dedup is by name: re-declaring `{@section: Hero}` elsewhere in the SAME template yields ONE analyzer entry, not two.

## Output schema

Each `Template` returned by `POST /api/analyzer/` carries:

```json
{
  "id": "tpl_<uuid>",
  "path": "contact.html",
  "extends": "base.html",
  "blocks": […],
  "sections": [
    {"id": "sec--contact-html--hero",      "name": "Hero",      "marker_type": "comment", "line": 12},
    {"id": "sec--contact-html--contact-form", "name": "contact-form", "marker_type": "html", "line": 41}
  ]
}
```

Section IDs are deterministic (`sec--<path_slug>--<name_slug>`) so frontend/diffs across rebuilds are stable.

## Adoption cookbook

1. Pick which sections of `applications/<site>/templates/<page>/main.html` you want to track.
2. Add `{# @section: <name> #}` comments OR wrap blocks in `<section data-section-id="<name>">`.
3. Re-run the analyzer — sections appear automatically in the JSON output.

See `docs/architecture/templates_analyzer_integration.md` for how the analyzer walks templates, and `docs/development/analyzer.md` for the analyzer API surface.
