# Theme Variations — Specifications

> **Status:** Active · **Version:** 1.0 · **Location:** `projects/assets/theme/`

This document specifies the 8 theme variations generated for the Structa
Cloud theme system. Each variation is a **token-only override** — it
shares the same design tokens, the same component behavior, and requires
minimal override logic (one `[data-theme]` block).

## How a variation works

```text
┌─────────────────────────────────────────────────────────────────┐
│  Shared layer (identical for every variation)                   │
│                                                                 │
│  • --fu-token-* semantic aliases (engine/_fu-tokens.scss)      │
│  • All BEM components (engine/components/, <theme>/components/) │
│  • Component behavior: states, sizes, variants                  │
├─────────────────────────────────────────────────────────────────┤
│  Variation layer (the ONLY thing that changes)                 │
│                                                                 │
│  • fu-<name>-* custom properties (tokens/<name>/_fu-*.scss)    │
│  • One [data-theme="<name>"] block calling fu-theme-remap()    │
├─────────────────────────────────────────────────────────────────┤
│  Result: same markup, same components, different look          │
└─────────────────────────────────────────────────────────────────┘
```

**Minimal override logic:** adding a variation is exactly two files —
a token partial and a one-line `[data-theme]` block. No component CSS
is ever touched.

---

## Variation matrix

| # | Theme | `data-theme` | Character | Best for |
|---|---|---|---|---|
| 1 | Modern SaaS | `saas` | Indigo-violet, soft gradients, generous radius | Dashboards, product UIs |
| 2 | Enterprise | `enterprise` | Deep blue, structured, conservative | Admin suites, B2B tools |
| 3 | Corporate | `corporate` | Navy-steel, serif display, flat | Company sites, annual reports |
| 4 | Educational | `educational` | Warm blue-green, rounded, friendly | Learning platforms, portals |
| 5 | Retail | `retail` | Coral-orange, bold, high-energy | E-commerce, storefronts |
| 6 | Minimal | `minimal` | Monochrome, hairline, editorial | Portfolios, documentation |
| 7 | Dark | `dark` | Electric violet, dark-first, glow | Dev tools, monitoring |
| 8 | High Contrast | `contrast` | Max luminance, thick borders, AAA | Accessibility compliance |

---

## 1. Modern SaaS (`data-theme="saas"`)

### Color palette

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `248 90% 60%` (indigo) | `248 90% 75%` | Brand, CTAs |
| Secondary | `199 89% 48%` (cyan) | — | Supporting accent |
| Accent | `48 96% 56%` (amber) | `48 96% 65%` | Highlights |
| Paper | `240 30% 99%` | `240 20% 8%` | Page background |
| Ink | `240 40% 12%` | `240 25% 95%` | Primary text |
| Card | `0 0% 100%` | `240 15% 11%` | Surfaces |

### Typography system

| Property | Value |
|---|---|
| Display | Inter 700, `-0.02em` tracking |
| Body | Inter 400, 1.625 line-height |
| Mono | JetBrains Mono (code, IDs) |
| Headings | Inter 800, tight leading |

### Signature details

- Radius: generous (0.375 → 1.25rem)
- Shadows: soft, layered elevation
- Gradients: `indigo → violet` primary gradient
- Motion: `cubic-bezier(0.4, 0, 0.2, 1)` premium easing

### Preview example

```html
<html data-theme="saas">
<body>
  <header class="fu-nav fu-nav--sticky">
    <a class="fu-nav__brand">Acme SaaS</a>
    <ul class="fu-nav__list">
      <li class="fu-nav__item active"><a>Dashboard</a></li>
      <li class="fu-nav__item"><a>Analytics</a></li>
    </ul>
    <div class="fu-nav__actions">
      <button class="fu-btn fu-btn--primary">Upgrade</button>
    </div>
  </header>
  <main>
    <div class="fu-card fu-card--padded">
      <h2 class="fu-card__title">Revenue overview</h2>
      <p class="fu-card__text">$48,200 this month — up 12.5%</p>
      <button class="fu-btn fu-btn--gradient">View report</button>
    </div>
  </main>
</body>
</html>
```

---

