---
title: Design & Frontend — Migration Guide
description: Upgrade paths from the archived theme, plain CSS, legacy hex tokens, and hardcoded templates to the shared fu-* theme system.
object:
  type: "guide"
  id: "docs.design.migration-guide"
attributes:
  source_path: "design/migration-guide.md"
  canonical_route: "/docs/en/design/migration-guide"
  section: "design"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - design
  - migration-guide
  - theme
  - scss
  - tokens
  - django-fusion
links:
  - label: "Design suite home"
    to: "/docs/en/design"
    icon: "i-lucide-palette"
---

# 🔄 Migration Guide — Design & Frontend Systems

> **Audience:** engineers upgrading existing code to the shared theme
> system.
> **Scope:** moving off `.archives/theme`, converting CSS→SCSS, adopting
> `--fu-*` tokens, migrating products to the theme engine, and adopting
> django-fusion + dynamic template fields.

---

## 1. Theme Engine — Adopting It in a Product

### Purpose

Get an existing product on the shared theme engine so it gains runtime
theming, dark mode, and multi-brand support.

### Architecture (before → after)

```text
BEFORE:  product-local styles with hardcoded colors
AFTER:   product imports theme + engine → components read --fu-token-*
```

### Examples

A product that currently styles everything locally (e.g.
`projects/precis/precis-main/assets/styles/`) migrates in four steps:

```scss
// 1. Import the shared theme + engine from the product entry point
@import '../../../assets/theme/lms';
@import '../../../assets/theme/engine';

// 2. (product entry keeps local partials that are not yet migrated)
@import 'components/product-specific';
```

```html
<!-- 3. Set the theme on the root element -->
<html data-theme="lms">
```

```scss
// 4. Product partials swap hardcoded values for semantic tokens
.button { background: var(--fu-token-primary); }
```

### Usage

1. Identify the product's SCSS entry point (product `assets/styles/_index.scss` or equivalent).
2. Import theme + engine above the product partials.
3. Set `data-theme` in the base template.
4. Iterate: replace hardcoded colors in product partials with tokens, one
   component family at a time.

### Customization

- Products with unique visuals keep product partials after the shared
  import — shared tokens win for everything already migrated.
