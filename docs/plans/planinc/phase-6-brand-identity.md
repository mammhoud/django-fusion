# Phase 6 — PlanInc Brand Identity & Visual System

**Status:** Planned  
**Scope:** `application/tools/PlanInc/brandkit/`, `planing/app/src/styles/`, `src-tauri/`  
**Owner:** Design / Frontend  
**Depends on:** Phase 5 (CSS token system in place)  
**Can start in parallel with:** Phase 5

---

## Objective

Establish a premium, ownable brand identity for PlanInc — logo mark, color
system, typography, CSS tokens, Tauri window identity, and a brandkit
reference board — coherent across the app window, icon, documentation, and
any future marketing surfaces.

---

## Brand Strategy

| Axis | Decision |
|---|---|
| Category | Developer planning & project incubation tool |
| Audience | Technical founders, indie builders, product-focused engineering teams |
| Personality | Precise · minimal · path-driven · architectural · focused |
| Core metaphor | **Path + Incubation** — structured progress from raw idea to launched product. The mark is a path that opens and closes: like a development loop, like a contained circuit, like the letter P reduced to intent. |
| Visual mode | Dark Developer / Builder |
| What to avoid | Generic SaaS gradients · sparkle AI marks · overcrowded dashboards · cheap neon |

---

## Color System

```
Primary palette:

  #0d0d0f   Void Black      — app background
  #1e1f26   Slate Surface   — card / panel surfaces
  #2d2f3d   Border Layer    — dividers, subtle borders
  #f59e0b   Amber Accent    — primary interactive, highlight, brand accent
  #fbbf24   Amber Light     — hover state of accent
  #f8fafc   Cool White      — primary text
  #94a3b8   Muted Slate     — secondary text, labels
  #334155   Ghost           — disabled states

Accent CSS mapping (in the Alpine appearance system):
  accent: 'orange' → hsl(38, 92%, 50%)   ← matches #f59e0b
```

---

## Logo Mark

**Concept:** The `P` mark is a geometric construction where:
- A vertical baseline stroke (the `|` of the `P`) anchors the mark.
- An arc rises from the top of the baseline, travels right, and curves down —
  but instead of closing back to the baseline (like a standard `P`), it ends in
  an **open terminal that faces inward**, suggesting a circuit, a path not yet
  complete, an incubation space.
- The negative space inside the arc reads as a contained **seed** or **node**.
- At small sizes it reads cleanly as the letter `P`. At large sizes the
  construction logic becomes visible.

**Construction grid:**
- 48×48 unit base grid (scales to any target size)
- Vertical stroke: 6px wide, full height (0→48)
- Arc: radius 18px, centered at x=6, y=18, sweeps 270° (not the full 360°)
- Terminal: 4px rounded cap, turned 45° inward

**Variants:**
| Variant | Usage |
|---|---|
| Mark only (amber on void) | App icon, favicon, loading screen |
| Mark + wordmark horizontal | Main app header, README |
| Mark + wordmark stacked | Documentation cover, brandkit |
| Mark on light | Light theme mode (mark: `#0d0d0f`, wordmark: `#0d0d0f`) |
| Monochrome white | Dark backgrounds requiring contrast safety |

---

## Typography

| Role | Font | Weight | Notes |
|---|---|---|---|
| Display / headlines | Inter | 700 | App window title, section headers |
| Body / UI | Inter | 400, 500 | All UI text |
| Code / monospace accents | JetBrains Mono | 400 | Tag names, note IDs, timestamps, terminal-adjacent UI |
| Tagline | Inter | 300 italic | Used in brandkit only |

Fallback stack: `'Inter', 'system-ui', '-apple-system', sans-serif`

---

## Tagline

> **"From idea to orbit."**

Secondary tagline (for documentation):
> **"Plan clearly. Build completely."**

---

## Brandkit Directory (`application/tools/PlanInc/brandkit/`)

```
brandkit/
├── logo/
│   ├── planinc-mark.svg          ← The P mark (amber on transparent)
│   ├── planinc-wordmark.svg      ← Wordmark only
│   ├── planinc-lockup-h.svg      ← Horizontal lockup (mark + wordmark)
│   ├── planinc-lockup-v.svg      ← Vertical/stacked lockup
│   └── planinc-mark-white.svg    ← White version for dark overlays
├── icons/
│   ├── 32x32.png
│   ├── 128x128.png
│   ├── 128x128@2x.png
│   ├── icon.icns                 ← macOS
│   └── icon.ico                  ← Windows
├── colors/
│   └── planinc-palette.css       ← CSS custom property definitions
├── brand-guidelines.md           ← Full usage guide
└── brand-overview.png            ← 3×3 brandkit reference board
```

---

## Brandkit Image Prompt (3×3 Dark Developer/Builder)

Generate via the brandkit skill:

