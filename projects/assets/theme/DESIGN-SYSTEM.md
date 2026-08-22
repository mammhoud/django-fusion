# Structa Cloud — Unified Design System Specification

> **Status:** Active · **Version:** 1.0 · **Location:** `projects/assets/theme/`

This document defines the unified design system shared across all Structa
Cloud products (CRM, POS, LMS, Landing Pages, and future products). It is
the single source of truth for design tokens, component standards, and
accessibility recommendations.

---

## Table of Contents

1. [Colors](#1-colors)
2. [Typography](#2-typography)
3. [Spacing](#3-spacing)
4. [Components](#4-components)
5. [Deliverables](#5-deliverables)
   - [Design Tokens](#design-tokens)
   - [Theme Variables](#theme-variables)
   - [Component Standards](#component-standards)
   - [Accessibility Recommendations](#accessibility-recommendations)
   - [Documentation](#documentation)

---

## 1. Colors

### Color categories

Every product exposes seven color categories. Each is tokenised as a
CSS custom property with the `--fu-<theme>-<category>` pattern, and
abstracted behind a semantic alias `--fu-token-<category>`.

| Category | Semantic alias | Purpose |
|---|---|---|
| Primary | `--fu-token-primary` | Brand identity, CTAs, active states |
| Secondary | `--fu-token-secondary` | Supporting accent, gradients |
| Accent | `--fu-token-accent` | Tertiary highlight, badges |
| Success | `--fu-token-success` | Positive states, confirmations |
| Warning | `--fu-token-warning` | Caution, pending states |
| Error | `--fu-token-error` | Destructive actions, validation errors |
| Neutral | `--fu-token-neutral-0..9` | Surfaces, text, borders |

### Color values per theme

All colors use **HSL channel notation** (`H S% L%`) so they can be
assembled with `hsl(var(--…))` and adjusted with opacity via
`hsl(var(--…) / 0.3)`.

| Token | Default | LMS | CRM | POS |
|---|---|---|---|---|
| Primary | `217 91% 43%` | `233 76% 56%` | `200 89% 44%` | `165 50% 32%` |
| Secondary | `265 75% 65%` | `265 75% 65%` | `175 70% 38%` | `35 80% 50%` |
| Accent | `48 100% 50%` | `48 96% 56%` | `48 96% 56%` | `48 96% 53%` |
| Success | `144 68% 37%` | `144 68% 37%` | `144 68% 37%` | `144 68% 37%` |
| Warning | `38 92% 50%` | `38 92% 50%` | `38 92% 50%` | `38 92% 50%` |
| Error | `0 72% 51%` | `0 72% 51%` | `0 72% 51%` | `0 72% 51%` |

### Neutral ramp

| Alias | Light | Dark | Role |
|---|---|---|---|
| `--fu-token-neutral-0` | Card (white) | Card (dark surface) | Highest surface |
| `--fu-token-neutral-1` | Paper (off-white) | Paper (near-black) | Page background |
| `--fu-token-neutral-3` | Line (light gray) | Line (dark gray) | Borders, dividers |
| `--fu-token-neutral-5` | Muted @ 50% | Muted @ 50% | Disabled, placeholders |
| `--fu-token-neutral-7` | Muted | Muted | Secondary text |
| `--fu-token-neutral-9` | Ink (near-black) | Ink (near-white) | Primary text |

### Dark mode

Dark mode is activated by adding the `.dark` class to `<html>`. Each
theme defines its own dark overrides for surface/ink tokens. The engine
remaps the neutral ramp automatically. See [Theme Engine](THEME-ENGINE.md).

---

## 2. Typography

### Font families

| Alias | Default | LMS | CRM | POS |
|---|---|---|---|---|
| `--fu-token-font-sans` | Inter | Inter | Inter | Outfit |
| `--fu-token-font-mono` | JetBrains Mono | JetBrains Mono | JetBrains Mono | JetBrains Mono |
| `--fu-token-font-display` | Inter | Inter | Inter | Outfit |

LMS additionally defines `--fu-lms-font-serif` (Source Serif Pro) for
editorial/body copy.

### Font sizes (modular scale — 1.250 Major Third)

| Alias | Size | Pixels | Usage |
|---|---|---|---|
| `--fu-token-text-xs` | 0.75rem | 12px | Captions, meta, badges |
| `--fu-token-text-sm` | 0.875rem | 14px | Body text (compact) |
| `--fu-token-text-base` | 1rem | 16px | Body text (default) |
| `--fu-token-text-lg` | 1.125rem | 18px | Lead paragraphs |
| `--fu-token-text-xl` | 1.25rem | 20px | Subheadings |
| `--fu-token-text-2xl` | 1.5rem | 24px | Section headings |
| `--fu-token-text-3xl` | 1.875rem | 30px | Page headings |
| `--fu-token-text-4xl` | 2.25rem | 36px | Hero headings |
| `--fu-token-text-5xl` | 3rem | 48px | Display headings |
| `--fu-token-text-6xl` | 3.75rem | 60px | Mega display |

### Font weights

| Alias | Value | Usage |
|---|---|---|
| `--fu-token-weight-light` | 300 | Large display text |
| `--fu-token-weight-regular` | 400 | Body text |
| `--fu-token-weight-medium` | 500 | Buttons, labels |
| `--fu-token-weight-semibold` | 600 | Subheadings, active nav |
| `--fu-token-weight-bold` | 700 | Headings, titles |
| `--fu-token-weight-extrabold` | 800 | Stat values, prices |
| `--fu-token-weight-black` | 900 | Brutalist display |

### Line heights

| Alias | Value | Usage |
|---|---|---|
| `--fu-token-leading-none` | 1 | Stat values, KPIs |
| `--fu-token-leading-tight` | 1.25 | Headings |
| `--fu-token-leading-snug` | 1.375 | Subheadings |
| `--fu-token-leading-normal` | 1.5 | UI text, form labels |
| `--fu-token-leading-relaxed` | 1.625 | Body copy |
| `--fu-token-leading-loose` | 2 | Wide editorial |

### Letter spacing

| Alias | Value | Usage |
|---|---|---|
| `--fu-token-tracking-tighter` | -0.05em | Large display |
| `--fu-token-tracking-tight` | -0.025em | Headings |
| `--fu-token-tracking-normal` | 0 | Body text |
| `--fu-token-tracking-wide` | 0.025em | Buttons |
| `--fu-token-tracking-wider` | 0.05em | Labels |
| `--fu-token-tracking-widest` | 0.1em | Uppercase eyebrows |

---

## 3. Spacing

### Margin / padding scale

The spacing scale is shared across all themes, but each theme can
override individual steps (e.g., LMS uses wider spacing for reading
comfort, CRM uses tighter spacing for data density).

| Alias | Default | LMS | CRM | POS |
|---|---|---|---|---|
| `--fu-token-space-0` | 0 | 0 | 0 | 0 |
| `--fu-token-space-px` | 1px | 1px | 1px | 1px |
| `--fu-token-space-xs` | 0.25rem | 0.375rem | 0.25rem | 0.25rem |
| `--fu-token-space-sm` | 0.5rem | 0.625rem | 0.5rem | 0.5rem |
| `--fu-token-space-md` | 1rem | 1.25rem | 0.875rem | 0.75rem |
| `--fu-token-space-lg` | 1.5rem | 1.75rem | 1.25rem | 1rem |
| `--fu-token-space-xl` | 2rem | 2.5rem | 1.75rem | 1.5rem |
| `--fu-token-space-2xl` | 3rem | 3.5rem | 2.5rem | 2rem |
| `--fu-token-space-3xl` | 4rem | 5rem | 3.5rem | 3rem |

### Section padding

| Alias | Default | LMS | CRM | POS |
|---|---|---|---|---|
| `--fu-token-section-lg` | 5rem | 6rem | 4rem | 3.5rem |
| `--fu-token-section-xl` | 6rem | 8rem | 5rem | 5rem |

### Grid system

| Token | Value | Description |
|---|---|---|
| `--fu-token-grid-columns` | 12 | Column count |
| `--fu-token-grid-gutter` | `--fu-token-space-md` | Default gutter |
| `--fu-token-grid-gutter-sm` | `--fu-token-space-sm` | Tight gutter |
| `--fu-token-grid-gutter-lg` | `--fu-token-space-lg` | Wide gutter |
| `--fu-token-grid-max-width` | 80rem | Max content width |

### Container widths

| Alias | Width | Breakpoint |
|---|---|---|
| `--fu-token-container-sm` | 40rem (640px) | `sm` |
| `--fu-token-container-md` | 48rem (768px) | `md` |
| `--fu-token-container-lg` | 64rem (1024px) | `lg` |
| `--fu-token-container-xl` | 80rem (1280px) | `xl` |
| `--fu-token-container-2xl` | 96rem (1536px) | `2xl` |

### Breakpoints

| Alias | Width |
|---|---|
| `--fu-token-bp-sm` | 640px |
| `--fu-token-bp-md` | 768px |
| `--fu-token-bp-lg` | 1024px |
| `--fu-token-bp-xl` | 1280px |
| `--fu-token-bp-2xl` | 1536px |

---

## 4. Components

All components follow **BEM** (Block Element Modifier) naming. Theme-
specific components use the `fu-<theme>-<block>` prefix. Theme-agnostic
components (in `engine/components/`) use `fu-<block>` and consume
`--fu-token-*` semantic aliases.

### Buttons

**Files:** `default/components/_fu-btn.scss`, per-theme variants

| Variant | Class | Description |
|---|---|---|
| Primary | `.fu-btn` | Solid primary background |
| Secondary | `.fu-btn--secondary` | Secondary color |
| Outline | `.fu-btn--outline` | Bordered, transparent bg |
| Ghost | `.fu-btn--ghost` | No bg, hover tint |
| Gradient | `.fu-btn--gradient` | Animated gradient |
| Link | `.fu-btn--link` | Inline text link with underline |
| Round/Icon | `.fu-btn--round` | Circular icon button |

**Sizes:** `--xs`, `--sm`, `--md`, `--lg`, `--xl`, `--block`

**States:** default, `:hover`, `:focus-visible`, `:active`, `:disabled`

### Forms

**File:** `engine/components/_fu-form.scss`

| Element | Class | Description |
|---|---|---|
| Text input | `.fu-form-input` | Standard text input |
| Textarea | `.fu-form-textarea` | Multi-line input |
| Select | `.fu-form-select` | Dropdown select |
| Label | `.fu-form-label` | Field label with required marker |
| Help text | `.fu-form-help` | Field description |
| Error text | `.fu-form-error-text` | Validation error |
| Checkbox/Radio | `.fu-form-check` | Inline check control |
| Switch | `.fu-form-switch` | Toggle switch |
| Field group | `.fu-form-group` | Label + input + help wrapper |
| Field row | `.fu-form-row` | Inline field layout |

**Validation states:** `.is-invalid` (red border + error shadow),
`.is-valid` (green border)

### Cards

**Files:** `default/components/_fu-card.scss`, per-theme variants

| Variant | Class | Description |
|---|---|---|
| Default | `.fu-card` | Standard surface with shadow |
| Minimal | `.fu-card--minimal` | Larger padding, elevated shadow |
| List | `.fu-card--list` | Horizontal image-left layout |
| Interactive | `.fu-card--interactive` | Hover lift + cursor |
| Gradient | `.fu-card--gradient` | Dark inverted surface |
| Padded | `.fu-card--padded` | Reduced padding |
| Compact | `.fu-card--compact` | Dense layout |

### Tables

**Files:** `engine/components/_fu-table.scss`, `crm/components/tables/_fu-crm-table.scss`

| Feature | Class | Description |
|---|---|---|
| Responsive wrapper | `.fu-table-wrapper` | Horizontal scroll on overflow |
| Base table | `.fu-table` | Semantic HTML table |
| Striped | `.fu-table--striped` | Alternating row backgrounds |
| Bordered | `.fu-table--bordered` | Cell borders |
| Compact | `.fu-table--compact` | Reduced padding |
| Hover rows | `.fu-table--hover` | Row highlight on hover |
| Numeric cell | `.fu-table__cell--numeric` | Right-aligned, tabular nums |
| Mono cell | `.fu-table__cell--mono` | Monospace font |
| Truncate cell | `.fu-table__cell--truncate` | Ellipsis overflow |
| Actions cell | `.fu-table__cell--actions` | Inline action buttons |

### Navigation

**File:** `engine/components/_fu-nav.scss`

| Element | Class | Description |
|---|---|---|
| Nav bar | `.fu-nav` | Horizontal navigation bar |
| Brand/logo | `.fu-nav__brand` | Logo + name |
| Nav list | `.fu-nav__list` | Horizontal link list |
| Nav item | `.fu-nav__item` | Individual link |
| Actions | `.fu-nav__actions` | Right-aligned actions |
| Mobile toggle | `.fu-nav__toggle` | Hamburger (≤768px) |
| Sticky | `.fu-nav--sticky` | Sticky positioning |
| Transparent | `.fu-nav--transparent` | Over-hero transparent |
| Tabs | `.fu-nav-tabs` | Tab navigation |
| Tab item | `.fu-nav-tabs__item` | Individual tab |
| Pills variant | `.fu-nav-tabs--pills` | Pill-style tabs |

### Modals

**File:** `default/components/_fu-modal.scss`

| Element | Class | Description |
|---|---|---|
| Container | `.fu-modal` | Fixed overlay (`.open` to show) |
| Backdrop | `.fu-modal__backdrop` | Semi-transparent blur layer |
| Dialog | `.fu-modal__dialog` | Centered card |
| Header | `.fu-modal__header` | Title + close button |
| Close | `.fu-modal__close` | Close button |
| Body | `.fu-modal__body` | Content area |
| Footer | `.fu-modal__footer` | Action buttons |

**Sizes:** `--sm` (24rem), default (32rem), `--lg` (48rem), `--xl`
(64rem), `--fullscreen` (100%)

### Alerts

**File:** `engine/components/_fu-alert.scss`

| Variant | Class | Description |
|---|---|---|
| Info | `.fu-alert--info` | Blue informational |
| Success | `.fu-alert--success` | Green confirmation |
| Warning | `.fu-alert--warning` | Amber caution |
| Error | `.fu-alert--error` | Red error |
| Solid | `.fu-alert--solid` | Strong filled background |
| Toast | `.fu-alert--toast` | Fixed bottom-right notification |

**Elements:** `__icon`, `__title`, `__body`, `__close`

---

## 5. Deliverables

### Design Tokens

All design tokens are CSS custom properties defined in SCSS partials:

```text
projects/assets/theme/
├── default/tokens/_fu-default-theme.scss   # base palette
├── lms/tokens/_fu-lms-theme.scss           # LMS palette
├── crm/tokens/_fu-crm-theme.scss           # CRM palette
├── pos/tokens/_fu-pos-theme.scss           # POS palette
└── engine/_fu-tokens.scss                  # semantic aliases
```

Tokens follow three layers:
1. **Raw** — `--fu-<theme>-<property>` (e.g., `--fu-lms-primary`)
2. **Semantic** — `--fu-token-<property>` (e.g., `--fu-token-primary`)
3. **Component** — components reference `--fu-token-*` only

### Theme Variables

Each theme defines a complete set of variables covering: colors,
typography, spacing, radius, shadows, transitions, z-index, and
theme-specific extras (e.g., CRM pipeline stage colors, POS touch
target sizing). See [Theme Engine Architecture](THEME-ENGINE.md) for
the full inheritance and override strategy.

### Component Standards

Every component is documented with:
- **BEM class name** and file location
- **Element** and **modifier** tables
- **State** variants (`:hover`, `:focus-visible`, `:disabled`)
- **Size** variants where applicable

Component SCSS files are at:
- `engine/components/` — theme-agnostic (consume `--fu-token-*`)
- `<theme>/components/` — theme-specific (consume `--fu-<theme>-*`)

### Accessibility Recommendations

#### Color contrast

| Combination | Light mode | Dark mode | Standard |
|---|---|---|---|
| Ink on Paper | 15:1 | 13:1 | AAA |
| Muted on Paper | 4.6:1 | 4.8:1 | AA |
| Primary on Card | 4.5:1 | 4.6:1 | AA |
| Error on Card | 4.5:1 | 4.5:1 | AA |
| Card on Line | — | — | Decorative only |

- **Minimum contrast:** 4.5:1 for body text (WCAG AA).
- **Large text** (≥18px or ≥14px bold): 3:1 minimum.
- **Interactive elements:** 3:1 against adjacent background.
- Never rely on color alone — always include an icon or text label
  for semantic states (success/warning/error).

#### Focus management

- All interactive elements use `:focus-visible` with a 2px outline
  in `--fu-token-primary` at 2px offset.
- Modals trap focus within the dialog when open.
- Focus returns to the triggering element when a modal closes.
- Tab order follows visual order (DOM source order).

#### Touch targets

- POS theme enforces `--fu-pos-touch-min: 2.75rem` (44px) minimum
  for all interactive elements, meeting WCAG 2.5.5 (Level AAA).
- Other themes use 2.5rem (40px) as the practical minimum.

#### Motion

- `prefers-reduced-motion: reduce` is respected globally — all
  transitions and animations are reduced to 0.01ms.
- Theme switching transitions are opt-in via `.fu-theme-transition`
  on `<html>` to avoid affecting initial paint.

#### Screen readers

- Form inputs use `<label>` with `for` attribute (or wrapping `<label>`).
- Validation errors use `aria-describedby` pointing to the error text.
- Modals use `role="dialog"` and `aria-modal="true"`.
- Alert/toast elements use `role="alert"` or `role="status"`.
- Icon-only buttons have `aria-label`.

### Documentation

- **[DESIGN-SYSTEM.md](DESIGN-SYSTEM.md)** — this file (design spec)
- **[THEME-ENGINE.md](THEME-ENGINE.md)** — architecture and runtime
- **[README.md](README.md)** — directory structure and import guide
- **Inline SCSS headers** — every partial has a header block
  explaining its purpose, source, and token dependencies