- If the product needs its own palette, create a product theme (two files,
  see the [Developer Guide](developer-guide.md#1-theme-engine)) instead of
  inlining colors.

### Best Practices

- Migrate bottom-up: tokens first, then components, then pages.
- Verify with `npx sass` at each step; diff the compiled CSS for regressions.
- Don't delete product partials until the shared versions cover them.

---

## 2. SCSS Architecture — CSS → SCSS Conversion

### Purpose

Convert any remaining plain `.css` stylesheets to `.scss` partials so they
join the layered system (tokens → engine → components).

### Architecture

```text
*.css (hardcoded)  →  _*.scss partial (tokens)  →  imported by theme _index.scss
```

### Examples

BEFORE (`legacy.css`):

```css
.card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; }
```

AFTER (`theme/default/components/_fu-card.scss`):

```scss
.fu-card {
  background: var(--fu-token-surface);
  border: 1px solid var(--fu-token-line);
  border-radius: var(--fu-token-radius);
  padding: var(--fu-token-space-6);
}
```

### Usage

1. Move the file into the owning theme's `components/` (or `base/` for
   resets/typography) as a partial.
2. Rewrite selectors to BEM (`fu-<block>`) and values to tokens.
3. Update templates to the new class names.
4. Delete the old CSS file and its `<link>`/import.

### Customization

- Global resets/typography belong in the theme's `base/` equivalents; the
  shared `engine/components/` holds generic form/alert/nav/table styles.
- Keep `@import` (repo convention) rather than converting to `@use`.

### Best Practices

- One file per component; subdirectories per family (cards/, layout/…).
- No IDs for styling; no `!important`; mobile-first media queries.
- Run `npx sass projects/assets/theme/_index.scss` after conversion.

---

## 3. Design System — Legacy `--color-*` → `--fu-*` Tokens

### Purpose

Replace the legacy hex token set (documented in
`docs/dev/customization/design-system.md`) with the HSL semantic system.

### Architecture

| Legacy (hex) | New (semantic) |
|---|---|
| `--color-primary` | `--fu-token-primary` |
| `--color-primary-dark` | theme raw `--fu-<theme>-primary` dark variant via `.dark` |
| `--color-primary-light` | `hsl(var(--fu-token-primary) / 0.12)` |
| `--color-bg` | `--fu-token-surface` |
| `--color-bg-subtle` | `--fu-token-card` or `hsl(var(--fu-token-surface) / 0.6)` |
| `--color-border` | `--fu-token-line` |
| `--color-text` | `--fu-token-ink` |
| `--color-text-muted` | `--fu-token-muted` |
| `--color-success/warning/error/info` | `--fu-token-success/warning/error/info` |

### Examples

```css
/* BEFORE */
.card { color: #111827; background: #ffffff; border-color: #e5e7eb; }

/* AFTER */
.card { color: var(--fu-token-ink); background: var(--fu-token-surface); border-color: var(--fu-token-line); }
```

### Usage

1. `rg --color` across the product to find every legacy token.
2. Map per the table above (see `engine/_fu-tokens.scss` for the full list).
3. Dark mode: legacy code used `[data-theme="dark"]` blocks — new code gets
   dark remapping free from the engine's `.dark` blocks.

### Customization

- Keep the legacy `--color-*` names alive in a small compatibility partial
  during the transition, then delete it:
  `:root { --color-primary: var(--fu-token-primary); … }`
- Spacing: legacy `--space-*`/`--radius-*` map to `--fu-token-space-*` /
  `--fu-token-radius`.

### Best Practices

- Migrate semantic names, not hex values — never reintroduce raw hex.
- Check contrast after migration (target ≥ 4.5:1 body).
- Remove the compatibility partial within one release.

---

## 4. Components — Legacy Classes → `fu-*` BEM

### Purpose

Standardize on the shared BEM catalog so behavior, states, and
accessibility are identical everywhere.

### Architecture

```text
Legacy: .button .button--primary .card-title (flat, per-product)
Shared: .fu-btn .fu-btn--primary .fu-card__title (BEM, per-library)
```

### Examples

| Legacy | Shared equivalent |
|---|---|
| `.button` / `.btn` | `.fu-btn` (+ `--primary`, `--ghost`, `--danger`, `--sm`, `--lg`) |
| `.card`, `.card-title` | `.fu-card`, `.fu-card__title` |
| `.badge` | `.fu-badge` |
| `.alert`, `.alert-success` | `.fu-alert`, `.fu-alert--success` |
| `.table` | `.fu-table` (+ `--striped`, `--bordered`, `--compact`) |
| `.pagination a` | `.fu-pagination__link` |
| `.breadcrumb li` | `.fu-breadcrumb__item` |

### Examples

```html
<!-- BEFORE -->
<div class="card">
  <h3 class="card-title">Structural Analysis I</h3>
  <a class="btn btn-primary" href="#">Enroll</a>
</div>

<!-- AFTER -->
<div class="fu-card">
  <h3 class="fu-card__title">Structural Analysis I</h3>
  <a class="fu-btn fu-btn--primary" href="#">Enroll</a>
</div>
```

### Usage

1. Map the product's classes to shared components (table above).
2. Update templates; remove product partials that duplicate shared ones.
3. Keep product-specific components as `fu-<product>-<block>` partials
   (e.g. `fu-lms-course-card`) inside the product's theme dir.

### Customization

- If the product needs a variant, add a `--modifier` to the shared partial
  (upstream it) rather than forking.
- If behavior must differ, fork only the component partial into the product
  styles and import it after the shared theme.

### Best Practices

- Delete dead stylesheets as you go; `rg` for old class names to find
  stragglers.
- Verify with `npx sass` and visual smoke tests on key pages.

---

## 5. Django Fusion — Hardcoded Templates → `{% comp %}`

### Purpose

Replace copied/inlined HTML with registered framework components so updates
propagate everywhere.

### Architecture

```text
BEFORE: <div class="fu-card">…</div> inline in every template
AFTER:  {% comp "cards/course-card" course=course / %}
```

### Examples

Register a component (framework package):

```python
# libs/django-fusion/src/django_fusion/comp/components/cards/course_card.py
from django_fusion.comp import Component

class CourseCard(Component):
    template_name = "components/cards/course_card.html"
```

Use it everywhere:

```django
{% comp "cards/course-card" course=course variant="featured" / %}
```

HTMX fragments migrate to `render_fragment(..., fragment_name=…)`.

### Usage

1. Identify repeated HTML blocks (cards, alerts, buttons, tables).
2. Register each as a component; replace inline markup with `{% comp %}`.
3. For dynamic template fields, add `field_schema` to models that render
   user-authored text (e.g. `EmailTemplate`).

### Customization

- Product-specific markup stays in the product, but should call shared
  components internally.
- Overrides per product via `TEMPLATES['DIRS']` — same component name,
  product template wins.

### Best Practices

- Preserve Wagtail context, translation tags, permissions, HTMX attributes
  during migration.
- Keep `fragment_name` identical across views using the same fragment.
- Run `cd libs/django-fusion && uv run pytest` and the product's
  `make check` after migration.

---

## 6. Dynamic Templates — String Interpolation → Template Fields

### Purpose

Replace manual `f"...{customer.name}..."` formatting and unsafe `format()`
calls with the sandboxed dynamic template field system.

### Architecture

```text
BEFORE: f"Dear {customer.name}, your order is {order.total}"   (no validation, no escaping, no preview)
AFTER:  renderer.render("Dear {{ customer.name }}, your order is {{ order.total }}", {...})
        → validated · escaped · filterable · previewable
```

### Examples

BEFORE (Django view):

```python
subject = f"Your invoice {invoice.number} is ready"
body = f"Hi {customer.name}, total {order.total}"
```

AFTER:

```python
from django_fusion.templates.fields import TemplateRenderer  # provided by the system

renderer = TemplateRenderer()
subject = renderer.render("Your invoice {{ invoice.number }} is ready", {"invoice": invoice})
body = renderer.render(
    "Hi {{ customer.name }}, total {{ order.total|currency }}",
    {"customer": customer, "order": order},
)
```

### Usage

1. Find every f-string/`format()` that interpolates record data into user-
   facing text (emails, receipts, certificates, notifications).
2. Replace with template strings + `renderer.render(...)`.
3. Add a `TemplateSchema` where inputs are user-editable so editors get
   validation and preview.
4. Remove any `mark_safe` on interpolated output — the renderer escapes.

### Customization

- Keep the old Python formatting for internal/system messages that users
  never edit; migrate user-editable templates first.
- Register product-specific filters in the registry when needed.

### Best Practices

- Never render user-authored strings with `Template()`/Jinja — the regex
  parser is the only allowed path (prevents SSTI).
- Provide fallbacks for optional fields; preview before send.
- Delete old formatting helpers after migration to avoid dual paths.

---

## Rollback Plan

| Step | Action |
|---|---|
| 1 | Keep the old CSS/template files until the release ships (git history preserves them beyond that) |
| 2 | Feature-flag theme activation (`data-theme` from settings, not hardcoded) |
| 3 | If a regression appears: revert to the product's previous entry point (git revert of the entry-point commit) |
| 4 | The compatibility partial (`--color-*` aliases) buys time during token migration |
| 5 | Dynamic template migration is additive: old `f-string` path can be kept behind a setting until templates are converted |

## Migration Checklist

- [ ] Product imports theme + engine; `data-theme` set in base template
- [ ] `npx sass` passes for product entry point and master index
- [ ] All legacy `--color-*` usages replaced (or aliased temporarily)
- [ ] Legacy classes mapped to `fu-*` BEM; old partials deleted
- [ ] Repeated HTML moved to `{% comp %}`; fragments use `fragment_name`
- [ ] User-editable strings render through the template-field renderer
- [ ] Dark mode + High Contrast verified on key screens
- [ ] `make check WEBSITE=<product>` and django-fusion pytest pass
- [ ] Docs updated (this suite, `DESIGN-SYSTEM.md`, `THEME-VARIATIONS.md`)

## Remarks & Notes

- `.archives/theme/` is a kept archive: its components were extracted into
  `projects/assets/theme/` (273 files) — do not build new work on the
  archive, but do not delete it without a plan (git history preserves it).
- The legacy `--color-*` hex tokens in `docs/dev/customization/design-system.md`
  are superseded by `--fu-token-*`; that page is kept for historical
  reference and cross-linkage.
- Theme slugs must match `data-theme` values exactly; products should pin
  one theme + engine, not the master index, for bundle size.
- <!-- AI-generated: review needed -->
