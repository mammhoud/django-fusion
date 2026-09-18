# Loop-CRM — Frontend Design Tokens

Single source of truth for the Loop-CRM visual language. Every page (landing,
auth, app shell, data screens) must derive from these tokens. Tokens are
declared in `src/styles/globals.css` (`--loop-*`) and mirrored inline where a
standalone page (Django render-first) needs them.

## Palette

Dark substrate only. No pure black, no pure white, one accent.

| Token | Value | Role |
|---|---|---|
| `--loop-bg-deep` | `#0b1114` | Page substrate (radial emerald wash at top-right) |
| `--loop-bg` | `#0f1a1d` | App-shell surface behind panels |
| `--loop-panel` | `#111b1e` | Card/panel surface |
| `--loop-panel-raised` | `#172c2b` | Hover/elevated surface |
| `--loop-ink` | `#edf2f7` | Primary text |
| `--loop-muted` | `#8d9aaa` | Secondary text (AA on substrate) |
| `--loop-dim` | `#4f6464` | Tertiary/mono labels |
| `--loop-line` | `#263241` | Hairline borders |
| `--loop-line-soft` | `rgba(38,50,65,.55)` | Softer hairlines |
| `--loop-accent` | `#73d1bb` | Accent (emerald) — the ONLY accent |
| `--loop-accent-bright` | `#a7e8d8` | Accent highlights, active nav, revenue numbers |

Rules: exactly one accent; never add purple/blue glows; tints of the emerald
accent (`rgba(139,203,181,…)`) are allowed for washes; gradients are
radial washes or 145deg surface gradients only.

## Typography

- **Display/body:** `Bricolage Grotesque` (variable, self-hosted via
  `@fontsource-variable`). Headlines: weight 700, `letter-spacing:-.06em`,
  `line-height:1.02-1.04`, `text-wrap:balance`. Body: 400, `--loop-muted`,
  `text-wrap:pretty`, max measure ~42rem.
- **Data/labels/mono:** `JetBrains Mono` for eyebrows, breadcrumbs, nav
  labels, numbers, metadata strips — 600 weight, `letter-spacing:.08-.16em`,
  `text-transform:uppercase` for labels.
- **Never** use a serif. **Never** use Inter as the display face.

## Radii & elevation

- Cards/containers: squircle `1rem .4rem 1rem .4rem` (or `.72rem .28rem` on
  compact surfaces) — this asymmetrical radius is the signature.
- Controls/buttons/inputs: `.45rem` (small `.28rem`).
- Pills/badges/status dots: full (`999px`).
- Shadows: diffused, tinted to the background hue
  (`0 1.5rem 3rem rgba(3,17,19,.5)`); no hard dark drop shadows, no outer
  glows. Insets: `inset 0 1px 0 rgba(182,227,209,.06)` on raised surfaces.

## Interaction

- Hover: `transform:translateY(-1/-2px)` + border-color to
  `#477c6c`/`#4d8575`; active: `translateY(1px) scale(.98)`; focus-visible:
  2px `--loop-accent-2` outline offset 3px.
- Motion: `cubic-bezier(.16,1,.3,1)` entry reveals (rise 12px + fade),
  `prefers-reduced-motion` collapses everything to static.
- Background grid: 5rem blueprint grid at 4-16% opacity, masked to the top
  80% — decorative only, `pointer-events:none`.

## Borrowed-pattern map (DNA)

| Surface | Pattern | DNA |
|---|---|---|
| Side nav, breadcrumbs, record chrome | Twenty record-app shell | Twenty |
| Deals kanban board | Twenty board UI | Twenty |
| Content calendar + approvals | Postiz calendar + review queues | Postiz |
| Landing `.loop-dna` heritage strip | both | Twenty + Postiz |
| Attribution + finance ledger | net-new, no parent | Loop-CRM |