## 2. Enterprise (`data-theme="enterprise"`)

### Color palette

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `215 80% 40%` (deep blue) | `215 80% 68%` | Brand, CTAs |
| Secondary | `210 60% 45%` (steel) | — | Supporting |
| Accent | `45 90% 50%` (gold) | `45 90% 60%` | Status highlights |
| Paper | `215 20% 98%` | `215 25% 7%` | Page background |
| Ink | `215 35% 14%` | `215 20% 94%` | Primary text |
| Card | `0 0% 100%` | `215 16% 10%` | Surfaces |

### Typography system

| Property | Value |
|---|---|
| Display | Segoe UI / Inter 700 |
| Body | Segoe UI / Inter 400 |
| Mono | Cascadia Code (data, IDs) |
| Table | 0.5rem cell padding, 2.5rem rows |

### Signature details

- Radius: moderate (0.25 → 0.75rem)
- Shadows: firm, defined
- Data-dense table sizing tokens
- System-first, conservative type stack

### Preview example

```html
<html data-theme="enterprise">
<body>
  <div class="fu-table-wrapper">
    <table class="fu-table fu-table--striped">
      <thead>
        <tr><th>Dept</th><th>Owner</th><th class="fu-table__cell--numeric">Budget</th></tr>
      </thead>
      <tbody>
        <tr><td class="fu-table__cell--name">Engineering</td>
            <td>J. Doe</td>
            <td class="fu-table__cell--numeric">$1.2M</td></tr>
      </tbody>
    </table>
  </div>
  <button class="fu-btn fu-btn--primary">Approve</button>
</body>
</html>
```

---

## 3. Corporate (`data-theme="corporate"`)

### Color palette

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `220 70% 30%` (navy) | `220 70% 62%` | Brand, CTAs |
| Secondary | `215 40% 45%` (slate) | — | Supporting |
| Accent | `40 90% 48%` (gold) | `40 90% 60%` | Highlights |
| Paper | `220 15% 99%` | `220 20% 7%` | Page background |
| Ink | `220 35% 12%` | `220 18% 93%` | Primary text |
| Card | `0 0% 100%` | `220 14% 10%` | Surfaces |

### Typography system

| Property | Value |
|---|---|
| Display | **Source Serif Pro** 700 (serif!) |
| Body | Source Sans Pro 400 |
| Mono | JetBrains Mono |
| Headings | Serif, `-0.01em` tracking |

### Signature details

- Radius: small, classic (0.125 → 0.625rem)
- Shadows: subtle, flat
- Serif display headings for formal identity
- Conservative spacing

### Preview example

```html
<html data-theme="corporate">
<body>
  <article class="fu-card fu-card--padded">
    <h2 class="fu-card__title">Annual Report 2025</h2>
    <p class="fu-card__text">The Board is pleased to report a record year.</p>
    <button class="fu-btn fu-btn--outline">Download PDF</button>
  </article>
</body>
</html>
```

---

## 4. Educational (`data-theme="educational"`)

### Color palette

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `200 80% 42%` (friendly blue) | `200 85% 70%` | Brand, CTAs |
| Secondary | `35 90% 50%` (warm amber) | — | Supporting |
| Accent | `15 85% 58%` (coral) | — | Highlights |
| Paper | `60 20% 98%` (warm) | `210 25% 8%` | Page background |
| Ink | `210 30% 15%` | `210 20% 94%` | Primary text |
| Card | `0 0% 100%` | `210 16% 11%` | Surfaces |

### Typography system

| Property | Value |
|---|---|
| Display | Nunito 800 (rounded, friendly) |
| Body | Nunito / Inter 400 |
| Mono | JetBrains Mono |
| Headings | Rounded, wide leading |

### Signature details

- Radius: rounded, friendly (0.5 → 1.5rem)
- Shadows: soft, playful
- Bouncy motion `cubic-bezier(0.34, 1.56, 0.64, 1)`
- Pastel category surfaces
- Generous reading spacing

### Preview example

