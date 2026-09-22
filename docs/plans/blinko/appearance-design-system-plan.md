# Blinko Appearance & Design-System Expansion Plan

> Status: Tier 1 IMPLEMENTED (radius, shadow, edge, density tokens shipped as
> `html[data-radius-scale|shadow-depth|edge-strength|density]` with per-workspace
> persistence). Decision answers recorded in §8.
> Extends the Settings → Appearance surface after the
> SURFACE STYLE (sharp/rounded/compact/wide) pass, following the same
> token-driven, per-workspace-persisted pattern already proven in production.

## 1. Current state (audited)

**Design tokens** (`:root` in `styles.css`): `--ink --muted --faint --panel
--accent --accent-soft --signal --danger --shadow --font-scale`, plus
`html[data-theme]` (light/dark/system), `html[data-accent]` (5 accents),
`html[data-font-scale]` (compact/default/large), and the new
`html[data-style-variant]` (sharp/rounded/compact/wide).

**Persistence chain**: option group click → `state.workspace` → `PATCH
/api/settings` → SurrealDB `workspace` record → `publicWorkspace` → applied via
`apply*()` functions writing `data-*` attributes on `<html>`.

**Existing appearance panel**: THEME MODE, ACCENT COLOR, TEXT SIZE, SURFACE
STYLE — all option-button grids (a select-based "dropdown" variant is the
documented next UI evolution for dense option sets).

## 2. Design-system principles to lock in

1. **Tokens, not literals** — every new option must express itself as a CSS
   custom property consumed by components; no component reads the option value
   directly.
2. **Per-workspace persistence** — new options ride the existing
   `/api/settings` chain; nothing in localStorage.
3. **Orthogonality** — options must compose (e.g., Rounded + Dark + Large
   without conflicts); each owns a distinct token axis.
4. **Reduced-motion & dark-mode parity** — every visual addition defines both.
5. **Server is the validator** — enum lists live in `server.mjs` (as
   `themes/accents/fontScales/styleVariants` do), never client-side only.

## 3. Proposed option roadmap

### Tier 1 — completes the current axes (low risk)
| Option | Values | Token/attr | Notes |
|---|---|---|---|
| Corner radius scale | none/s/subtle/soft/full | `--radius-scale` + `data-radius` | Supersedes per-variant hard-coded radii; styleVariant becomes a bundle of token presets |
| Edge contrast | soft/medium/strong | `--edge-strength` | Governs border opacity of panels/cards; helps low-vision users |
| Shadow depth | flat/raised/floating | `--shadow-depth` | Remaps `--shadow` presets; 'flat' disables offset shadows |
| Density | comfortable/cozy/compact | `--space-scale` | Spacing multiplier distinct from font scale |

### Tier 2 — new axes (medium)
| Option | Values | Notes |
|---|---|---|
| Focus/reading width | measure/normal/wide/full | `--content-measure`; wide ~72ch cap |
| Link style | plain/underline/dotted | `--link-decoration` |
| Motion level | full/reduced/off | `--motion-scale`; complements prefers-reduced-motion |
| Note list columns | 1/2/3/auto | Overrides grid for the notes view only |

### Tier 3 — personality (opt-in)
| Option | Values | Notes |
|---|---|---|
| Background texture | none/paper/grid/dots | Pure CSS gradients; must stay `pointer-events: none` fixed layers |
| Accent intensity | muted/standard/vivid | `--accent-saturation` clamp on the accent pipeline |
| Display font pairing | grotesk/mono-headings/rounded | Heading-family token; body stays unchanged |

### UI evolution for the panel itself
- Convert long option groups (density, radius, shadow) to **select dropdowns**
  to control panel height; keep core groups (theme/accent) as button grids.
- Add **live preview cards** (mini note, mini kanban card, mini calendar chip)
  inside the panel rendering with current tokens.
- Group sections under collapsible headers: *Base · Layout · Reading · Texture*.

### API surface (mirrors existing chain)
```
PATCH /api/settings  { radiusScale, edgeStrength, shadowDepth, density, ... }
GET  /api/settings → appearance: { themes, accents, fontScales, styleVariants, radiusScales, ... }
workspace record: + radius_scale, edge_strength, shadow_depth, density, ...
publicWorkspace:  + radiusScale, edgeStrength, ...
```
Each new option = schema field + enum constant + whitelist in PATCH +
publicWorkspace mapping + apply*() function + i18n en/ar keys. Identical
5-step recipe per option; the SURFACE STYLE implementation is the template.

