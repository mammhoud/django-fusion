# Structa Cloud — Shared Theme Library

`projects/assets/theme/` is the shared, product-agnostic theme library for
every Structa Cloud frontend. It contains tokenized design systems, BEM SCSS
component partials, and HTML reference templates organised by product
domain (`default`, `lms`, `crm`, `pos`).

## Directory structure

```text
projects/assets/theme/
├── _index.scss               # master import (imports all four themes)
├── README.md                 # this file
├── engine/                   # theme engine — runtime layer (authored)
│   ├── _index.scss           # engine entry (tokens → engine → components)
│   ├── _fu-tokens.scss       # --fu-token-* semantic alias layer
│   ├── _fu-engine.scss       # [data-theme] / .dark / [data-brand] remaps
│   └── components/           # theme-agnostic BEM components
│       ├── _fu-form.scss         # forms
│       ├── _fu-alert.scss        # alerts & toasts
│       ├── _fu-nav.scss          # navigation & tabs
│       ├── _fu-table.scss        # data tables
│       └── _fu-attribution.scss  # product-owned colophon (brand + copyright)
├── default/                  # canonical base theme (fu-default-*)
│   ├── _index.scss
│   ├── tokens/               # fu-default-* custom properties
│   │   ├── _fu-default-theme.scss
│   │   ├── variables/        # archived _variables.scss + _mixins.scss
│   │   ├── base/             # reset, typography, spacing, animations…
│   │   ├── elements/         # archived element SCSS (card, button, badge…)
│   │   ├── header/           # archived header SCSS (mega-menu, nav…)
│   │   ├── footer/           # archived footer SCSS
│   │   └── template/         # archived page-template SCSS
│   ├── components/           # BEM SCSS partials (fu-card, fu-btn…)
│   │   ├── cards/            # Card, CourseCard, PricingCard, QuizCard…
│   │   ├── headers/          # Header, HeaderHomeTechnology, MegaMenu
│   │   ├── footers/          # Footer, FooterHomeTechnology, FooterMainDemo
│   │   ├── navigation/       # Breadcrumb
│   │   ├── content/          # content components
│   │   ├── interactive/      # Scripts, back-to-top
│   │   ├── _fu-card.scss
│   │   ├── _fu-btn.scss
│   │   ├── _fu-badge.scss
│   │   ├── _fu-breadcrumb.scss
│   │   ├── _fu-accordion.scss
│   │   ├── _fu-team.scss
│   │   ├── _fu-testimonial.scss
│   │   ├── _fu-counter.scss
│   │   ├── _fu-pricing.scss
│   │   ├── _fu-header.scss
│   │   ├── _fu-footer.scss
│   │   ├── _fu-megamenu.scss
│   │   ├── _fu-pagination.scss
│   │   ├── _fu-social.scss
│   │   ├── _fu-section-title.scss
│   │   ├── _fu-progressbar.scss
│   │   └── _fu-modal.scss
│   ├── templates/            # full HTML page templates (reference only)
│   │   ├── pages/            # main-demo, about, contact, pricing, 404…
│   │   ├── blog/             # blog grid, list, details, post formats
│   │   ├── shop/             # shop grid, single product
│   │   ├── course/           # course details, lessons, quizzes
│   │   ├── instructor/       # instructor dashboard, profile, courses
│   │   ├── student/          # student dashboard, profile, wishlist
│   │   ├── event/            # event grid, list, details
│   │   ├── elements/         # newsletter, counterup
│   │   └── fragments/        # project-copied partials (header, footer, hero, cta)
│   └── design-systems/       # higher-order design variations
│       ├── _fu-default-editorial.scss
│       ├── _fu-default-brutalist.scss
│       └── _fu-default-glassmorphism.scss
├── lms/                      # LMS / educational theme (fu-lms-*)
│   ├── _index.scss
│   ├── tokens/_fu-lms-theme.scss
│   ├── components/
│   │   ├── cards/             # course-card, instructor-card, quiz-card
│   │   ├── layout/            # header, sidebar
│   │   ├── content/
│   │   ├── navigation/
│   │   ├── course/
│   │   └── dashboard/
│   ├── templates/            # project-copied learning templates
│   │   ├── course/           # course_detail, lesson, catalog
│   │   ├── dashboard/        # dashboard, profile
│   │   └── fragments/        # course_list, lesson_progress, header, footer
│   └── design-systems/
│       └── _fu-lms-bento.scss
├── crm/                      # CRM / data-dense theme (fu-crm-*)
│   ├── _index.scss
│   ├── tokens/_fu-crm-theme.scss
│   ├── components/
│   │   ├── tables/           # data table with row/column BEM
│   │   ├── pipeline/         # kanban pipeline with stage colors
│   │   ├── cards/            # contact card
│   │   ├── navigation/
│   │   ├── layout/
│   │   └── dashboard/
│   ├── templates/             # project-copied CRM pages
│   │   ├── pages/            # contact, about, pricing, faq
│   │   └── fragments/        # list, pagination, form, stat-card
│   └── design-systems/
│       └── _fu-crm-command.scss
├── pos/                      # POS / register theme (fu-pos-*)
│   ├── _index.scss
│   ├── tokens/_fu-pos-theme.scss
│   ├── components/
│   │   ├── products/         # product card (touch-friendly)
│   │   ├── receipt/          # monospace receipt
│   │   ├── register/         # checkout panel (cart + totals + keypad)
│   │   ├── kpi/              # KPI stat tiles
│   │   ├── navigation/
│   │   └── dashboard/
│   ├── templates/            # project-copied POS templates
│   │   ├── dashboard/        # admin dashboard
│   │   ├── admin/            # products, users, settings, devices
│   │   └── fragments/        # tables, invoice
│   └── design-systems/
│       └── _fu-pos-double-bezel.scss
├── saas/                     # Modern SaaS variation (fu-saas-*)
│   └── tokens/_fu-saas-theme.scss
├── enterprise/               # Enterprise variation (fu-enterprise-*)
│   └── tokens/_fu-enterprise-theme.scss
├── corporate/                # Corporate variation (fu-corporate-*)
│   └── tokens/_fu-corporate-theme.scss
├── educational/              # Educational variation (fu-educational-*)
│   └── tokens/_fu-educational-theme.scss
├── retail/                   # Retail variation (fu-retail-*)
│   └── tokens/_fu-retail-theme.scss
├── minimal/                  # Minimal variation (fu-minimal-*)
│   └── tokens/_fu-minimal-theme.scss
├── dark/                     # Dark-first variation (fu-dark-*)
│   └── tokens/_fu-dark-theme.scss
├── contrast/                 # High-contrast variation (fu-contrast-*)
│   └── tokens/_fu-contrast-theme.scss
├── THEME-VARIATIONS.md       # variation specs (palettes, type, previews)
└── preview.html              # interactive theme switcher showcase
```

