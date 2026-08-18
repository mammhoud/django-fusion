---
name: structa-industrial-ui
description: The Structa Cloud Swiss Industrial Print design system — a monorepo-personalized implementation of industrial-brutalist-ui fused with gpt-taste quality bars. Use for any frontend work in projects/precis/*/frontend (Astro + Tailwind v4 with fu-* design tokens) or django-fusion-rendered Django templates. Enforces matte paper + carbon ink + single aviation-red accent, zero border-radius, hard offset shadows, mono uppercase telemetry, BEM blocks, 2-3 line hero rule, no gradients/translucency, and light-only substrate with an inert dark block.
argument-hint: "<product frontend or page section>"
---

# Structa Industrial UI — Swiss Industrial Print for Structa Cloud

## 1. Skill Meta

**Name:** Structa Industrial UI (Swiss Industrial Print)
**Description:** The repo's canonical visual language, currently implemented in
`projects/precis/precis-ctc/frontend/src/styles/globals.css` and shared via the
`fu-*` design tokens. One substrate (light), one accent (aviation red), absolute
rejection of radius, gradients, and translucency. This skill encodes BOTH the
design law AND the real component inventory so new sections match the shipped
system without reinventing tokens.

## 2. Non-Negotiable Design Law

1. **One substrate.** Matte documentation paper only: `--fu-paper` = `60 17% 95%` (#F4F4F0), `--fu-card` = `55 13% 91%` (#EAE8E3). The `.dark` block is INTENTIONALLY inert (same values) so the theme toggle can never switch into a mixed substrate.
2. **One accent.** Aviation/hazard red `--fu-link` = `0 82% 50%` (#E61919). Every legacy alias (`--fu-teal`, `--fu-amber`, `--fu-live`, `--fu-teal-bright`) MUST resolve to the red. Status = red, not green. Never introduce a second hue.
3. **Carbon ink.** `--fu-ink` = `0 0% 4%` (#0A0A0A) for text and structural rules; `--fu-muted` = `45 5% 38%` for secondary text.
4. **Zero radius.** `* { border-radius: 0 !important }` is a global law. No rounded corners anywhere — including badges, avatars, pills, buttons.
5. **No gradients, no translucency, no blur.** Remove `backdrop-filter`, `bg-*/5` translucent fills, soft shadows. Hard offset presses only (`box-shadow: 4px 4px 0 0 var(--fu-ink)`).
6. **Mechanical noise.** Keep the global low-opacity (0.05) SVG grain on `body::after` — it unifies the paper substrate.
7. **Typography:** `--font-display` = "Archivo Black" (heavy neo-grotesque, uppercase, `clamp()` scales, line-height ~0.92, letter-spacing -0.03em); `--font-sans` = Inter; `--font-mono` = IBM Plex Mono for ALL telemetry/metadata/nav/buttons (uppercase, tracking 0.08-0.22em).

## 3. The Token System (real values — never invent new hues)

```css
--fu-paper: 60 17% 95%;     /* #F4F4F0 matte paper    */
--fu-ink: 0 0% 4%;          /* #0A0A0A carbon ink     */
--fu-muted: 45 5% 38%;      /* protocol grey          */
--fu-line: 42 8% 62%;       /* visible structural rule */
--fu-card: 55 13% 91%;      /* #EAE8E3 ruled sheet    */
--fu-link: 0 82% 50%;       /* #E61919 aviation red   */
--fu-link-dark: 0 86% 42%;  /* pressed ink red        */
```

Tailwind v4 `@theme inline` maps these to `bg-fu-paper`, `text-fu-ink`,
`border-fu-line`, `text-fu-link`, `bg-fu-card`, etc. Use the utility classes in
Astro; use `hsl(var(--fu-*))` in raw CSS. `.dark` block: same values (inert).

## 4. Component Inventory (real classes from globals.css)

Reuse these — they are already defined. Do NOT recreate equivalents.

### Document primitives
- `.tag-marker` — mono uppercase label framed as `[ LABEL ]` (ASCII brackets, `::before`/`::after`).
- `.doc-sheet` — section page with `border-t-2 border-fu-ink` (2px carbon rule between sections).
- `.status-line` — mono uppercase telemetry line with a square `.dot` (red, `animate-fusion-pulse`). Dot is SQUARE, never rounded.
- `.source-panel` — inverted industrial panel: `background: #0A0A0A; color: #F4F4F0`, mono, code tokens: `tok-tag` #E61919, `tok-attr` #F4F4F0, `tok-str` #9C9C92, `tok-com` #6E6E64 italic.
- `.eyebrow-pill` — square ASCII tag `+ ` before headings, carbon frame, mono uppercase 0.22em tracking.

