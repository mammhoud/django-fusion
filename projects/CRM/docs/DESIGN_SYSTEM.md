# Loop-CRM — Tactical Telemetry Design System

> **Archetype:** Industrial Brutalism — *Tactical Telemetry & CRT Terminal*
> **Applies to:** `frontend/` (Astro shell) + `backend/templates/base.html` (Django shell)
> **Status:** Active

Loop-CRM is a revenue-operations workspace: CRM, publishing, attribution,
finance, and automation. The interface is engineered like the instrument
panel of a revenue operations console — **dark-only, monospace-led, hard
right angles, hazard-red alerts, and simulated CRT phosphor**. No gradients,
no soft shadows, no rounded corners, no translucency-as-decoration.

This system follows the **Industrial Brutalism** skill (Tactical Telemetry
archetype) and applies one substrate palette everywhere.

---

## 1. Palette (one substrate — never mixed)

| Token | Value | Use |
|-------|-------|-----|
| `--bg` | `#0A0A0A` | Deactivated CRT substrate (never pure `#000`) |
| `--bg-deep` | `#080808` | Deepest panels / page backgrounds |
| `--panel` | `#121212` | Cards, tables, forms |
| `--panel-2` | `#1A1A1A` | Raised panels, hover states |
| `--line` | `#262626` | Structural 1px rules |
| `--line-soft` | `#1E1E1E` | Inner hairlines |
| `--ink` | `#EAEAEA` | White-phosphor primary text |
| `--muted` | `#8A8A8A` | Secondary text |
| `--dim` | `#5A5A5A` | Metadata, labels, unit IDs |
| `--accent` | `#E61919` | **Hazard red — the ONLY accent.** Thick rules, alerts, active states, vital data |
| `--accent-bright` | `#FF3B3B` | Hover/glow variant of hazard red |
| `--terminal-green` | `#4AF626` | ONE element only: the live-sync status dot. Never general text |

Rules:

- Red is used for strike-throughs, active navigation markers, structural
  dividing lines, and vital data highlights.
- Terminal green appears **only** on the live-sync indicator.
- All other states are monochrome grayscale.

## 2. Typography

### Structural (macro)
- Font: **Archivo Black / Inter ExtraBold** (fallback `Arial Black`).
- Scale: `clamp(2.5rem, 6vw, 5.5rem)` for page titles; `clamp(1.3rem, 2.4vw, 1.8rem)` for card values.
- Tracking: `-0.04em` to `-0.06em` (tight, architectural).
- Leading: `0.92` to `1.0`.
- Casing: uppercase.

### Data & telemetry (micro)
- Font: **JetBrains Mono / IBM Plex Mono** (`ui-monospace` fallback).
- Scale: `0.625rem`–`0.875rem` fixed.
- Tracking: `0.06em`–`0.12em`.
- Casing: uppercase for all metadata, navigation, labels, coordinates.

### Textural contrast (sparing)
- A single serif face (Playfair Display / Times) may appear in large
  editorial numerals or stamp-style blocks, always with a halftone/dither
  overlay. Used sparingly.

## 3. Geometry

- **Zero `border-radius`.** All corners are exactly 90°.
- Borders are `1px solid var(--line)`.
- Grid: strict `display:grid` with `gap:1px` + contrasting parent/child
  backgrounds to produce razor-thin lines (the "blueprint grid").
- Compartmentalization: every zone is visibly boxed by solid rules; `<hr>`
  spans full width to separate operational units.

## 4. Texture & degradation

- **CRT scanlines** on the root:
  ```css
  background-image: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,.22) 2px 4px);
  ```
- **Mechanical noise**: global low-opacity SVG turbulence overlay (already
  present as `body::after`).
- **Blueprint grid**: faint 1px grid lines behind panels.
- **Phosphor glow**: `box-shadow: 0 0 8px color-mix(in srgb, var(--accent) 40%, transparent)` on the live dot only.

## 5. Symbology

- ASCII framing on section headers: `[ COMPANIES ]`, `< DEAL FLOW >`,
  `>>> REVENUE`.
- Registration/copyright/trademark marks as structural glyphs: `® © ™`.
- Crosshairs `+` at grid intersections; repeating vertical barcode lines;
  unit codes like `UNIT / W-01`, `REV 2.6`.
- Semantic tags: `<data>`, `<samp>`, `<kbd>`, `<output>`, `<dl>`.

## 6. Components

| Component | Spec |
|-----------|------|
| **Page title** | Mono kicker (red), 90–100pt uppercase sans H1, hairline rule below |
| **Table** | `border-collapse: collapse`; mono cells; uppercase red headers; row hover `#141414`; 1px `#262626` rules |
| **Form** | 90° boxed fields; mono labels uppercase; red `:focus` outline; no radius |
| **Button** | Mono uppercase; `1px` border; primary = red fill + black text; quiet = `#1A1A1A` |
| **Card** | 90° box, `1px #262626`, no shadow, no radius |
| **Nav** | Sidebar `16.5rem`, hard right border, active item red left rule `3px` |
| **Status chip** | Mono uppercase; live dot = terminal green with phosphor glow |

## 7. Implementation notes

- Frontend tokens live in `frontend/src/styles/globals.css` (`:root`).
- The Django shell (`backend/templates/base.html`) declares the same tokens
  in its inline `<style>` block so server-rendered screens match the Astro
  shell exactly.
- Keep the `loop-*` class contract intact; only swap visual properties.
- React islands (board, dashboard) consume `var(--loop-*)` tokens, so the
  brutalist palette applies automatically; hard-code zero radius where the
  islands declare their own `border-radius`.
- Prefer `border-radius: 0` resets in one place (e.g. `* { border-radius: 0 }` guarded per component) to guarantee 90° corners.

## 8. Files

| File | What it defines |
|------|-----------------|
| `frontend/src/styles/globals.css` | Astro shell + island tokens |
| `frontend/src/components/AppShell.astro` | Sidebar/topbar/content chrome |
| `backend/templates/base.html` | Django shell chrome + shared table/form styles |
| `docs/DESIGN_SYSTEM.md` | This document |
