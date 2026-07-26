# CSS / Tailwind Docs — LMS Front-End

> **Directory:** `docs/css/`
> **Framework:** Tailwind CSS 3 + CTC Custom Theme
> **Project:** `projects/lms/front-end/`

---

## CTC Teal Theme Variables

```css
:root {
  --ctc-primary: 0 161 179;        /* #00a1b3 — Main teal */
  --ctc-primary-dark: 0 122 136;   /* #007a88 — Dark teal */
  --ctc-primary-light: 26 127 212; /* #1a7fd4 — Light blue accent */
  --ctc-secondary: 0 128 128;      /* #008080 — Teal */
  --ctc-accent: 108 99 255;        /* #6C63FF — Indigo accent */
  --ctc-accent-alt: 255 107 139;   /* #FF6B8B — Pink accent */
}
```

Usage: `text-[rgb(var(--ctc-primary))]`, `bg-[rgb(var(--ctc-primary))]/10`

## Component Classes

| Class | Purpose |
|-------|---------|
| `.btn-primary` | Primary action button (teal bg, white text) |
| `.btn-secondary` | Secondary button (white bg, gray border) |
| `.btn-outline` | Outline button (teal border) |
| `.btn-accent` | Accent button (indigo bg) |
| `.card` | White card with shadow |
| `.card-hover` | Card with hover lift effect |
| `.input-field` | Form input with focus ring |
| `.badge` / `.badge-primary` / `.badge-success` | Status badges |
| `.section-hero` | Teal gradient hero section |
| `.card-gradient` | Teal gradient card background |
| `.progress-track` / `.progress-fill` | Progress bar |

## Responsive Breakpoints

| Breakpoint | Width | Use |
|------------|-------|-----|
| default | < 640px | Mobile |
| `sm` | ≥ 640px | Mobile wide |
| `md` | ≥ 768px | Tablet |
| `lg` | ≥ 1024px | Desktop |
| `xl` | ≥ 1280px | Wide desktop |

## Forbidden Classes
- `indigo-*` — All pages migrated to CTC teal
- `purple-*` — All pages migrated to CTC teal

## Detailed Guides

| Guide | Description |
|-------|-------------|
| [Complete Theme Reference](./theme-complete-reference.md) | All CSS variables, 30+ component classes, responsive breakpoints, color usage guide |