```html
<html data-theme="educational">
<body>
  <div class="fu-card fu-card--padded">
    <span class="fu-badge fu-badge--primary">New</span>
    <h2 class="fu-card__title">Introduction to Python</h2>
    <p class="fu-card__text">20 lessons · 40 students</p>
    <button class="fu-btn fu-btn--primary">Enroll now</button>
  </div>
</body>
</html>
```

---

## 5. Retail (`data-theme="retail"`)

### Color palette

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `10 85% 52%` (coral) | `10 90% 66%` | Brand, CTAs |
| Secondary | `25 90% 52%` (orange) | — | Supporting |
| Accent | `45 100% 50%` (yellow) | `45 100% 60%` | Promo, sale |
| Paper | `40 30% 98%` (warm) | `25 30% 8%` | Page background |
| Ink | `20 40% 14%` | `30 25% 94%` | Primary text |
| Card | `0 0% 100%` | `25 20% 11%` | Surfaces |

### Typography system

| Property | Value |
|---|---|
| Display | Poppins 700 (bold, punchy) |
| Body | Inter 400 |
| Mono | JetBrains Mono |
| Price | 1.25rem, extrabold |

### Signature details

- Radius: medium, tactile (0.375 → 1.125rem)
- Shadows: bold, coral-tinted hover
- Sale/new promo tones
- Bouncy, high-energy motion
- Product tile sizing tokens

### Preview example

```html
<html data-theme="retail">
<body>
  <div class="fu-card fu-card--padded">
    <span class="fu-badge fu-badge--error">Sale</span>
    <h2 class="fu-card__title">Premium Espresso</h2>
    <p class="fu-card__text">Single-origin, medium roast</p>
    <div class="fu-card__bottom">
      <span class="fu-retail-price">$14.00</span>
      <button class="fu-btn fu-btn--primary">Add to cart</button>
    </div>
  </div>
</body>
</html>
```

---

## 6. Minimal (`data-theme="minimal"`)

### Color palette

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `0 0% 9%` (near-black) | `0 0% 94%` | Brand, CTAs |
| Secondary | `0 0% 35%` (gray) | — | Supporting |
| Accent | `210 90% 38%` (restrained blue) | `210 90% 70%` | The only color |
| Paper | `0 0% 99%` | `0 0% 6%` | Page background |
| Ink | `0 0% 9%` | `0 0% 94%` | Primary text |
| Card | `0 0% 100%` | `0 0% 9%` | Surfaces |

### Typography system

| Property | Value |
|---|---|
| Display | Inter 700, `-0.03em` tracking |
| Body | Inter 400, 1.75 line-height |
| Mono | JetBrains Mono (labels) |
| Eyebrow | Mono, uppercase, `0.1em` tracking |

### Signature details

- Radius: near-zero (0 → 0.375rem)
- Shadows: none / hairline only
- Monochrome with a single accent
- Generous whitespace (6rem sections)
- Editorial, quiet motion

### Preview example

```html
<html data-theme="minimal">
<body>
  <section style="padding: 6rem">
    <span class="fu-tag">About</span>
    <h1 class="fu-section-title__title">Design is how it works.</h1>
    <p class="fu-section-title__subtitle">A quiet portfolio of thoughtful work.</p>
    <button class="fu-btn fu-btn--outline">View projects</button>
  </section>
</body>
</html>
```

---

## 7. Dark (`data-theme="dark"`)

### Color palette (dark-first)

| Token | Value | Role |
|---|---|---|
| Primary | `260 90% 64%` (electric violet) | Brand, CTAs |
| Secondary | `190 90% 55%` (cyan) | Supporting |
| Accent | `330 90% 62%` (pink) | Highlights |
| Paper | `240 20% 7%` (near-black) | Page background |
| Ink | `240 25% 95%` | Primary text |
| Card | `240 16% 10%` | Surfaces |
| Raised | `240 18% 13%` | Panels, tables |

### Typography system

| Property | Value |
|---|---|
| Display | Inter 700 |
| Body | Inter 400 |
| Mono | JetBrains Mono (telemetry-forward) |
| Labels | Mono, uppercase, `0.14em` tracking |

### Signature details

- **Dark is the default** — no `.dark` class needed
- Glow shadows tinted with the primary color
- Raised surface tokens for panel depth
- Mono-forward technical typography
- Snappy, technical motion