## 4. Preset bundles (recommended UX layer)

Keep granular tokens but expose **presets** that set several at once:
- **Industrial (default)** — current sharp look, flat shadows, strong edges.
- **Paper** — subtle radius, soft edges, paper texture, serif-free.
- **Focus** — compact density, narrow measure, motion off.
- **Midnight** — dark theme + vivid accent + floating shadows.

Presets are just write-many PATCH calls; no new storage concept needed.

## 5. Sequencing

| Phase | Content | Estimate |
|---|---|---|
| A1 | Radius + shadow + edge tokens (Tier 1) + dropdown UI conversion | 1–2 d |
| A2 | Density + note-list columns + reading width | 1 d |
| A3 | Preset bundles + live preview cards | 1–2 d |
| A4 | Tier 3 texture/accent-intensity/font-pairing | 2 d |

## 6. Risks

- **Token drift** — components hard-coding values would break variants;
  mitigate with a stylelint rule (no raw hex/radius outside `:root`/tokens).
- **Option explosion** — cap Tier 3; every option must justify a token axis.
- **Dark-mode parity** — every new token needs a `[data-theme="dark"]` value.

## 7. Decision points

1. Ship presets (A3) before or after the full Tier 1 token set?
2. Dropdown vs button-grid conversion — all groups, or only long ones?
3. Should styleVariant presets remain, or dissolve into individual tokens with Industrial as default?

## 8. Decision record (2026-09-17)

1. **Tier 1 tokens first** — presets deferred until the token axes exist so presets are pure PATCH bundles, not new CSS.
2. **Button grids kept** — dropdown conversion deferred; all groups are uniform option-button grids (panel length acceptable at current option count).
3. **styleVariant stays as a base bundle** (curve/motion personality); the new radius/density/edge/shadow axes are orthogonal overrides on top of it, not replacements.

## 9. Test coverage (2026-09-17)

Tier-1 token persistence is locked in by
`runtime/tests/appearance-and-graph.spec.mjs` (dedicated Playwright config
`playwright.appearance.config.mjs`): applies Square/Compact/Floating/Strong via
the Appearance panel, verifies the `data-*` attributes on `<html>`, reloads, and
requires the attributes to return identically from SurrealDB. Token
application on boot (not only inside Settings) was a real bug this spec caught
and fixed. Run everything with `npm test` in `runtime/` (main suite +
appearance suite).

## 10. Implementation review (2026-09-17)

<!-- AI-generated: review needed -->
Beyond Tier 1 (recorded in §9), later passes shipped most of the remaining
roadmap in the same token-driven pattern — verified against the deployed
runtime:

| Planned | Shipped | Where |
|---|---|---|
| Panel UI evolution: grouped sections | ✅ Categorized panel: PRESETS · THEME · SURFACE · ELEMENTS with sublabels | `public/index.html` |
| Preset bundles (§4) | ✅ Industrial / Paper / Focus / Midnight — write-many PATCH bundles with swatches + active-state detection, definitions in `app.js` (`APPEARANCE_PRESETS`) | `app.js` L206–231 |
| New axes (§3) | ✅ `themeVariant` (default/corporate/luxury/pastel/perplexity — ported from Formints' OKLCH light+dark pairs), `buttonStyle` (default/outline/solid/ghost), `badgeStyle` (default/tinted/outline/solid) | `server.mjs` enums + PATCH whitelist; `data-theme-variant/button-style/badge-style` on `<html>` |
| Dark-mode parity | ✅ Variant palettes define light+dark counterparts per token (`--ink/--muted/--faint/--panel/--accent`) | `styles.css` |
| i18n parity | ✅ 595/595 en↔ar keys incl. all new option labels + preset cards | `i18n.mjs` |

**Gaps vs plan:** Tier 2 options (reading width, link style, motion level,
note-list columns) and Tier 3 textures (paper/grid/dots, accent intensity,
font pairing) are **not shipped** — they remain the next slice if wanted.
Dropdown conversion stays deferred per decision §8.2. Element axes
(button/badge) were an unplanned addition from the Formints theme review.

## Remarks & Notes
- Every new axis followed the 5-step recipe in §3 (schema + enum + PATCH whitelist + publicWorkspace + apply*); the recipe is the reliable path for the remaining tiers.
- Presets are pure PATCH bundles as planned — adding an axis later does not require touching preset code beyond the bundle object.
- Boot-path application of all axes (not just inside Settings) was a real bug caught by Playwright; `enterApp` now applies every token group at login.
