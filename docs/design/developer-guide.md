---
title: Design & Frontend — Developer Guide
description: Hands-on recipes for building themes, components, SCSS partials, design tokens, django-fusion components, and dynamic template fields.
object:
  type: "guide"
  id: "docs.design.developer-guide"
attributes:
  source_path: "design/developer-guide.md"
  canonical_route: "/docs/en/design/developer-guide"
  section: "design"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - design
  - developer-guide
  - theme
  - scss
  - components
  - django-fusion
  - templates
links:
  - label: "Design suite home"
    to: "/design"
    icon: "i-lucide-palette"
---

# 🧑‍💻 Developer Guide — Design & Frontend Systems

> **Audience:** engineers implementing features.
> **Scope:** concrete recipes for the theme engine, SCSS architecture,
> components, design system, django-fusion, and dynamic template fields.
> Read the [Architecture Guide](architecture-guide.md) first if you need the
> big picture.

---

## 1. Theme Engine

### Purpose

Give your product a theme in **two files** and enable runtime switching with
zero component changes.

### Architecture

The engine remaps semantic `--fu-token-*` variables from raw per-theme
tokens based on `[data-theme]` on `<html>`. You never touch components.

### Examples

Create `projects/assets/theme/acme/tokens/_fu-acme-theme.scss`:

```scss
// Raw tokens — HSL channels only
:root, [data-theme="acme"] {
  --fu-acme-primary:    243 75% 59%;
  --fu-acme-secondary:  262 83% 58%;
  --fu-acme-accent:      24 95% 53%;
  --fu-acme-success:    152 69% 41%;
  --fu-acme-warning:     38 92% 50%;
  --fu-acme-error:        0 84% 60%;
  --fu-acme-info:       217 91% 60%;
  --fu-acme-surface:      0   0% 100%;
  --fu-acme-ink:        222 47% 11%;
  --fu-acme-muted:      215 16% 47%;
  --fu-acme-line:       214 32% 91%;
  --fu-acme-card:         0   0% 100%;
  --fu-acme-link:       243 75% 59%;
  --fu-acme-radius:      14px;
  --fu-acme-shadow:      0 20px 50px -20px hsl(243 75% 59% / 0.25);
  --fu-acme-font-display: "Inter", system-ui, sans-serif;
  --fu-acme-font-body:    "Inter", system-ui, sans-serif;
  --fu-acme-space:        4px;
  --fu-acme-max-width:    1200px;
}
```

Create `projects/assets/theme/acme/_index.scss`:

```scss
@import 'tokens/fu-acme-theme';
```

Register it in `projects/assets/theme/engine/_fu-engine.scss`:

```scss
[data-theme="acme"] { @include fu-theme-remap(acme); }
```

Import it from the master `projects/assets/theme/_index.scss`:

```scss
@import 'acme';
```

### Usage

```html
<html data-theme="acme">
```

Runtime switching in JavaScript:

```js
document.documentElement.dataset.theme = 'acme';
document.documentElement.classList.toggle('dark', prefersDark);
```

Add `.fu-theme-transition` to `<html>` once to animate the switch; the
engine respects `prefers-reduced-motion`.

### Customization

- **Dark mode:** add a `.dark { … }` block in your theme token file
  remapping the same raw token names.
- **Multi-brand:** `[data-brand="acme"]` override blocks in the engine
  remap semantic tokens per brand.
- **Derived themes:** `@include fu-theme-remap(saas)` inherits the whole
  semantic map; override individual tokens afterwards.

### Best Practices

- Always define all seven color roles plus surface/ink/muted/line/card/link.
- Store raw tokens as **HSL channels** (no `hsl()` wrapper) so the engine
  can compose alpha (`hsl(var(--fu-acme-primary) / 0.5)`).
- Validate with `npx sass projects/assets/theme/_index.scss` after
  registering.

---

## 2. SCSS Architecture

### Purpose

Keep the SCSS layered, partial-based, and consistent so any engineer can
find, extend, or restyle any UI.

### Architecture

```text
tokens/  →  engine/  →  theme components/  →  design-systems/  →  _index.scss
```

Import order is contract: tokens before components, engine before themes.

### Examples

Add a new partial for a product-specific widget:

```scss
// projects/assets/theme/lms/components/cards/_fu-lms-progress-card.scss
.fu-lms-progress-card {
  background: var(--fu-token-card);
  border: 1px solid var(--fu-token-line);
  border-radius: var(--fu-token-radius);
  padding: var(--fu-token-space-4);

  &__bar {
    height: 8px;
    background: var(--fu-token-surface);
    border-radius: 999px;
    overflow: hidden;
  }

  &__fill {
    height: 100%;
    background: var(--fu-token-primary);
    transition: width 0.4s ease;
  }

  &--complete .fu-lms-progress-card__fill {
    background: var(--fu-token-success);
  }
}
```