> Create a premium brand-kit overview image for "PlanInc".
>
> Brand strategy:
> - category: developer planning & incubation tool
> - audience: technical founders, indie builders
> - personality: precise, minimal, path-driven, architectural
> - core metaphor: a geometric P mark where the arc opens into an incubation
>   space — structured progress from raw idea to launched product
> - logo idea: vertical baseline + upward arc that terminates inward (not a
>   closed loop), suggesting a development circuit and the letter P; negative
>   space reads as a contained node/seed
>
> Layout: 3×3 grid on near-black `#0d0d0f` canvas with amber `#f59e0b` accent,
> strong gutters, and refined negative space.
>
> Panels:
> 1. Logo cover — large P mark + PlanInc wordmark, amber on void, extreme negative space
> 2. Logo construction — geometric grid: vertical stroke, arc construction
>    from circle, terminal angle, negative space isolation
> 3. Digital application — dark terminal/app window with amber tag chips and
>    a note card in the Planing UI
> 4. Brand essence — "From idea to orbit." in large Inter 300, amber accent on
>    "orbit", cool white on void
> 5. Color system — four chips: Void `#0d0d0f`, Slate `#1e1f26`, Amber `#f59e0b`,
>    White `#f8fafc`; monospace labels below each
> 6. Typography — Inter 700 display at 96pt, JetBrains Mono 400 code label
>    row below
> 7. Physical application — matte black business card, debossed P mark,
>    amber foil edge strip
> 8. Image direction — dark editorial: circuit board abstraction in muted
>    amber halftone, wide crop, low contrast, grain texture overlay
> 9. System detail — UI chip row: amber tag badges, note status chips, a
>    command-line fragment `$ planinc build` in JetBrains Mono amber
>
> Visual mode: Dark Developer / Builder
> Palette: `#0d0d0f` + `#1e1f26` + `#f59e0b` amber + `#f8fafc` white
> Style: premium, sparse, cinematic, intentional, polished, brand-guidelines
> deck, no clutter, no copied logos, no generic sparkles.

---

## CSS Token Application

`application/tools/PlanInc/planing/app/src/styles/brand.css`:

```css
:root {
  /* PlanInc brand tokens */
  --planinc-bg:           #0d0d0f;
  --planinc-surface:      #1e1f26;
  --planinc-border:       #2d2f3d;
  --planinc-accent:       #f59e0b;
  --planinc-accent-hover: #fbbf24;
  --planinc-text:         #f8fafc;
  --planinc-text-muted:   #94a3b8;
  --planinc-ghost:        #334155;

  /* Map to Alpine appearance system */
  --accent-h: 38;
  --accent-s: 92%;
  --accent-l: 50%;
}
```

Update `tailwind.config.js` to extend the color palette:
```js
theme: {
  extend: {
    colors: {
      brand: {
        bg:      'var(--planinc-bg)',
        surface: 'var(--planinc-surface)',
        accent:  'var(--planinc-accent)',
        text:    'var(--planinc-text)',
        muted:   'var(--planinc-text-muted)',
      }
    }
  }
}
```

---

## Tauri Config Update (`src-tauri/tauri.conf.json`)

```json
{
  "productName": "PlanInc",
  "version": "1.0.0",
  "identifier": "cloud.structa.planinc",
  "app": {
    "windows": [
      {
        "title": "PlanInc",
        "width": 1440,
        "height": 900,
        "minWidth": 720,
        "minHeight": 480
      }
    ]
  },
  "bundle": {
    "icon": [
      "../../brandkit/icons/32x32.png",
      "../../brandkit/icons/128x128.png",
      "../../brandkit/icons/128x128@2x.png",
      "../../brandkit/icons/icon.icns",
      "../../brandkit/icons/icon.ico"
    ]
  },
  "plugins": {
    "updater": null
  }
}
```

Remove the Blinko updater endpoint (`blinkospace/blinko/releases`).

---

## Default Workspace Settings

Update in `runtime/server.mjs`:
```js
const defaultWorkspace = {
  name: 'PlanInc workspace',
  theme: 'dark',
  theme_variant: 'default',
  accent: 'orange',          // ← amber maps to the 'orange' accent slot
  font_scale: 'default',
  style_variant: 'sharp',
  radius_scale: 'subtle',
  edge_strength: 'default',
  shadow_depth: 'default',
  density: 'cozy',
  button_style: 'default',
  badge_style: 'tinted',
};
```

---

## Verification

```bash
# 1. App window title is "PlanInc"
# 2. App icon (taskbar / dock) matches the P mark
# 3. Default theme is dark with amber accent
# 4. CSS custom properties are set to brand values
node -e "require('puppeteer').launch().then(b => b.newPage().then(p => {
  p.goto('http://localhost:1111');
  p.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--planinc-accent'));
}))"
# → " #f59e0b"

# 5. cargo tauri build produces a PlanInc-branded binary
cargo tauri build --target current
```