### Preview example

```html
<html data-theme="dark">
<body>
  <div class="fu-card fu-card--padded">
    <span class="fu-badge fu-badge--primary">LIVE</span>
    <h2 class="fu-card__title">System status</h2>
    <p class="fu-card__text">All systems operational · 99.99% uptime</p>
    <button class="fu-btn fu-btn--primary">Open console</button>
  </div>
</body>
</html>
```

---

## 8. High Contrast (`data-theme="contrast"`)

### Color palette (WCAG AAA)

| Token | Light | Dark | Role |
|---|---|---|---|
| Primary | `220 100% 35%` (strong blue) | `220 100% 70%` | Brand, CTAs |
| Secondary | `270 100% 40%` (purple) | — | Supporting |
| Accent | `50 100% 40%` (gold) | `50 100% 55%` | Highlights |
| Paper | `0 0% 100%` (pure white) | `0 0% 0%` (pure black) | Page background |
| Ink | `0 0% 0%` (pure black) | `0 0% 100%` | Primary text |
| Muted | `0 0% 20%` | `0 0% 85%` | Secondary text |

### Typography system

| Property | Value |
|---|---|
| Display | Arial 700 |
| Body | Arial 400, **1.0625rem base** (larger) |
| Mono | Courier New |
| Focus | 3px outline width |

### Signature details

- **Maximum luminance contrast** (pure black on pure white)
- Thick borders (`--fu-contrast-border-strong: 2px`)
- No reliance on color alone — always paired with icons/text
- Larger base text size
- Near-zero radius, functional
- Every combination meets WCAG AAA

### Preview example

```html
<html data-theme="contrast">
<body>
  <div class="fu-alert fu-alert--error fu-alert--solid" role="alert">
    <span class="fu-alert__icon">⚠</span>
    <div class="fu-alert__body">
      <strong class="fu-alert__title">Connection failed</strong>
      <p>Check your network and try again.</p>
    </div>
  </div>
  <button class="fu-btn fu-btn--primary">Retry</button>
</body>
</html>
```

---

## Shared design tokens

All variations consume the same semantic token layer. The table below
shows which token categories each variation overrides vs. inherits:

| Token category | Overridden per variation | Inherited from base |
|---|---|---|
| Colors | ✅ | — |
| Typography (families) | ✅ | — |
| Spacing scale | ✅ | — |
| Radius | ✅ | — |
| Shadows | ✅ | — |
| Transitions | ✅ | — |
| Z-index | ✅ (same values) | — |
| Grid / containers | — | ✅ base |
| Component structure | — | ✅ base |
| Component behavior | — | ✅ base |

## Consistent component behavior

Because every variation shares the same component partials, behavior is
identical across themes:

- **States:** `:hover`, `:focus-visible`, `:active`, `:disabled`
- **Sizes:** `--xs` → `--xl`, `--block`
- **Variants:** `--primary`, `--secondary`, `--outline`, `--ghost`, etc.
- **Accessibility:** focus rings, reduced-motion, contrast (all themes)

## Minimal override logic

Adding a new variation is exactly two steps:

```scss
/* 1. Token file — tokens/<name>/_fu-<name>-theme.scss */
:root { --fu-<name>-primary: 248 90% 60%; /* … */ }

/* 2. Activation block — engine/_fu-engine.scss */
[data-theme="<name>"] { @include fu-theme-remap(<name>); }
```

The `fu-theme-remap` mixin generates the complete `--fu-token-*`
remapping. No component CSS, no engine changes, no markup changes.

## Activation reference

| Variation | HTML |
|---|---|
| Modern SaaS | `<html data-theme="saas">` |
| Enterprise | `<html data-theme="enterprise">` |
| Corporate | `<html data-theme="corporate">` |
| Educational | `<html data-theme="educational">` |
| Retail | `<html data-theme="retail">` |
| Minimal | `<html data-theme="minimal">` |
| Dark | `<html data-theme="dark">` |
| High Contrast | `<html data-theme="contrast">` |

Combine with `data-brand` for white-label and `.dark` for dark mode
(except the dark-first theme, where dark is the default).
