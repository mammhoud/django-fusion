# LMS Front-End — Complete Theme Reference

> **Directory:** `docs/css/`
> **Theme:** Fusion CMS Teal
> **Framework:** Tailwind CSS 3

---

## CSS Variables (`:root`)

```css
:root {
  /* ── Primary (Teal) ── */
  --ctc-primary: 0 161 179;        /* #00a1b3 — Main brand teal */
  --ctc-primary-dark: 0 122 136;   /* #007a88 — Dark teal for hover/active */
  --ctc-primary-light: 26 127 212; /* #1a7fd4 — Blue accent */

  /* ── Secondary ── */
  --ctc-secondary: 0 128 128;      /* #008080 — Pure teal */

  /* ── Accents ── */
  --ctc-accent: 108 99 255;        /* #6C63FF — Indigo accent */
  --ctc-accent-alt: 255 107 139;   /* #FF6B8B — Pink accent */
}
```

Usage: `text-[rgb(var(--ctc-primary))]` or `bg-[rgb(var(--ctc-primary))]/10`

---

## Component Utility Classes

### Buttons

| Class | Style | Usage |
|-------|-------|-------|
| `.btn-primary` | Teal bg, white text, uppercase, 14px | Primary actions (Submit, Save, Sign In) |
| `.btn-secondary` | White bg, gray border, gray text | Secondary actions (Cancel, Back) |
| `.btn-outline` | Teal border, teal text, transparent bg | Ghost actions |
| `.btn-accent` | Indigo bg (`--ctc-accent`), white text | Accent actions |
| `.btn-white` | White bg, dark teal text | CTA on dark backgrounds |

### Cards

| Class | Style |
|-------|-------|
| `.card` | White bg, rounded-xl, shadow-sm, border gray-100 |
| `.card-hover` | `.card` + hover:-translate-y-1 + shadow-md |
| `.card-gradient` | Teal gradient (`--ctc-primary` to `--ctc-primary-dark`), white text |

### Forms

| Class | Style |
|-------|-------|
| `.input-field` | Full width, gray border, teal focus ring, 10px padding |

### Badges

| Class | Style |
|-------|-------|
| `.badge` | Inline-flex, px-2.5 py-0.5, rounded-full, text-xs, font-medium |
| `.badge-primary` | `.badge` + teal bg at 10% + teal text |
| `.badge-success` | `.badge` + green bg + green text |
| `.badge-warning` | `.badge` + yellow bg + yellow text |

### Sections

| Class | Style |
|-------|-------|
| `.section-hero` | Teal gradient (`--ctc-primary` → `--ctc-primary-dark` → `#005566`), white text, `overflow-hidden` |
| `.section-light` | Gray-50 bg |
| `.section-dark` | Gray-900 bg, white text |
| `.gradient-cta` | Gradient from `--ctc-primary` to `--ctc-accent` |

### Stats

| Class | Style |
|-------|-------|
| `.stat-card` | Card + hover lift + text-center |
| `.stat-value` | text-3xl, font-extrabold, teal, Urbanist font |
| `.stat-label` | text-sm, gray-500, uppercase, tracking-wider |

### Progress

| Class | Style |
|-------|-------|
| `.progress-track` | Full width, gray-200 bg, rounded-full, h-2 |
| `.progress-fill` | Teal bg, h-2, rounded-full, transition-all duration-500 |

### Icons

| Class | Style |
|-------|-------|
| `.feature-icon` | 12×12, rounded-xl, teal bg at 10%, teal icon |
| `.service-icon` | 16×16, rounded-2xl, teal bg at 10%, teal icon |
| `.contact-icon` | 10×10, rounded-lg, teal bg at 10%, teal icon |
| `.icon-stat` | 12×12, rounded-lg, flex center |

### Layout

| Class | Style |
|-------|-------|
| `.team-card` | Card + p-6 + text-center |
| `.team-avatar` | 20×20 rounded-full, teal→accent gradient, white initials |
| `.service-card` | Card + p-8 + text-center |
| `.contact-card` | Card + p-5 + flex + gap-4 |
| `.course-thumb` | card-gradient + h-40 + rounded-t-lg |
| `.faq-item` | border + rounded-xl + overflow-hidden |
| `.timeline-item` | relative + pl-8 + pb-8 + border-l-2 |
| `.timeline-dot` | absolute + 4×4 + rounded-full + teal + border-2 white |

---

## Responsive Breakpoints

| Breakpoint | Width | Use Case |
|------------|-------|----------|
| default | < 640px | Mobile — 1-col grids, hamburger menu |
| `sm` | ≥ 640px | Mobile wide — 2-col grids, inline nav |
| `md` | ≥ 768px | Tablet — sidebar + content, 2-3 col grids |
| `lg` | ≥ 1024px | Desktop — full sidebar, 3-4 col grids |
| `xl` | ≥ 1280px | Wide — max-w-7xl container, extra padding |

---

## Forbidden Classes (Theme Migration)

These classes MUST NOT appear in any LMS front-end page:

- `indigo-*` — Replaced with `--ctc-accent` or `--ctc-primary`
- `purple-*` — Replaced with `--ctc-accent` or `--ctc-primary`

Audit command:
```bash
rg 'indigo-|purple-' src/ --no-filename | wc -l
# Expected: 0
```

---

## Color Usage Guide

| Context | Variable | Tailwind |
|---------|----------|----------|
| Primary buttons, links, active states | `--ctc-primary` | `text-[rgb(var(--ctc-primary))]` |
| Button hover, pressed states | `--ctc-primary-dark` | `hover:bg-[rgb(var(--ctc-primary-dark))]` |
| Secondary accent (charts, badges) | `--ctc-accent` | `bg-[rgb(var(--ctc-accent))]` |
| Pink accent (highlights, alerts) | `--ctc-accent-alt` | `text-[rgb(var(--ctc-accent-alt))]` |
| Light teal backgrounds (cards, icons) | `--ctc-primary` at 10% | `bg-[rgb(var(--ctc-primary))]/10` |
| Gradient hero sections | `--ctc-primary` → `--ctc-primary-dark` | `.section-hero` |
| Gradient CTA | `--ctc-primary` → `--ctc-accent` | `.gradient-cta` |