### Buttons (rigid 90° plates)
- `.btn` base — `font-mono uppercase`, 0.78rem, tracking 0.08em; `:active { transform: translate(2px, 2px) }`.
- `.btn-primary` — red fill, `border: 2px solid var(--fu-ink)`, `box-shadow: 4px 4px 0 0 var(--fu-ink)`; hover reduces offset to 2px.
- `.btn-secondary` — paper fill, 2px carbon frame, hard offset shadow; hover inverts to ink fill / paper text.
- `.btn-outline` — transparent, 2px carbon frame; hover inverts.
- `.btn-white` — for dark panels: paper fill on ink, 2px frame.
- Text contrast law: dark surface = paper text; light surface = ink text. Red buttons use `text-fu-paper` (never white).

### Cards & shells
- `.card` — `bg-fu-card border-2 border-fu-ink`; hover: paper bg + `box-shadow: 4px 4px 0 0 var(--fu-ink)`.
- `.card-gradient` — ink plate (`bg-fu-ink text-fu-paper border-2 border-fu-ink`) — despite the name, NO gradients.
- `.bezel` / `.bezel__core` — rigid plate frame (2px ink border, line fill); `.bezel--ink` / `.bezel__core--ink` for inverted panels (#0A0A0A / #F4F4F0 35% border).

### BEM blocks (page sections — files in `frontend/src/components/blocks/`)
Each block: `hero`, `stats`, `features`, `cta`, `testimonials`, `faq`, `pricing`, `blog-preview`, `team`, `timeline`, `contact-form`, `capability`, `project`. Pattern: `block__element` (+ `--modifier`), 2px `border-t` carbon rules between sections, cards use the hover-offset law. Examples:
- `hero__heading` — font-display, uppercase, `clamp(2.6rem, 8vw, 6.5rem)`, line-height 0.92, letter-spacing -0.03em, `text-wrap: balance`. **Hero text MUST flow in 2-3 lines max** (gpt-taste rule): wide container, aggressive clamp.
- `hero__accent` — inline block with `.hero__accent-mark` = red underline bar (`hsl(var(--fu-link) / 0.85)`, height 0.28em), NOT italic, NOT skewed.
- `hero__eyebrow` — mono uppercase red with `[ ` ` ]` framing.
- `features__icon`, `stats__value`, `pricing__card--highlighted` (red hard offset, `md:-translate-y-2`), `timeline__dot--highlighted`, `testimonials__avatar` (square, 2px ink frame), `team__avatar` (square).
- Section headers use `.eyebrow-pill` + display heading + muted intro; generous vertical rhythm (sections feel like document chapters).

### Forms & badges
- `.input-field` — `w-full border-2 border-fu-ink bg-fu-card`, focus = red border (no ring, no translucency), placeholder `text-fu-muted`.
- `.form-label` — mono uppercase 0.14em tracking.
- `.badge-primary` — paper + red mono tag, 2px ink frame. `.badge-success` — INK plate with paper text (red is the status color; "success" renders as carbon). `.badge-white` — 2px #F4F4F0 frame on dark panels.

### Site shell
- `.site-header` — sticky, paper bg, `border-bottom: 2px solid var(--fu-ink)` (NO blur/translucency).
- `.site-nav a` — mono uppercase 0.78rem; hover = red.
- `.site-footer` — 2px carbon top border, muted text.

## 5. Motion (restrained, mechanical)

- Transitions are SHORT and mechanical: `0.15s ease` for hover states. No premium springs, no 0.45-0.8s luxury fades, no blur-in reveals.
- Scroll reveal: `.reveal-visible` toggles opacity/translateY (24px → 0, `0.6s ease`). No `scale`, no `blur()` in reveals.
- `.status-line .dot` and `.htmx-indicator__pulse` use `animate-fusion-pulse` (respect `prefers-reduced-motion: reduce` — keep the existing reduce block).
- Hard offset press on active: translate(2px, 2px).
- For GSAP/scroll-driven work, the repo's Astro apps have `frontend/src/fusion/motion.ts` / `scroll.ts` helpers — use those, keep the mechanical character (no springy overshoot).

## 6. gpt-taste Quality Bars (applied, adapted)

Keep these from gpt-taste, adapted to the industrial system:
- **Hero 2-3 line rule:** wide container (`max-w-5xl`+), `clamp(2.6rem, 8vw, 6.5rem)`, uppercase, balance. NEVER a 6-line wall.
- **No cheap meta-labels** like "SECTION 01" — use the mono `[ TAG ]` framing instead (real system: `tag-marker`, `hero__eyebrow`).
- **Button contrast:** verify legibility always (ink text on paper, paper text on red/ink). Invisible text = failure.
- **Intentional card counts:** 3-5 dense cards beat 8 sparse ones. Cards = square plates with carbon frames, no dead grid cells.
- **No emojis** in code, comments, or output. Strictly professional formatting.

## 7. Anti-Patterns (BANNED)

- Any border-radius, pill, rounded-full, circle (avatars/dots are squares).
- Gradients, `backdrop-filter`, translucency (`/5`, `/10` fills), soft multi-layer shadows, glow, blur reveals.
- Second hues: teal, amber, green, blue accents. ALL resolve to red.
- Italic serif display type (`--font-display` is Archivo Black, not Fraunces).
- `‹ ›` guillemet framing — use `[ ]` ASCII brackets.
- Bringing back the old luxury motion (0.45s springs, scale+fade reveals).
- Editing generated bundles instead of `src/styles/globals.css` or component styles.

## 8. Where Things Live

- **Tokens + global components:** `projects/precis/precis-ctc/frontend/src/styles/globals.css` (canonical; port to other product frontends by copying the token block and component layer).
- **Astro blocks:** `projects/precis/precis-ctc/frontend/src/components/blocks/*.astro` (Hero, Stats, Features, CTA, Testimonials, FAQ, Pricing, BlogPreview, Team, Timeline, ContactForm).
- **UI primitives:** `projects/precis/precis-ctc/frontend/src/components/ui/*.astro` (Button, Card, CodeBlock, Accordion, Breadcrumb...).
- **Layout:** `frontend/src/layouts/Layout.astro`; motion/theme helpers in `frontend/src/fusion/` (fragments.ts, htmx.ts, motion.ts, scroll.ts, sse.ts, theme.ts).
- **Backend-rendered (django-fusion):** use `{% comp "name" /%}` components and the same fu-* utilities; see structa-backend skill.
- **Other products:** precis-landing and precis-main have their own `frontend/src/styles/globals.css` — follow the same token law there (or note drift).

## 9. Pre-Flight Checklist (before writing UI)

1. Tokens: only the 7 values in §3; legacy aliases mapped to red.
2. Radius: 0 everywhere. No pill/circle/full classes.
3. Substrate: light only; `.dark` block left inert.
4. Typography: display = Archivo Black uppercase; metadata/mono = IBM Plex Mono; hero fits 2-3 lines.
5. Framing: `[ ]` ASCII brackets, not guillemets.
6. Components: reuse the inventory in §4 before writing new CSS.
7. Motion: 0.15s mechanical hovers; reveal = opacity/translateY only.
8. Contrast: dark=paper text, light=ink text, red buttons=paper text.
