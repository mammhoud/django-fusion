# Formint — Design System & Theme Reference

> **Version:** 2.0.0
> **Last Updated:** 22 August 2026
> **Applies to:** formint-pro, formint-community, formint-standard, formint-cloud, formint-client
> **Canonical source:** `projects/formints/formint-pro/frontend/src/styles/` (`tokens.css` + `global.css`)

---

## 1. Design Language

All five editions share one **Formint design language**:

| Element | Value |
|---|---|
| **Palette** | Warm cream paper · warm ink · verdigris primary · amber accent |
| **Primary (verdigris)** | `oklch(47% 0.08 165)` (light) · `oklch(78% 0.09 165)` (dark) |
| **Accent (amber)** | `oklch(83% 0.12 90)` |
| **Paper** | `oklch(98.4% 0.006 90)` (light) · `oklch(18% 0.012 70)` (dark) |
| **Ink** | `oklch(25% 0.015 60)` (light) · `oklch(90% 0.01 90)` (dark) |
| **Type** | Outfit (brand) · JetBrains Mono (mono) · Noto Naskh Arabic (RTL) |
| **Motion** | Spring physics `cubic-bezier(0.32, 0.72, 0, 1)`, 150/200/300ms transitions |
| **Shape** | `--radius-box: 0.75rem` · `--radius-field: 0.5rem` · `--radius-selector: 9999px` |

The single source of truth is **formint-pro** (`Astro + Alpine.js + HTMX + Tailwind CSS v4`),
which defines the tokens and BEM components that the other editions mirror.

---

## 2. Edition Implementation Map

| Edition | Stack | Design implementation |
|---|---|---|
| **formint-pro** | Astro 5 + Alpine.js + HTMX + Tailwind v4 | **Canonical** — `src/styles/tokens.css` (semantic tokens) + `src/styles/global.css` (BEM components + animations) |
| **formint-community** | Astro 5 + React 19 + FlyonUI 2.4 + shadcn | FlyonUI `perplexity` theme re-themed to the Formint palette + `assets/styles/base/_variables.css` semantic tokens + BEM library |
| **formint-standard** | Same as community | Identical to community (FlyonUI `perplexity` + shadcn `base-nova`) |
| **formint-cloud** | Same as community (Django backend) | Identical to community |
| **formint-client** | Vue 3 + Vite + daisyUI 5 + shadcn-vue + Astro shell | `fu-*` tokens (paper/ink/verdigris/amber) + semantic alias layer + BEM components (`src/styles/globals.css`) |

---

## 3. Semantic Token Vocabulary

The shared token vocabulary (defined literally in formint-pro, aliased in the other editions):

### Surface & text

| Token | Role |
|---|---|
| `--color-surface-page / card / raised / hover` | Background surfaces |
| `--color-text-primary / secondary / disabled / inverse` | Text colors |

### Brand & semantic

| Token | Role |
|---|---|
| `--color-primary / -content / -hover / -light / -strong` | Verdigris brand/action |
| `--color-accent / -content / -strong` | Amber highlight |
| `--color-secondary / -content` | Complementary |
| `--color-success / warning / error / info / neutral` (+ `-content`, `-strong`) | Semantic states |

### Structure & motion

| Token | Role |
|---|---|
| `--color-border-subtle / default / emphasis` | Hairline borders |
| `--radius-box / field / selector` | Radius scale (12px / 8px / pill) |
| `--shadow-sm / md / lg / colored` | Diffused, tinted depth |
| `--transition-fast / normal / slow` | 150 / 200 / 300ms |
| `--space-pos-xs … xl` | POS density spacing scale |
| `--color-chart-1 … 7` | Categorical data-viz palette |
| `--font-sans / mono / arabic` | Outfit / JetBrains Mono / Noto Naskh Arabic |

> Rule of thumb: reference these tokens — never hard-code hex — so components
> keep working across light/dark, RTL, and every edition.

---

## 4. BEM Component Library

Defined in formint-pro `global.css` (`@layer components`), mirrored in the other editions:

| Class | Purpose |
|---|---|
| `.badge` (+ `-primary/success/warning/error/info/neutral`, `-soft-*`, `-xs/sm/lg`) | Status pills |
| `.btn` (+ `-primary/secondary/ghost/outline/success/error/warning`, sizes, `-block`) | Buttons |
| `.card` / `.card-body` | Surface container |
| `.input` / `.select` | Form fields (token-driven, dark-safe) |
| `.switch` / `.switch--on` / `.switch__knob` | Toggle |
| `.tag` (+ `--primary/warning/info/success/error/neutral`, `--sm`) | Filter pills |
| `.toast` (+ `-success/-error`) | Status toast |
| `.stat-card` (+ `__title/__value/__desc`) | Metric card |
| `.data-table` | Dense responsive table |
| `.kds-ticket` (+ `--overdue`) | Kitchen display ticket |
| `.skeleton-shimmer` | Loading placeholder |

---

## 5. Animations

| Animation | Token/easing |
|---|---|
| Spring transitions | `cubic-bezier(0.32, 0.72, 0, 1)` |
| `toast-in` | 250ms slide-fade |
| `shimmer` | 1.4–1.8s skeleton sweep |
| Button press | `transform: scale(0.97)` on `:active` |
| Reduced motion | All motion collapsed under `prefers-reduced-motion: reduce` |

---

## 6. Assets

| Asset | Path (canonical) | Shared by |
|---|---|---|
| `Outfit-400/500/600/700.woff2` | `formint-pro/frontend/src/assets/fonts/outfit/` | All editions (byte-identical copies) |

---

## 7. How to Change the Design

1. Edit `formint-pro/frontend/src/styles/tokens.css` (tokens) or `global.css` (components/animations).
2. Propagate the change to each edition's equivalent layer:
   - React editions → `assets/styles/base/_variables.css` + component library.
   - client → `frontend/src/styles/globals.css` semantic alias + BEM block.
3. Re-copy any changed font assets.
4. Update this document and the edition `color-palette.md` / `styling.md` / `shared-components.md`.
