---
title: Design & Frontend — Architecture Guide
description: How the theme engine, SCSS architecture, component system, design system, django-fusion, and dynamic template fields fit together.
object:
  type: "guide"
  id: "docs.design.architecture-guide"
attributes:
  source_path: "design/architecture-guide.md"
  canonical_route: "/docs/en/design/architecture-guide"
  section: "design"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - design
  - architecture
  - theme
  - scss
  - components
  - django-fusion
links:
  - label: "Design suite home"
    to: "/docs/en/design"
    icon: "i-lucide-palette"
---

# 🏛️ Architecture Guide — Design & Frontend Systems

> **Audience:** architects and senior engineers.
> **Scope:** how the shared theme engine, SCSS layers, component system,
> design tokens, django-fusion rendering, and dynamic template fields
> compose into one coherent frontend architecture.

---

## 1. Theme Engine

### Purpose

The theme engine (`projects/assets/theme/engine/`) lets one component
codebase serve many products — CRM, POS, LMS, landing pages, and future
products — by remapping **semantic tokens** (`--fu-token-*`) to whichever
theme is active, at runtime, with zero JavaScript layout recalculations.

### Architecture

```text
┌──────────────────────────────  THEME ENGINE  ──────────────────────────────┐
│                                                                             │
│  Raw theme tokens            Semantic aliases          Components          │
│  ┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐  │
│  │ --fu-saas-primary   │     │ --fu-token-primary│    │ .fu-btn         │  │
│  │ --fu-lms-surface    │ ──▶ │ --fu-token-bg     │ ──▶ │ .fu-card        │  │
│  │ --fu-pos-ink        │     │ --fu-token-ink    │     │ .fu-crm-table   │  │
│  │ … (per-theme files) │     │ … (engine tokens) │     │ … (shared BEM)  │  │
│  └─────────────────────┘     └──────────────────┘     └─────────────────┘  │
│        ▲                            ▲                       ▲               │
│        │ [data-theme]               │ [data-brand]          │ nothing      │
│        │ attribute                  │ attribute              │ theme-      │
│        │ selector                   │ selector               │ specific    │
│        │                            │                        │             │
│  theme/<name>/tokens/         engine/_fu-tokens.scss   theme/<name>/      │
│  _fu-<name>-theme.scss                               components/          │
└─────────────────────────────────────────────────────────────────────────────┘
```

Three-layer token model (see `engine/_fu-tokens.scss` and `_fu-engine.scss`):

1. **Raw layer** — `--fu-<theme>-*` HSL values per theme (`tokens/`).
2. **Semantic layer** — `--fu-token-*` aliases defined once in the engine
   and remapped per `[data-theme]`.
3. **Component layer** — BEM partials consume only semantic tokens, so
   components are theme-agnostic by construction.

### Examples

```scss
// engine/_fu-engine.scss — one activation line per theme
[data-theme="saas"] { @include fu-theme-remap(saas); }
[data-theme="pos"]  { @include fu-theme-remap(pos); }
```

```html
<html data-theme="saas" data-brand="structa" class="dark">
```

### Usage

Products import the engine plus their theme(s) and set `data-theme` on the
`<html>` element. `prefers-reduced-motion` and `.fu-theme-transition` handle
smooth runtime switching.

### Customization

- Add a theme: token file + one `[data-theme] { @include fu-theme-remap(t); }` line — no component changes.
- Add a brand: `[data-brand="acme"]` override block remapping semantic tokens.
- Dark mode: `.dark` blocks inside each theme remap the same semantic tokens.

### Best Practices

- Components must **never** reference raw `--fu-<theme>-*` tokens.
- Keep raw tokens as HSL channels (`hsl(var(--fu-saas-primary))`) so alpha
  compositing works.
- One theme per product at build time; multiple themes only where the
  product genuinely needs runtime switching.

---

## 2. SCSS Architecture

### Purpose

A layered, partial-based SCSS architecture shared across all products:
raw stylesheets never ship; every theme compiles from small BEM partials.

### Architecture

```text
projects/assets/theme/
├── engine/                        # semantic tokens + switching
│   ├── _fu-tokens.scss
│   ├── _fu-engine.scss
│   ├── components/                # generic BEM: form, alert, nav, table
│   └── _index.scss
├── default/  lms/  crm/  pos/     # product themes
│   ├── tokens/_fu-<theme>-theme.scss
│   ├── components/                # BEM partials, organized by subdir
│   │   ├── cards/  layout/  tables/  pipeline/  products/  …
│   ├── templates/                 # HTML reference templates
│   ├── design-systems/            # higher-order variations
│   └── _index.scss                # theme entry point
├── saas/ enterprise/ corporate/ educational/ …   # variation themes
└── _index.scss                    # master entry (all themes + engine)
```

Compile entry points are plain `@import` chains (the repo convention):

```scss
// theme/_index.scss (master)
@import 'engine';   // semantic layer first
@import 'default';
@import 'lms';
@import 'crm';
@import 'pos';
@import 'saas';
// …
```

Import order matters: tokens → engine → theme components → design systems.