## Tokenisation convention

Every theme exposes its tokens with a `fu-<theme-name>-*` prefix:

| Theme | Token prefix | Example |
|---|---|---|
| Default | `fu-default-*` | `--fu-default-primary: 217 91% 43%;` |
| LMS | `fu-lms-*` | `--fu-lms-primary: 233 76% 56%;` |
| CRM | `fu-crm-*` | `--fu-crm-primary: 200 89% 44%;` |
| POS | `fu-pos-*` | `--fu-pos-primary: 165 50% 32%;` |

Tokens use **HSL channel notation** (`H S% L%`) so they can be assembled
with `hsl(var(--fu-*-primary))` or `hsl(var(--fu-*-primary) / 0.3)` for
opacity. This matches the existing fusion `--fu-*` convention.

## BEM naming convention

BEM blocks follow `fu-<theme-name>-<block>`:

```scss
.fu-lms-course-card { … }
.fu-lms-course-card__title { … }
.fu-lms-course-card--list { … }

.fu-crm-table { … }
.fu-crm-table__cell--status { … }
.fu-crm-table--striped { … }

.fu-pos-product-card { … }
.fu-pos-product-card__add { … }
.fu-pos-product-card--compact { … }
```

## Design system variations

Each theme can include one or more **design system** partials that override
tokens and add higher-order layout patterns:

| Theme | Design system | Character |
|---|---|---|
| default | Editorial | Wide serif typography, dropcaps, pullquotes |
| default | Industrial Brutalist | Zero radius, mechanical type, hazard red |
| default | Glassmorphism | Frosted blur surfaces, floating depth |
| lms | Bento Grid | Asymmetric 12-col dashboard grid |
| crm | Command Center | 3-pane telemetry shell |
| pos | Double-Bezel | Premium nested card (outer shell + inner core) |