Then include it from `lms/_index.scss`:

```scss
@import 'components/cards/fu-lms-progress-card';
```

### Usage

```bash
# Validate the partial compiles (any entry point)
npx sass projects/assets/theme/lms/_index.scss

# Full suite
npx sass projects/assets/theme/_index.scss
```

### Customization

- Naming: `_fu-<theme>-<block>.scss` in shared themes; `_fu-<block>.scss`
  for engine-generic components.
- Nesting: BEM elements may nest, but never nest blocks inside blocks.
- Media queries live inside the block partial (mobile-first `min-width`).

### Best Practices

- No plain CSS files; every stylesheet is a `.scss` partial.
- No `@extend` across partials (complicates cascade); use modifiers.
- Keep `!important` out; raise specificity with BEM modifiers instead.

---

## 3. Components

### Purpose

Build accessible, theme-agnostic BEM components that behave identically in
every theme.

### Architecture

Component = HTML reference (in `theme/<theme>/templates/` or
`components/*.html`) + SCSS partial (in `components/`) + semantic tokens.

### Examples

Full component recipe — the SCSS partial:

```scss
// theme/default/components/_fu-alert.scss
.fu-alert {
  display: flex;
  gap: var(--fu-token-space-3);
  align-items: flex-start;
  padding: var(--fu-token-space-3) var(--fu-token-space-4);
  border: 1px solid var(--fu-token-line);
  border-radius: var(--fu-token-radius);
  background: var(--fu-token-surface);
  color: var(--fu-token-ink);

  &__icon  { flex: none; }
  &__title { font-weight: 600; }
  &__body  { color: var(--fu-token-muted); }

  &--success { border-color: hsl(var(--fu-token-success) / 0.4); background: hsl(var(--fu-token-success) / 0.08); }
  &--warning { border-color: hsl(var(--fu-token-warning) / 0.4); background: hsl(var(--fu-token-warning) / 0.08); }
  &--error   { border-color: hsl(var(--fu-token-error) / 0.4);   background: hsl(var(--fu-token-error) / 0.08); }
  &--info    { border-color: hsl(var(--fu-token-info) / 0.4);    background: hsl(var(--fu-token-info) / 0.08); }
}
```

And the HTML reference (Django template):

```django
<div class="fu-alert fu-alert--success" role="status">
  <span class="fu-alert__icon" aria-hidden="true">✓</span>
  <div>
    <p class="fu-alert__title">Payment received</p>
    <p class="fu-alert__body">Invoice {{ invoice.number }} is now paid.</p>
  </div>
</div>
```

### Usage

1. Copy the HTML into your product template.
2. Import the partial into your theme index.
3. Swap `--fu-token-*` values via the theme token file when restyling.

### Customization

- **New variant:** add a `--modifier` to the partial and a class in HTML.
- **New size:** `--sm` / `--lg` modifiers that scale `--fu-token-space-*`.
- **Product fork:** copy the partial into the product's own styles dir and
  extend; never edit shared partials for one product.

### Best Practices

- Semantic HTML + ARIA (`role="status"`, `aria-live` for toasts).
- Keyboard accessible; visible focus ring (`outline: 3px solid var(--fu-token-primary)`).
- Touch targets ≥ 44×44px (POS theme enforces this via `--fu-pos-touch`).

---

## 4. Design System

### Purpose

One source of truth for colors, typography, spacing, and grid that every
theme derives from.

### Architecture

`DESIGN-SYSTEM.md` → per-theme token files → engine semantic layer →
components. The eight variation themes in `THEME-VARIATIONS.md` demonstrate
the pattern (each is exactly two files).

### Examples

```scss
// Add a new semantic role to engine/_fu-tokens.scss
:root {
  --fu-token-focus-ring: hsl(var(--fu-token-primary) / 0.35);
}
// …and each theme already provides --fu-<theme>-primary, so no per-theme edit needed.
```

### Usage

Reference semantic tokens, not raw ones:

```scss
.box { color: var(--fu-token-ink); background: var(--fu-token-surface); }
```

Typography scale (defined in `DESIGN-SYSTEM.md`):

| Token | Size | Weight | Line height |
|---|---|---|---|
| `--fu-token-font-display` | clamp(2.5rem, 5vw, 4rem) | 700 | 1.05 |
| `--fu-token-font-h2` | clamp(1.75rem, 3vw, 2.5rem) | 700 | 1.15 |
| `--fu-token-font-body` | 1rem | 400 | 1.6 |
| `--fu-token-font-caption` | 0.8125rem | 500 | 1.5 |

### Customization

- **Recolor a theme:** edit its `tokens/_fu-<theme>-theme.scss` only.
- **New color role:** add `--fu-token-<role>` in the engine, then the raw
  token in every theme.
