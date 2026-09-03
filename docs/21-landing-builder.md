# Landing Builder (DF-021)

> **Status:** ✅ Exists · **Source:** `src/django_fusion/builder/`
> **Consumers:** Loop-CRM reference mount (`apps.pages.BuilderPage`)

## Purpose

The landing builder assembles landing pages from the shared `fu-*` component
catalog on top of Wagtail, with three levers per page:

1. **Theme picking** — every page stores a `theme` (and optional `brand` /
   `dark_mode`) that the renderer emits as `data-theme` / `data-brand` /
   `.dark` on `<html>`, activating the theme engine's token remap.
2. **Section assembly** — editors compose a StreamField from generic,
   theme-agnostic section blocks (hero, features, steps, stats, pricing, FAQ,
   CTA) that render through `builder/sections/<type>.html` partials composing
   the `fu-*` BEM components.
3. **Dynamic template fields** — any text value may contain
   `{{ company.name }}` placeholders resolved against the page's
   `template_context` by the sandboxed engine (see DF-022).

It is the thin assembly layer that turns three duplicated landing shells
(Precis, CTC, Loop-CRM) into one reusable surface, and the first real
consumer of the shared theme engine.

## Architecture

```text
Wagtail admin (/cms/)
   │  BuilderPage (abstract, django_fusion.builder.models)
   │    ├─ theme / brand / dark_mode   → theme engine activation
   │    ├─ template_context (JSON)     → dynamic field values
   │    └─ sections (StreamField)      → section blocks
   ▼
BuilderRenderer (django_fusion.builder.rendering)
   │  1. flatten stream → plain dicts (PageChooser → URLs)
   │  2. resolve {{ var }} via TemplateFieldEngine (+ URL sanitization)
   │  3. render section partials (fu-* components)
   ├─► server HTML (Wagtail preview / public template)
   └─► to_dict() JSON (data-API road)
   ▼
django_fusion.builder.api  →  GET /builder/pages/  ·  GET /builder/pages/<slug>/
```

The abstract `BuilderPage` has no table; each consuming product subclasses it
concretely. The API discovers concrete subclasses automatically.

## Examples

### Mount in a product (Loop-CRM reference)

```python
# apps/pages/models.py
from django_fusion.builder.models import BuilderPage as FusionBuilderPage

class BuilderPage(FusionBuilderPage):
    template = "builder/page.html"
    parent_page_types = ["pages.HomePage"]
    subpage_types = []
```

```python
# settings INSTALLED_APPS — enables builder templates + static
"django_fusion.builder",
```

```python
# urls.py — the data-API road
from django_fusion.builder.api import builder_page_data, builder_page_list
path("apis/builder/", builder_page_list, name="builder_page_list"),
path("apis/builder/<slug:slug>/", builder_page_data, name="builder_page_data"),
```

### Render a page programmatically

```python
from apps.pages.models import BuilderPage

page = BuilderPage.objects.get(slug="saas-launch").specific
renderer = page.get_builder_renderer()
renderer.theme_attrs()      # 'data-theme="saas" data-brand="loop"'
renderer.sections_html()    # composed fu-* section HTML
renderer.to_dict()          # JSON payload (theme + resolved sections + issues)
```

## Usage

- **Editors** compose pages in Wagtail: add sections, pick a theme/brand/dark
  mode in the Theme panel, and store dynamic-field values in
  `template_context` (e.g. `{"company": {"name": "Structa Cloud"}}`).
- **Frontends** consume `/apis/builder/<slug>/` (resolved JSON) instead of
  duplicating the landing shell.
- **Previews** render server-side through `builder/page.html`; in preview
  mode a sticky bar reports unresolved dynamic fields.

## Customization

| Need | How |
|---|---|
| Own page shell | Override `template` on the concrete subclass (extend `builder/page.html`). |
| Own theme CSS | Override the `theme_css` block to link your compiled theme SCSS. |
| Own section set | Subclass `BuilderPage` and override `sections` StreamField with your block list. |
| Own section markup | Override `builder/sections/<type>.html` in your templates dir. |
| Extra renderer behavior | Override `get_builder_renderer()` on the concrete model. |
| Extra context values | Pass `context_override` to the renderer (previews, A/B). |

## Best practices

- Keep blocks theme-agnostic — styling lives in the section templates and the
  theme engine, never in block field help text.
- Use `template_context` for dynamic values; never hard-code per-tenant copy.
- Validate with `renderer.preview_issues()` before publishing; unresolved
  fields render empty (fail-safe) but should be fixed.
- Compile the full theme SCSS (`projects/assets/theme/_index.scss`) into your
  pipeline rather than shipping the lean reference build for production.

## Remarks & Notes

- The reference mount lives in Loop-CRM (`apps.pages.BuilderPage`,
  `seed_builder`, `/apis/builder/`). Other products mount the same abstract
  model.
- The abstract model produces no migrations; the concrete subclass does.
- `django_fusion.builder.__init__` must stay import-light (no Wagtail model
  imports) — Django imports it before the app registry is populated.