## Theme variations

The library ships 8 token-only theme variations that share all components
and the semantic `--fu-token-*` layer. Each is activated with a single
`data-theme` attribute and requires no component changes:

| Variation | `data-theme` | Character |
|---|---|---|
| Modern SaaS | `saas` | Indigo-violet, soft gradients, generous radius |
| Enterprise | `enterprise` | Deep blue, structured, conservative |
| Corporate | `corporate` | Navy-steel, serif display, flat |
| Educational | `educational` | Warm blue-green, rounded, friendly |
| Retail | `retail` | Coral-orange, bold, high-energy |
| Minimal | `minimal` | Monochrome, hairline, editorial |
| Dark | `dark` | Electric violet, dark-first, glow |
| High Contrast | `contrast` | Max luminance, thick borders, WCAG AAA |

See [THEME-VARIATIONS.md](THEME-VARIATIONS.md) for full specs (color
palettes, typography systems, preview examples) and open
[preview.html](preview.html) in a browser to switch between all 8
variations live.

## Importing a theme

In a product's SCSS entry point:

```scss
/* Import only the themes this product needs */
@import 'theme/default';
@import 'theme/lms';

/* Or import everything */
@import 'theme';
```

The path assumes `projects/assets/` is in the SCSS `includePath` (which it is
for every Django-fusion and Astro product in the monorepo).

## Product attribution (`fu-attribution`)

The engine ships one colophon band that belongs to us: `fu-attribution`. It
renders the product mark, name, resource links, and the copyright line, and it
consumes `--fu-token-*` only — so it re-themes correctly with every variation:

```html
<footer class="fu-attribution">
  <div class="fu-attribution__inner">
    <a class="fu-attribution__brand" href="https://structa.cloud">
      <span class="fu-attribution__mark" aria-hidden="true">SC</span>
      <span>
        <span class="fu-attribution__name">Structa Cloud</span>
        <span class="fu-attribution__tagline">Tokens, components, and variations</span>
      </span>
    </a>
    <nav aria-label="Theme resources">
      <ul class="fu-attribution__links">
        <li><a class="fu-attribution__link" href="docs">Docs</a></li>
      </ul>
    </nav>
    <div class="fu-attribution__legal">
      <span class="fu-attribution__copyright">Copyright &copy; 2026 Structa Cloud</span>
      <span class="fu-attribution__licence">All strings authored in this repository</span>
    </div>
  </div>
</footer>
```

Variants: `--compact` for dense layouts and `--stacked` to stack the legal line
under the brand on narrow viewports (also the default below 640px).

**Why the block is `fu-attribution`, not `fu-footer`.** The vendored base
already defines a `.fu-footer` block in `default/components/_fu-footer.scss`, so
a second one would collide. This block is the authored replacement band for
authored pages, not an override of the archived one.

---

## Archived source

The `default/` theme's `tokens/` directory contains the original archived SCSS
from `.archives/theme/theme/` — `variables/`, `base/`, `elements/`, `header/`,
`footer/`, and `template/`. These are the raw source partials and are imported
by `default/_index.scss` alongside the newly-authored BEM component partials
in `components/`. This preserves the original design while layering clean BEM
components on top.

## CSS → SCSS

All stylesheets are `.scss` partials (prefixed with `_`). The archived
`style.scss` is at `default/tokens/_style.scss`. No plain `.css` files remain
in the theme library — everything compiles through the SCSS pipeline.

### Archived means excluded, not ours to rename

The `default/` theme's `tokens/`, `templates/`, and `components/` trees are a
vendored copy of a **commercial** education template (its own `tokens/_style.scss`
names the upstream item, and several templates still carry the upstream author's
copyright notice and purchase link). Two consequences, both permanent:

1. **They are excluded from every publish set.** Removing a copyright notice
does not clear a licence — the markup, SCSS, and imagery remain derivative. The
marketplace publish path (`docs/plans/structa-cloud/`) therefore builds only
from authored surfaces, and `tools/rebrand.mjs` refuses to rewrite anything on
the `theme-default-archive` surface.
2. **They are not the branding surface.** Structa Cloud attribution belongs in
the authored `fu-attribution` band above, not in an edit of an archived footer.

Authored surfaces — `engine/`, the token-only variations (`saas`, `corporate`,
…), and `design-systems/` — carry no third-party text and are the only ones a
rebrand may touch.