### Examples

```bash
# Validate any entry point with zero output artifacts
npx sass projects/assets/theme/_index.scss
```

### Usage

A product imports one theme + the engine:

```scss
// e.g. projects/precis/precis-main/assets/styles/_index.scss
@import '../../assets/theme/lms';
@import '../../assets/theme/engine';
```

### Customization

Add a new partial under `theme/<theme>/components/<group>/`, then include it
from that theme's `_index.scss`. Never edit generated CSS — only SCSS
partials are authored.

### Best Practices

- BEM naming throughout: `.fu-<block>`, `.fu-<block>__<element>`, `.fu-<block>--<modifier>`.
- One concern per partial; subdirectories mirror component groups.
- No IDs for styling, no plain CSS files in the theme library.

---

## 3. Components

### Purpose

A shared BEM component catalog gives every product the same behavior,
states, and accessibility with theme-specific looks.

### Architecture

```text
HTML template (reference)          SCSS partial                    Token
┌──────────────────────────┐       ┌──────────────────────┐        ┌──────────────┐
│ <div class="fu-card      │       │ .fu-card {           │        │ --fu-token-  │
│      fu-card--featured">│       │   background:         │ ─────▶ │ surface,     │
│   <div class="fu-card__  │       │     var(--fu-token-   │        │ ink, radius, │
│     media">…             │       │     surface); …       │        │ shadow …     │
└──────────────────────────┘       └──────────────────────┘        └──────────────┘
        component HTML                   component SCSS              semantic tokens
        (templates/, copied              (components/_fu-*.scss)
        into products)
```

Component families in the library:

| Family | Examples |
|---|---|
| Core | `fu-btn`, `fu-badge`, `fu-card`, `fu-modal`, `fu-form` fields |
| Layout | `fu-header`, `fu-footer`, `fu-nav`, `fu-megamenu`, `fu-sidebar` |
| Content | `fu-accordion`, `fu-breadcrumb`, `fu-section-title`, `fu-pagination` |
| Social proof | `fu-team`, `fu-testimonial`, `fu-counter`, `fu-pricing`, `fu-progressbar` |
| Data | `fu-table`, `fu-crm-table`, `fu-crm-pipeline`, `fu-pos-register` |
| Product | `fu-lms-course-card`, `fu-pos-product-card`, `fu-pos-receipt`, `fu-crm-contact-card` |
| Feedback | `fu-alert`, `fu-social`, `fu-kpi` |

### Examples

```html
<div class="fu-card fu-card--featured">
  <div class="fu-card__media"><img src="course.jpg" alt="Course cover"></div>
  <div class="fu-card__body">
    <h3 class="fu-card__title">Structural Analysis I</h3>
    <p class="fu-card__meta">12 modules · 6h 30m</p>
  </div>
  <div class="fu-card__actions"><a class="fu-btn fu-btn--primary" href="#">Enroll</a></div>
</div>
```

### Usage

Copy the reference HTML from `theme/<theme>/templates/` or the matching
`components/*.html` snapshot into product templates, then apply the partial.
Django products prefer registered `{% comp %}` components (see §5).

### Customization

- Look & feel: override tokens — never the component partial.
- Variant: add a BEM modifier to the partial (`fu-btn--ghost`).
- Product-specific behavior: fork into the product's own partial that
  extends the shared one; do not edit shared partials for one product.

### Best Practices

- One block per file; elements and modifiers in the same file.
- Semantic HTML first; BEM classes second; ARIA third.
- Touch targets ≥ 44×44px for POS; keyboard focus visible everywhere.

---

## 4. Design System

### Purpose

One specification (`projects/assets/theme/DESIGN-SYSTEM.md`) defines colors,
typography, spacing, grid, and component standards for every product, with
per-theme values expressed as tokens rather than hardcoded hex.

### Architecture

```text
DESIGN-SYSTEM.md  ── defines ──▶  7 color roles × 4 base themes
                                  (primary, secondary, accent, success,
                                   warning, error, neutral)
                                  + typography scale (display → caption)
                                  + spacing scale (--fu-token-space-*)
                                  + grid (container widths, breakpoints)
                                          │
        token files  theme/default/tokens/_fu-default-theme.scss  etc.
                                          │  (HSL values)
        semantic     engine/_fu-tokens.scss  --fu-token-*
                                          │
        components   theme/<theme>/components/_fu-*.scss
```

Design-system variations (higher-order layers) live in each theme's
`design-systems/` dir: Editorial, Industrial Brutalist, Glassmorphism, LMS
Bento, CRM Command Center, POS Double-Bezel.

### Examples

```scss
// default/tokens/_fu-default-theme.scss (HSL channels)
--fu-default-primary: 243 75% 59%;      // indigo
--fu-default-success: 152 69% 41%;
// engine remaps to semantic
--fu-token-primary: hsl(var(--fu-default-primary));
```

### Usage

Products reference `--fu-token-*` in their SCSS and `fu-*` classes in
templates. The variation spec `THEME-VARIATIONS.md` adds eight further
themes (Modern SaaS, Enterprise, Corporate, Educational, Retail, Minimal,
Dark, High Contrast).