- **New typography system:** override `--fu-<theme>-font-*` in the theme
  token file; the variation themes show serif, mono, and display-first
  systems.

### Best Practices

- Keep semantic names stable; add, don't repurpose.
- Document every token in `DESIGN-SYSTEM.md` when you add it.
- Contrast: body ≥ 4.5:1, large text ≥ 3:1 (High Contrast = AAA).

---

## 5. Django Fusion

### Purpose

Render shared components, fragments, and emails from Django with the
framework's `TemplateRenderer` and `{% comp %}` tag.

### Architecture

```text
View/Handler ──▶ TemplateRenderer ──▶ template + {% comp %} ──▶ HTML/HTMX/JSON
```

Canonical package: `libs/django-fusion/` (import `django_fusion.*`, never
re-export shims).

### Examples

Render a fragment for HTMX:

```python
from django_fusion.core.rendering import TemplateRenderer

renderer = TemplateRenderer(request)
html = renderer.render_fragment(
    "cards/course-card",
    fragment_name="course-card",
    context={"course": course, "variant": "featured"},
)
```

Use it from a template:

```django
{% comp "cards/course-card" course=course variant="featured" / %}
```

Emails:

```python
from django_fusion.models.email import EmailTemplate

email = EmailTemplate.objects.get(slug="invoice-receipt")
message = email.render({"customer": customer, "order": order})  # uses TemplateRenderer
```

### Usage

- Register components under `libs/django-fusion/src/django_fusion/comp/`.
- Fragment responses carry HTMX headers; JSON responses for Astro clients
  follow the render-first contract (see `docs/18-render-contract.md`).
- Forms and tables: see `libs/django-fusion/docs/06-forms-and-tables.md`.

### Customization

- Override a component template per product via `TEMPLATES['DIRS']`
  (product templates win before framework templates).
- Extend `TemplateRenderer` for product-specific context processors.
- Add filters/tags in the framework's template library, not per product.

### Best Practices

- Keep business logic in services/managers; views stay thin.
- Preserve Wagtail context, translation tags, permissions, HTMX attrs.
- Run `cd libs/django-fusion && uv run pytest` after touching the framework.

---

## 6. Dynamic Templates

### Purpose

Let editors and operators author `{{ variable }}` templates that render
against live data — sandboxed, validated, and previewable.

### Architecture

Regex parser (no template-engine evaluation) → dotted-path resolver →
validation → escaping → filters → assembly → preview. Spec:
`docs/features/template-fields/`.

### Examples

```python
from django_fusion.templates.fields import TemplateRenderer  # provided by the system

renderer = TemplateRenderer()
result = renderer.render(
    "Invoice {{ invoice.number }} for {{ customer.name|upper }} — due {{ invoice.due_date|date:\"%Y-%m-%d\" }}",
    {"invoice": invoice, "customer": customer},
)
```

Define a schema for validation:

```python
from django_fusion.templates.fields import TemplateSchema, SchemaField, FieldType

schema = TemplateSchema(fields=[
    SchemaField(name="customer.name", type=FieldType.TEXT, required=True),
    SchemaField(name="order.total", type=FieldType.DECIMAL, required=True, allowlist=True),
    SchemaField(name="invoice.number", type=FieldType.TEXT, fallback="—"),
])
issues = schema.validate("{{ customer.name }} — {{ order.total }}")
```

### Usage

- Register custom filters in the filter registry (14 built-in: `date`,
  `upper`, `lower`, `default`, `currency`, `truncate`, `join`, `urlencode`, …).
- Configure limits/allowlists in Django settings (`TEMPLATE_FIELD_*`).
- Preview: `renderer.preview(template, sample_data)` returns watermarked
  output plus `ValidationIssue` list.

### Customization

- New filter: add a function to the registry and document it in
  `05-examples.md`.
- New field type: extend `FieldType` + the resolver's coercion table.
- New data source: register it in the source allowlist (default: models
  referenced by the owning product).

### Best Practices

- Never render user templates through `Template()` / Jinja — always the parser.
- Auto-escape; sanitize URLs (`https:`, `mailto:` only).
- Provide fallbacks for every optional variable; validate required ones
  before render; log audit entries on send.

---

## Verification Checklist

```bash
# SCSS: all themes + engine compile
npx sass projects/assets/theme/_index.scss

# django-fusion tests
cd libs/django-fusion && uv run pytest

# Product checks (example)
cd projects && make check WEBSITE=precis-main

# Docs validation
make -C docs check
```

## Remarks & Notes

- Theme names must be lowercase slugs (they become `data-theme` values).
- `npx sass` is available repo-wide; Dart Sass deprecation warnings about
  `@import` are expected — the repo convention is `@import`, not `@use`.
- The theme library currently ships 13 themes; import only what a product
  needs to keep bundles small.
- <!-- AI-generated: review needed -->
