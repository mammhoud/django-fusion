# Structa Cloud — Theme Engine Architecture

> **Status:** Active · **Version:** 1.0 · **Location:** `projects/assets/theme/engine/`

This document describes the reusable theme engine that supports multiple
applications (CRM, POS, LMS, Landing Pages, and future products) with
theme inheritance, overrides, dark mode, multi-brand support, and runtime
theme switching.

---

## Table of Contents

1. [Architecture Diagram](#1-architecture-diagram)
2. [Theme Structure](#2-theme-structure)
3. [Inheritance Strategy](#3-inheritance-strategy)
4. [Override Strategy](#4-override-strategy)
5. [Configuration Examples](#5-configuration-examples)

---

## 1. Architecture Diagram

```text
                         ┌──────────────────────────────────────────────┐
                         │              HTML Document Root             │
                         │                                            │
                         │   <html                                     │
                         │     data-theme="lms"      ←─ active theme   │
                         │     data-brand="precis"    ←─ brand override │
                         │     class="dark"           ←─ dark mode      │
                         │   >                                        │
                         └─────────────┬────────────────────────────┘
                                       │
                   CSS Cascade (last wins)
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
         ▼                             ▼                             ▼
  ┌──────────────┐           ┌──────────────────┐          ┌──────────────┐
  │  Layer 1     │           │  Layer 2          │          │  Layer 3     │
  │  Base Tokens │           │  Theme Tokens     │          │  Brand       │
  │              │           │                  │          │  Overrides   │
  │ fu-default-* │           │ fu-<theme>-*     │          │              │
  │ (always on)  │           │ (per data-theme) │          │ [data-brand] │
  └──────┬───────┘           └────────┬─────────┘          └──────┬───────┘
         │                            │                           │
         └────────────────────────────┼───────────────────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────────┐
                         │  Layer 4: Semantic Aliases  │
                         │  --fu-token-*               │
                         │  (engine/_fu-tokens.scss)   │
                         │                            │
                         │  Remaps theme tokens →     │
                         │  semantic names components  │
                         │  actually consume.         │
                         └─────────────┬──────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────────┐
                         │  Layer 5: Dark Mode         │
                         │  .dark                      │
                         │  (overrides surface/ink     │
                         │   tokens per theme)         │
                         └─────────────┬──────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────────┐
                         │  Layer 6: Components        │
                         │                            │
                         │  engine/components/        │
                         │  (consume --fu-token-*)     │
                         │                            │
                         │  <theme>/components/        │
                         │  (consume --fu-<theme>-*)   │
                         └──────────────────────────────┘
```

### Request lifecycle

```text
Browser loads CSS
  → :root sets fu-default-* (base palette always present)
  → fu-lms-*, fu-crm-*, fu-pos-* tokens defined (available, not active)
  → :root sets --fu-token-* = fu-default-* (semantic base mapping)
  → [data-theme="lms"] remaps --fu-token-* → fu-lms-*
  → [data-brand="precis"] overrides --fu-token-primary
  → .dark overrides --fu-token-neutral-* and fu-*-paper/ink/card
  → Components render using --fu-token-* (resolved values)
```

---

## 2. Theme Structure

### Directory layout

```text
projects/assets/theme/
├── _index.scss                 # master: imports all themes + engine
├── engine/                     # theme engine (runtime layer)
│   ├── _index.scss             # engine entry point
│   ├── _fu-tokens.scss         # semantic alias definitions (--fu-token-*)
│   ├── _fu-engine.scss         # [data-theme], .dark, [data-brand] overrides
│   └── components/             # theme-agnostic BEM components
│       ├── _fu-form.scss       # forms (input, label, switch, check)
│       ├── _fu-alert.scss      # alerts & toasts
│       ├── _fu-nav.scss        # navigation & tabs
│       ├── _fu-table.scss      # data tables
│       └── _fu-attribution.scss # product-owned colophon (brand + copyright)
├── default/                    # base theme (fu-default-*)
│   ├── _index.scss
│   ├── tokens/
│   │   ├── _fu-default-theme.scss
│   │   ├── variables/           # archived _variables.scss, _mixins.scss
│   │   ├── base/                # reset, typography, spacing, animations
│   │   ├── elements/            # archived element SCSS (card, button…)
│   │   ├── header/              # archived header SCSS
│   │   ├── footer/              # archived footer SCSS
│   │   └── template/            # archived page-template SCSS
│   ├── components/              # BEM component partials
│   ├── templates/               # HTML reference templates
│   └── design-systems/          # editorial, brutalist, glassmorphism
├── lms/                         # LMS theme (fu-lms-*)
├── crm/                         # CRM theme (fu-crm-*)
├── pos/                         # POS theme (fu-pos-*)
├── DESIGN-SYSTEM.md             # design system specification
├── THEME-ENGINE.md              # this file
└── README.md                    # directory structure & import guide
```

### Token naming convention

| Layer | Pattern | Example |
|---|---|---|
| Raw (per-theme) | `--fu-<theme>-<property>` | `--fu-lms-primary` |
| Semantic alias | `--fu-token-<property>` | `--fu-token-primary` |
| Component class | `.fu-<theme>-<block>` | `.fu-lms-course-card` |
| Generic component | `.fu-<block>` | `.fu-form-input` |

### Three-layer token model

```text
Layer 1 (Raw):        --fu-lms-primary: 233 76% 56%;
                      ↓ (defined in lms/tokens/_fu-lms-theme.scss)

Layer 2 (Semantic):  --fu-token-primary: hsl(var(--fu-lms-primary));
                      ↓ (remapped in engine/_fu-engine.scss via [data-theme])

Layer 3 (Component):  .fu-btn { background: var(--fu-token-primary); }
                      ↓ (consumes only semantic aliases)
```

This separation means:
- **Switching themes** changes Layer 2 only — no component CSS changes.
- **Adding a new theme** requires only a new token file + a `[data-theme]`
  block in `_fu-engine.scss`. Zero component changes.
- **White-labeling** overrides Layer 2 brand colors via `[data-brand]`.

---

## 3. Inheritance Strategy

### CSS cascade order (last wins)

```text
1. :root                                    → fu-default-* base tokens
2. :root                                    → --fu-token-* = fu-default-*
3. .dark (on :root)                         → fu-default-* dark overrides
4. [data-theme="lms"]                       → fu-lms-* token definitions
5. [data-theme="lms"]                       → --fu-token-* remapped to fu-lms-*
6. [data-theme="lms"].dark                  → fu-lms-* dark overrides
7. [data-brand="precis"]                    → --fu-token-primary override
8. Local scope (inline style / class)       → --fu-token-* override (escape hatch)
```

### How inheritance works

1. **Base layer** (`default/tokens/_fu-default-theme.scss`):
   Defines `--fu-default-*` on `:root`. This is always loaded and always
   present. It is the fallback for every semantic alias.

2. **Theme layer** (e.g., `lms/tokens/_fu-lms-theme.scss`):
   Defines `--fu-lms-*` on `:root`. The custom properties exist in the
   cascade but are not consumed until the engine remaps the semantic
   aliases.

3. **Semantic layer** (`engine/_fu-tokens.scss`):
   Defines `--fu-token-*` on `:root`, initially mapping to
   `fu-default-*`. This is what components consume.

4. **Engine remap** (`engine/_fu-engine.scss`):
   When `[data-theme="lms"]` is set on `<html>`, a higher-specificity
   selector remaps `--fu-token-*` to `fu-lms-*`. Because attribute
   selectors `[data-theme]` have higher specificity than `:root` (which
   is equivalent to a type selector), the remap wins.

5. **Dark mode** (each theme's token file + engine):
   Each theme defines `.dark { --fu-<theme>-paper: …; … }`. The engine
   also remaps `--fu-token-neutral-*` under `.dark`. Because `.dark`
   is a class selector, it has higher specificity than `:root`, so dark
   overrides win.

6. **Brand overrides** (`engine/_fu-engine.scss`):
   `[data-brand="…"]` selectors override only the brand color tokens
   (`--fu-token-primary`, `--fu-token-secondary`, `--fu-token-accent`).
   These are placed after `[data-theme]` blocks so they win the cascade.

### Specificity chain

```text
:root                          → specificity 0-0-1 (element)
:root.dark                     → specificity 0-1-1 (class + element)
[data-theme="lms"]             → specificity 0-1-0 (attribute)
[data-theme="lms"].dark        → specificity 0-2-0 (attribute + class)
[data-brand="precis"]           → specificity 0-1-0 (attribute)
[data-theme="lms"][data-brand]  → specificity 0-2-0 (two attributes)
```

The cascade resolves correctly because:
- `[data-theme]` beats `:root` (attribute > element)
- `.dark` on `[data-theme]` beats `[data-theme]` alone
- `[data-brand]` is defined after `[data-theme]` in source order

---

## 4. Override Strategy

### Four override levels

| Level | Mechanism | Scope | Use case |
|---|---|---|---|
| 1. Theme | `[data-theme="…"]` | Entire app | Switch product theme (LMS→CRM) |
| 2. Brand | `[data-brand="…"]` | Entire app | White-label color customization |
| 3. Dark | `.dark` class | Entire app | Dark mode toggle |
| 4. Local | Inline `style` / scoped class | Single element/section | One-off customization |

### Theme override

Setting `data-theme` on `<html>` activates a theme. The engine remaps
all semantic tokens. No other markup changes needed.

```html
<!-- Default theme -->
<html data-theme="default">

<!-- LMS theme -->
<html data-theme="lms">

<!-- CRM theme -->
<html data-theme="crm">

<!-- POS theme -->
<html data-theme="pos">
```

### Brand override

Brand overrides recolor only the brand identity colors (primary,
secondary, accent). Spacing, radius, shadows, and motion remain from
the active theme.

```html
<!-- Structa brand (default) -->
<html data-theme="lms" data-brand="structa">

<!-- Precis brand -->
<html data-theme="lms" data-brand="precis">

<!-- Formint brand -->
<html data-theme="pos" data-brand="formint">

<!-- Loop CRM brand -->
<html data-theme="crm" data-brand="loop">
```

### Dark mode override

Dark mode is toggled by adding/removing `.dark` on `<html>`. Each theme
defines its own dark surface overrides. The engine remaps the neutral
ramp automatically.

```html
<!-- Light mode (default) -->
<html data-theme="lms">

<!-- Dark mode -->
<html data-theme="lms" class="dark">
```

### Local override (escape hatch)

Any component or section can override a token via inline style or a
scoped CSS rule. The cascade ensures these win because they are more
specific than attribute selectors.

```html
<!-- Inline override -->
<div style="--fu-token-primary: hsl(280 80% 50%)">
  <button class="fu-btn">Custom-colored button</button>
</div>
```

```scss
/* Scoped class override */
.my-section {
  --fu-token-primary: hsl(280 80% 50%);
  --fu-token-radius-md: 1rem;
}
```

### Design-token override (adding a new theme)

To add a new theme (e.g., "medical"):

1. Create `theme/medical/tokens/_fu-medical-theme.scss` with all
   `--fu-medical-*` tokens.
2. Add a `[data-theme="medical"]` block in `engine/_fu-engine.scss`
   remapping `--fu-token-*` to `fu-medical-*`.
3. Create component partials under `theme/medical/components/`.
4. Import the theme token file in the master `_index.scss`.

No changes to any existing component or the semantic alias layer are
needed.

---

## 5. Configuration Examples

### Example 1: Precis LMS (light mode)

```html
<!DOCTYPE html>
<html data-theme="lms" data-brand="precis" lang="en">
<head>
  <link rel="stylesheet" href="/static/css/theme.css">
</head>
<body>
  <header class="fu-nav fu-nav--sticky">
    <a class="fu-nav__brand" href="/">
      <img src="/logo.svg" alt="Precis">
    </a>
    <ul class="fu-nav__list">
      <li class="fu-nav__item active"><a href="/courses">Courses</a></li>
      <li class="fu-nav__item"><a href="/about">About</a></li>
    </ul>
  </header>
  <main>
    <div class="fu-lms-course-card">
      <div class="fu-lms-course-card__img">
        <img src="/course.jpg" alt="React Course">
      </div>
      <div class="fu-lms-course-card__body">
        <h3 class="fu-lms-course-card__title">React Front to Back</h3>
      </div>
    </div>
  </main>
</body>
</html>
```

### Example 2: Formint POS (dark mode)

```html
<!DOCTYPE html>
<html data-theme="pos" data-brand="formint" class="dark" lang="en">
<head>
  <link rel="stylesheet" href="/static/css/theme.css">
</head>
<body>
  <div class="fu-pos-register">
    <div class="fu-pos-register__cart">
      <div class="fu-pos-register__cart-item">
        <div class="info">
          <div class="name">Espresso</div>
          <div class="price">$3.50</div>
        </div>
        <div class="qty">
          <button>−</button>
          <span class="count">2</span>
          <button>+</button>
        </div>
        <div class="line-total">$7.00</div>
      </div>
    </div>
    <div class="fu-pos-register__totals">
      <div class="row grand">
        <span>Total</span>
        <span>$7.00</span>
      </div>
    </div>
    <div class="fu-pos-register__checkout">
      <button class="checkout-btn">Charge $7.00</button>
    </div>
  </div>
</body>
</html>
```

### Example 3: Loop CRM (command center)

```html
<!DOCTYPE html>
<html data-theme="crm" data-brand="loop" lang="en">
<head>
  <link rel="stylesheet" href="/static/css/theme.css">
</head>
<body>
  <div class="fu-crm-command">
    <div class="fu-crm-command__topbar">
      <input class="search" type="search" placeholder="Search contacts…">
    </div>
    <aside class="fu-crm-command__sidebar">
      <nav>
        <div class="fu-crm-command__nav-section">Pipeline</div>
        <a href="/leads" class="active">Leads</a>
        <a href="/deals">Deals</a>
      </nav>
    </aside>
    <main class="fu-crm-command__main">
      <div class="fu-crm-command__grid">
        <div class="fu-crm-command__stat">
          <div class="label">Total Revenue</div>
          <div class="value">$48.2k</div>
          <div class="delta delta--up">↑ 12.5%</div>
        </div>
      </div>
      <div class="fu-crm-pipeline">
        <div class="fu-crm-pipeline__column fu-crm-pipeline__column--lead">
          <div class="fu-crm-pipeline__column-header">
            <span class="fu-crm-pipeline__column-title">Lead</span>
            <span class="fu-crm-pipeline__column-count">8</span>
          </div>
          <div class="fu-crm-pipeline__column-body">
            <div class="fu-crm-pipeline__card">
              <div class="fu-crm-pipeline__card-title">Acme Corp</div>
              <div class="fu-crm-pipeline__card-meta">
                <span>John Doe</span>
                <span class="value">$12k</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</body>
</html>
```

### Example 4: Runtime theme switching (JavaScript)

```javascript
// Switch from LMS to CRM theme at runtime
document.documentElement.setAttribute('data-theme', 'crm');

// Toggle dark mode
document.documentElement.classList.toggle('dark');

// Switch brand (white-label)
document.documentElement.setAttribute('data-brand', 'loop');

// Smooth transition (opt-in)
document.documentElement.classList.add('fu-theme-transition');
// …switch theme…
// Remove after transition if desired:
// document.documentElement.classList.remove('fu-theme-transition');
```

### Example 5: Adding a custom brand at runtime

```javascript
// Define a custom brand inline (no pre-defined [data-brand] needed)
const root = document.documentElement;
root.style.setProperty('--fu-token-primary', 'hsl(280 80% 50%)');
root.style.setProperty('--fu-token-secondary', 'hsl(320 70% 55%)');
root.style.setProperty('--fu-token-accent', 'hsl(180 60% 50%)');
// Every component instantly restyles.
```

### Example 6: Product SCSS entry point

```scss
// projects/structa.cloud/assets/styles/_index.scss

// 1. Import the base theme (always needed)
@import 'theme/default';

// 2. Import the product theme
@import 'theme/lms';

// 3. Import the engine (semantic aliases + runtime switching)
@import 'theme/engine';

// 4. Import product-specific component overrides
@import 'pages/home';
@import 'pages/about';
```

### Example 7: Full master import (all themes)

```scss
// projects/assets/theme/_index.scss

@import 'default';   // base palette + all components + archived SCSS
@import 'lms';        // LMS tokens + components
@import 'crm';        // CRM tokens + components
@import 'pos';        // POS tokens + components
@import 'engine';     // semantic aliases + runtime switching + generic components
```

---

## Runtime switching summary

| Action | HTML change | CSS effect |
|---|---|---|
| Switch theme | `data-theme="crm"` | All `--fu-token-*` remap to `fu-crm-*` |
| Switch brand | `data-brand="loop"` | `--fu-token-primary/secondary/accent` override |
| Dark mode on | `class="dark"` | Surface/ink tokens invert per theme |
| Dark mode off | remove `dark` class | Surface/ink tokens revert to light |
| Smooth switch | `class="fu-theme-transition"` | Color properties animate over 200ms |
| Reduced motion | `prefers-reduced-motion: reduce` | All transitions → 0.01ms |

All switches are **instant** (CSS custom property re-resolution) unless
`.fu-theme-transition` is present, in which case color properties
animate smoothly. No JavaScript layout recalculation is needed — the
browser re-resolves `var()` references when custom properties change.