### Customization

Change a palette by editing the theme's raw token file — every component
updates automatically. Add a new color role by extending
`engine/_fu-tokens.scss` and every theme's token file.

### Best Practices

- HSL everywhere; never mix units in one token.
- Contrast ≥ 4.5:1 body, ≥ 3:1 large text (High Contrast theme targets AAA).
- Keep semantic names stable; themes churn, tokens don't.

---

## 5. Django Fusion

### Purpose

`libs/django-fusion/` is the shared Django/Wagtail framework layer: routing,
fragments, `{% comp %}` components, forms, tables, and the
`TemplateRenderer` used by the dynamic template system.

### Architecture

```text
Request
  │
  ▼
project urls.py ──▶ middleware (auth, CSRF, locale, HTMX, site)
  │
  ▼
PageHandler / Viewset / Wagtail page / API endpoint
  │
  ├── services / models / query layer
  │
  ▼
TemplateRenderer (core/rendering.py)  ── renders ──▶ Django template
  │                                                   + {% comp %} tags
  │
  ├── full HTML (server-rendered)
  ├── HTMX fragment (fragment_name)          ──▶ client swap
  └── JSON (for Astro/SPA clients)
```

Canonical imports: `django_fusion.*` (e.g.
`from django_fusion.core.rendering import TemplateRenderer`). No re-export
shims.

### Examples

```django
{% comp "cards/course-card" course=course variant="featured" / %}
```

### Usage

- Components: `{% comp "name" / %}` for registered components; `{% include %}`
  only for genuinely dynamic names.
- Fragments: `fragment_name` context key for HTMX swap targets.
- Emails: `EmailTemplate` model (`django_fusion/models/email.py`) renders
  against a data context via `TemplateRenderer`.

### Customization

Register new components in the framework's `comp` package; products override
templates through the project's `TEMPLATES['DIRS']` cascade. Shared behavior
belongs in django-fusion; product behavior belongs in the product.

### Best Practices

- Business logic in services/managers, never in templates or views.
- Preserve Wagtail context, translation tags, permissions, HTMX attributes.
- Update `libs/django-fusion/docs/` when the public API changes.

---

## 6. Dynamic Templates

### Purpose

The dynamic template field system
(`docs/features/template-fields/`) lets editors author templates like
`{{ customer.name }}` or `{{ order.total }}` that render against live data —
sandboxed, validated, previewable, and safe by design.

### Architecture

```text
┌────────── 7-STAGE RENDERING PIPELINE  ──────────┐
│  1. Parse        regex tokenization of {{ path }} │
│  2. Resolve      dotted-path traversal            │
│  3. Validate     required / type / allowlist      │
│  4. Escape       HTML auto-escape                 │
│  5. Format       filter chain (date, upper, …)    │
│  6. Assemble     token replacement                │
│  7. Preview      sample data + watermark + issues │
└──────────────────────────────────────────────────┘
        │
        ▼
TemplateRenderer (django-fusion) ──▶ EmailTemplate / field_schema
```

Key models (see `02-models.md`): `FieldReference`, `ResolvedValue`,
`ValidationIssue`, `PreviewResult`, `TemplateSchema`, `SchemaField`,
`FieldType`, plus `field_schema` and `is_previewable` on `EmailTemplate`.

### Examples

```text
{{ customer.name }}        → "Ada Lovelace"
{{ order.total }}          → "249.00"
{{ invoice.number }}       → "INV-2026-0001"
{{ customer.email|default:"—" }}
```

### Usage

Templates are **parsed, not evaluated** — no Jinja/Django engine runs, which
eliminates SSTI. Resolution follows dotted paths against an allowlisted data
source; unresolved variables fall back to defaults or empty strings.

### Customization

Add filters to the filter registry (14 built-in), extend `FieldType` for new
data shapes, and configure allowlists and length limits in Django settings
(`TEMPLATE_FIELD_*`).

### Best Practices

- Never pass user-authored templates to `Template()` or `jinja2` — always
  the parser.
- Auto-escape HTML; sanitize URLs to safe schemes.
- Preview before send; log validation issues for audit.

---

## Cross-System Flow: One Request End to End

```text
Editor saves:  "Welcome {{ customer.name }}, invoice {{ invoice.number }}"
      │
      ▼
EmailTemplate (django-fusion) ──▶ TemplateRenderer
      │                               │
      │  1–7 stage pipeline            ▼
      │                          Django template
      │                          {% comp "email/layout" / %}
      ▼                               │
  Rendered HTML styled by       theme/<theme>/components/_fu-*.scss
  --fu-token-* tokens           compiled from tokens → engine
```

## Remarks & Notes

- `docs/content/` is generated; author only under `docs/design/`.
- The master SCSS entry (`theme/_index.scss`) currently imports all 13
  themes; products should import only their own theme + engine to keep
  bundle size down.
- `npx sass` is available in the repo for validation; run
  `make -C docs check` for Docus validation.
- <!-- AI-generated: review needed -->
