# Theme Directory Strategy — Structa Cloud

Repo-wide plan to give every website/app/project a consistent, organized
`theme/` directory for styling (CSS/SCSS), each carrying its own **named design
variation** (a unique point-name identifier stamped into every SCSS file), with
a single documented contract, per-project migration steps, and verification.
The gold standard already exists: **precis-landing** (`fu-paper-ink`) — every
other project converges onto that layout under its own variation id.

---

## 1. Survey — current state (verified against the tree)

| Project | Framework / surface | Styling packages | Styles today | Theme dir? |
|---|---|---|---|---|
| **precis-landing** | Astro + Django/Wagtail (dual-render) | tailwind v4 (`@tailwindcss/vite`, `@tailwindcss/cli`), sass, postcss, webpack | `frontend/src/styles/globals.css` (single source, `--fu-*` tokens, `@source` for backend) + `assets/styles/` SCSS: `base/_tokens.scss`, `theme/_light.scss`, `theme/_dark.scss`, `layout/` (5), `components/` (14), `pages/` (6), `vendors/` | ✅ **yes — the model** |
| **precis** | Django/Wagtail LMS + webpack frontend | sass, postcss, webpack, css-loader/mini-css-extract | `assets/styles/_index.scss`, `fusion-theme.scss`, `vendors/`; **duplicated** `assets/static/styles/fusion-theme.scss` + committed build `assets/static/css/fusion-theme-compiled.css`; `frontend/src/styles/` `_variables.scss`, `_typography.scss`, `_buttons.scss`, `fusion.scss`, `globals.css` | ⚠️ partial — tokens in `_variables.scss`, no `theme/` |
| **syntara** | Django (dynaconf), no JS framework | sass (npm build in Makefile) | `assets/static/styles/main.scss` + 13 flat partials (`_variables`, `_reset`, `_layout`, `_navigation`, `_sidebar`, `_chat`, `_editor`, `_input`, `_enhancements`, `_animations`, `_responsive`, `_bootstrap-bem`) | ❌ flat, no `theme/` |
| **loop-crm** | Astro + React | tailwind v4 (`@tailwindcss/vite`), fontsource | `frontend/src/styles/globals.css` only, `--loop-*` tokens inline | ❌ single file |
| **formint-client** | Vue 3 + Tauri POS **and** Astro storefront | tailwind v4, daisyui, sass; heroicons/lucide | POS: `src/assets/main.css` + `src/assets/css/` (`pos-theme.css`, `base/`, `components/`, `utilities/`, README); Storefront: `frontend/src/styles/globals.css` (`--fu-*`, tailwind v4 + sass) | ⚠️ partial — `pos-theme.css` exists, no `theme/` dir |
| **formint-community** | React + Astro POS | tailwind v4 (`@tailwindcss/postcss` + `@tailwindcss/vite`), FlyonUI, tw-animate, lucide-react | `assets/styles/` `index.css`, `base/_variables.css`, `base/_reset.css`, `components/` (7), `fonts/` (3), `utilities/` | ⚠️ partial — tokens in `base/_variables.css`, no `theme/` |
| **formint-standard** | Astro POS (same layout as community) | tailwind v4, FlyonUI | `assets/styles/` identical shape (`index.css`, `base/`, `components/`, `fonts/`, `utilities/`) | ⚠️ partial — same as community |
| **formint-pro** | Astro + Django backend | tailwind v4 (`@tailwindcss/vite`), @tabler/icons | `frontend/src/styles/tokens.css` (semantic oklch tokens) + `global.css` | ⚠️ partial — `tokens.css` exists, no `theme/` |
| **formint-cloud** | React frontend | tailwind v4, geist, lucide-react, tw-animate | `frontend/assets/styles/index.css` only | ❌ single file |
| **formint / formintA / formintB / formintC** | legacy aliases | — | no styles (aliases/empty) | n/a |
| **www, pos, cms-fusion, lms, precis-lms** | legacy/retired boundaries | — | no styles | n/a |
| **projects/assets/static** | shared assets | — | nearly empty (`.gitkeep`) | n/a — shared sink |
| **projects/webpack**, **configs** | shared build/settings | — | shared webpack configs, Django settings | n/a |

### Cross-cutting observations

1. **Three styling dialects coexist:**
   - **SCSS partials** compiled by webpack (precis-landing, precis) or npm/sass (syntara)
   - **Tailwind v4 single globals.css** (loop-crm, formint-pro, formint-cloud, both Astro storefronts) — tokens in `:root` / `@theme`
   - **Tailwind v4 + layered CSS** (formint-community/standard `assets/styles/*.css`)
2. **Duplicated sources:** precis has `fusion-theme.scss` in two places + a committed compiled artifact.
3. **Naming drift:** `--fu-*` (precis-landing/storefronts), `--pos-*` (POS), `--loop-*` (CRM), `oklch` semantic tokens (pro), FlyonUI data-theme vars (community/standard).
4. **No `theme/` directory anywhere except precis-landing.** Tokens live in `base/_variables.*` or inline in globals.css.

---

## 2. The target contract — one `theme/` per project

Two shapes, one philosophy. The **contract** is: tokens → palettes (light/dark)
→ components, always behind a `theme/` entry, never inline hex in components.

### Shape A — SCSS (precis-landing, precis, syntara)

```text
<project>/assets/styles/
├── _index.scss              # entry — @use 'theme', base, layout, components, pages
├── theme/
│   ├── _tokens.scss         # design tokens (color/type/space/radius/motion) as maps or vars
│   ├── _light.scss          # :root / light palette (CSS custom props)
│   ├── _dark.scss           # .dark palette (or [data-theme="dark"])
│   └── _index.scss          # @use tokens; light; dark
├── base/                    # _reset, _typography, _elements
├── layout/                  # _header, _footer, _grid, _container, _sections
├── components/              # _buttons, _cards, _forms, _badges, _skeleton …
├── pages/                   # page-scoped overrides (only if needed)
└── vendors/                 # third-party overrides (swiper, jquery-ui …)
```

### Shape B — Tailwind v4 globals.css (loop-crm, formint-pro/cloud, storefronts)

Keep the single file as the entry, but split the theme layer into organized
blocks **in-file** (CSS is imported by the bundler; directories would need
@import chaining — supported, but the single-file convention is what Astro
scans). The `theme/` organization lives as a **directory of imported partials**
when the project already uses `@import` (community/standard), else as a
clearly-marked in-file theme section:

```css
@import "tailwindcss";

/* ── 1. TOKENS ─────────────────────────────────────────── */
@theme {
  --color-surface-*: …; --color-ink-*: …; --font-*: …;
}
/* ── 2. PALETTES ───────────────────────────────────────── */
:root  { /* light: --* tokens */ }
.dark  { /* dark: overrides */ }
/* ── 3. COMPONENT LAYERS (only what utilities can't do) ── */
@layer components { … }
```

For community/standard (already multi-file), adopt the directory form:

```text
<project>/assets/styles/
├── index.css                # @import theme/*, base/*, components/*, utilities/*
├── theme/
│   ├── tokens.css           # migrated from base/_variables.css
│   ├── light.css            # :root palette
│   └── dark.css             # [data-theme="dark"] palette
├── base/                    # _reset.css, typography
├── components/              # existing _card, _modal …
├── fonts/
└── utilities/
```

---

## 3. Design variations — each project's named identity

Every project gets a **unique variation identifier** — its design DNA name —
carried inside every SCSS/CSS file of that theme, so a file can be traced to
its variation at a glance and variations can coexist or compose without
collision. The identifier is the project's **unique point name**: the one
sentence that names the design's character (e.g. *paper + ink*, *machined
bezel*, *verdigris semantic*).

### 3.1 Variation naming rule

```text
{product-prefix}-{design-dna}          # lowercase, kebab-case
# examples
fu-paper-ink        # precis-landing — “the page as its own document”
precis-atelier      # precis LMS — academy/learning on the shared fusion layer
syntara-chat        # syntara — AI chat terminal, dark, bootstrap-BEM
loop-crm            # loop-crm — dark CRM ops console
formint-bezel       # formint-client POS — machined bezel register
formint-flyon       # formint-community / formint-standard — FlyonUI POS
formint-verdigris   # formint-pro — oklch semantic verdigris tokens
formint-cloud       # formint-cloud — FlyonUI + Remix cloud dashboard
```

### 3.2 Where the identifier lives in SCSS/CSS

Every theme file must carry the identifier in **all four surfaces**:

```scss
// ═══════════════════════════════════════════════════════════════════
// Variation: fu-paper-ink — “the page as its own document”
//   paper + ink, hairline rules, hypermedia-blue links, mono labels.
//   Theme dir: precis-landing/assets/styles/theme/
// ═══════════════════════════════════════════════════════════════════
$theme-variation: "fu-paper-ink" !default;   // 1. SCSS identity var

:root {
  // 2. Custom-property namespace: every token is prefixed with the
  //    variation id so no two variations can collide when composed.
  --fu-paper: 46 25% 98%;
  --fu-ink: 40 6% 10%;
}

// 3. data-theme attribute on <html> — the runtime variation selector.
//    <html data-theme="fu-paper-ink" data-mode="dark">
//    (variation id + mode combine to select the active palette)

// 4. BEM block prefix for shared component libraries
//    .fu-btn, .fu-card — components are namespaced by variation id.
```

**Contract rules:**

1. **The banner is mandatory** — every `theme/` file starts with the
   `// Variation: <id> — <unique point name>` banner. A grep for
   `^// Variation:` lists every variation in the repo.
2. **Token namespace = variation id** — SCSS: `--{variation-id}-{role}-{state}`;
   CSS: the same kebab prefix. Raw hex never appears outside the variation's
   own theme dir.
3. **Runtime selector** — `<html data-theme="{variation-id}">` + a
   `data-mode="light|dark"` attribute. Existing conventions (`.dark` class,
   FlyonUI `data-theme` variants) map onto this: the variation id *is* the
   FlyonUI theme name where FlyonUI is used.
4. **`$theme-variation` is the seam for composition** — a consumer project can
   `@use 'precis-landing/theme' as fu` and read `fu.$theme-variation`; it
   never re-declares another project's tokens.

### 3.3 Variation inventory (from the Phase-1 survey)

| Project | Variation id | Unique point name | Token prefix | Notes |
|---|---|---|---|---|
| precis-landing | `fu-paper-ink` | paper + ink, hairline rules, hypermedia-blue | `--fu-*` | the gold standard; `theme/_light` + `_dark` already exist |
| precis | `precis-atelier` | LMS academy on the shared fusion layer | `--pc-*` (new) over `--fu-*` shared | keeps fu tokens for fusion/CMS pages, adds pc tokens for LMS surfaces |
| syntara | `syntara-chat` | AI chat terminal, dark, bootstrap-BEM | `--sy-*` | 13 flat partials to reorganize under `theme/` |
| loop-crm | `loop-crm` | dark CRM ops console | `--loop-*` | single-file globals.css today |
| formint-client POS | `formint-bezel` | machined bezel register | `--pos-*` | pos-theme.css → theme/tokens.css |
| formint-client storefront | `fu-paper-ink` (shared) | same DNA as precis-landing | `--fu-*` | reuses the fu variation; no separate id |
| formint-community | `formint-flyon` | FlyonUI POS, warm paper surfaces | FlyonUI `data-theme` | same layout as standard |
| formint-standard | `formint-flyon` | FlyonUI POS (identical shape) | FlyonUI `data-theme` | do together with community |
| formint-pro | `formint-verdigris` | oklch semantic verdigris | `--color-*` semantic | tokens.css already exists |
| formint-cloud | `formint-cloud` | FlyonUI + Remix cloud dashboard | FlyonUI `data-theme` + `--fc-*` | single index.css today |

### 3.4 Composition (integration) rules

- **A variation may inherit another** — formint-client storefront is `fu-paper-ink`
  by identity; it does not fork tokens, it `@use`s the precis-landing theme.
- **No cross-project token reads** without `@use … as <prefix>` + the
  `$theme-variation` check (assert at build: `@if $theme-variation != 'x' { @error }`).
- **Shared `projects/assets/static/`** may hold a *neutral* `fusion-tokens.css`
  (no variation id) only when ≥2 variations genuinely consume it; every
  variation still declares its own id-prefixed tokens.

## 4. Per-project `workspace.js` — unified webpack build

Every project gets a **`workspace.js`** webpack config at its build root that
is the *single* way its styles/scripts get bundled. It extends the existing
shared factory (`projects/webpack/base.config.js`) so all projects inherit the
same loaders, minimizers, and bundle tracking — and it points every entry at
the **unified `theme/` dir** (Section 2), so the theme dir *is* the build input.

### 4.1 The template

```js
// <project>/webpack/workspace.js  (or <project>/workspace.js for flat apps)
/**
 * Variation: <variation-id> — <unique point name>
 * Unified webpack build — bundles the theme dir + TS/TSX/HTML into versioned
 * bundles, minified in production. Extends projects/webpack/base.config.js.
 */
const path = require('path');
const createConfig = require('../../webpack/base.config');
const HtmlWebpackPlugin = require('html-webpack-plugin'); // where an HTML shell exists

const PROJECT_ROOT = path.resolve(__dirname, '..');

module.exports = createConfig({
  name: '<variation-id>',            // e.g. 'fu-paper-ink'
  projectRoot: PROJECT_ROOT,

  // ── The unified theme dir is the ONLY style entry ───────────────────
  entries: {
    theme: [
      'assets/styles/theme/_index.scss',   // Shape A — SCSS theme entry
      // 'assets/styles/theme/index.css',   // Shape B — layered CSS theme entry
    ],
    app: [
      'assets/static/js/app.tsx',          // TS/TSX entry (babel-transpiled)
    ],
  },

  // ── Output (minified in production via CssMinimizer + Terser, already
  //    wired in base.config.js optimization) ───────────────────────────
  outputPath: 'assets/bundles',
  outputPublic: '/static/bundles/',

  // ── Extra rules — ts/tsx, html, and .astro interop ──────────────────
  extraRules: [
    {
      test: /\.tsx?$/,
      use: {
        loader: 'babel-loader',
        options: { presets: ['@babel/preset-env', '@babel/preset-react', '@babel/preset-typescript'] },
      },
    },
    { test: /\.html$/, use: 'html-loader' },
    // .astro is NOT bundled here — Astro compiles .astro through its own
    // Vite pipeline (astro build). workspace.js covers the theme + TS/TSX +
    // HTML shell; the Astro output is collected separately and the two are
    // joined at deploy (see 4.4).
  ],

  // ── Theme dir on the sass include path ──────────────────────────────
  scssIncludes: ['assets/styles/theme'],

  extraPlugins: [
    // Only where an HTML shell exists (e.g. a POS/CRM static host).
    new HtmlWebpackPlugin({ template: 'src/index.html', inject: 'body' }),
  ],
});
```

### 4.2 What `base.config.js` already gives every `workspace.js`

- **SCSS/CSS pipeline:** `mini-css-extract-plugin` → `css-loader` →
  `postcss-loader` → `sass-loader` (rules in `common.config.js`).
- **Style minification:** `CssMinimizerPlugin` + `TerserPlugin`
  (`drop_console`, comments stripped) when `argv.mode === 'production'`.
- **Bundle tracking:** `webpack-bundle-tracker` → `bundles.json` for
  `django-webpack-loader` (`{% render_bundle %}`), or the plain dist for
  Astro/Vite consumers.
- **Hashing + split chunks:** `[name].[contenthash:8]` filenames in prod,
  `vendor` cache group, single runtime chunk.
- **Copy step:** `assets/static/libs → bundles/libs` for vendored statics.

### 4.3 Per-project wiring

| Project | workspace.js location | Theme entry (unified dir) | ts/tsx | html | .astro | Output |
|---|---|---|---|---|---|---|
| precis-landing | `webpack/workspace.js` (rename of `precis-landing.config.js`) | `assets/styles/theme/_index.scss` | ✓ | ✓ | Astro own build | `backend/assets/static/bundles` |
| precis | `webpack/workspace.js` (rename of `precis.config.js`) | `assets/styles/theme/_index.scss` | ✓ | ✓ | n/a | `assets/bundles` |
| syntara | `workspace.js` (flat app) | `assets/static/styles/theme/_index.scss` | ✓ | ✓ | n/a | `assets/static/bundles` |
| loop-crm | `frontend/workspace.js` | `src/styles/globals.css` (bannered theme section) | ✓ tsx | ✓ | Astro own build | `frontend/dist` |
| formint-client POS | `workspace.js` | `src/assets/css/theme/index.css` | ✓ vue+ts | ✓ | n/a | `src-tauri`/bundles |
| formint-client storefront | `frontend/workspace.js` | `frontend/src/styles/globals.css` | ✓ ts | ✓ | Astro own build | `frontend/dist` |
| formint-community | `workspace.js` | `assets/styles/theme/index.css` | ✓ tsx | ✓ | Astro own build | `dist` |
| formint-standard | `workspace.js` | `assets/styles/theme/index.css` | ✓ tsx | ✓ | Astro own build | `dist` |
| formint-pro | `frontend/workspace.js` | `src/styles/tokens.css` + `global.css` | ✓ tsx | ✓ | Astro own build | `frontend/dist` |
| formint-cloud | `workspace.js` | `assets/styles/theme/index.css` | ✓ tsx | ✓ | n/a | `dist` |

### 4.4 Astro interop rule (important)

Astro compiles `.astro` itself (`astro build` via Vite). The `workspace.js`
**never** tries to bundle `.astro` files. The contract is:

1. `workspace.js` bundles the theme dir + TS/TSX + HTML shell → hashed, minified
   assets (for Django `{% render_bundle %}` or a static host).
2. Astro's build consumes the *compiled* theme output (imported CSS) and emits
   its own `dist/` with `.astro` pages + bundled styles.
3. A Makefile target per project (`make build`) runs **both** pipelines and
   reports both bundles — the plan's phases add this to each project's Makefile.

### 4.5 Minification guarantee

Every `workspace.js` inherits `minimize: !isDev` from `base.config.js`. The
phase check for each project is: `npx webpack --config webpack/workspace.js --mode=production`
and assert the emitted `theme.*.css` is minified (no comments, no newlines in
rules) and `theme.*.js` has `drop_console` applied.

## 5. Implementation plan — per project

### Phase 0 — shared groundwork (do first, once)

1. **Document the contract** — this file becomes `docs/dev/customization/design-system.md` with both shapes, naming rules (`--{product}-{role}-{state}`), and the rule "components reference tokens, never hex".
2. **De-duplicate precis** — decide the canonical `fusion-theme.scss` location; remove the copy and the committed `fusion-theme-compiled.css` (gitignore the build output).
3. **Shared tokens parity check** — precis-landing `theme/_light.scss` ↔ storefront `globals.css` `:root` are already mirrors; keep a note that the Astro `:root` and the Django SCSS theme must stay in sync (same values, two dialects).
4. **Ship the `workspace.js` template** — copy Section 4.1 into `projects/webpack/workspace.template.js` (a documented scaffold, not a required module) so every phase can drop it into the project, fill the entries, and extend `base.config.js`.
5. **Add `extraRules` + `extraPlugins` support to `base.config.js`** if not already accepted (the factory currently takes entries/aliases/scssIncludes — extend the opts so `workspace.js` can register ts/tsx/html rules + HtmlWebpackPlugin cleanly).

### Phase 1 — precis-landing (already done — verify + pin)

**Variation: `fu-paper-ink`** — the banner + token namespace already exist; this phase only pins them.

- [ ] Confirm every `assets/styles/**` file starts with the `// Variation: fu-paper-ink — “the page as its own document”` banner.
- [ ] Confirm `assets/styles/_index.scss` imports `theme` first and `theme/_index.scss` imports tokens → light → dark.
- [ ] Confirm `<html data-theme="fu-paper-ink">` is the runtime selector (and `data-mode` for light/dark).
- [ ] Rename `webpack/precis-landing.config.js` → `webpack/workspace.js` (entry `theme: ['assets/styles/theme/_index.scss']` + `app` TS entry) — keep the same output path so `{% render_bundle %}` names don't change.
- [ ] Add a CI/check step: `make check` asserts `globals.css :root` equals `theme/_light.scss` values (a tiny script or test), plus the 4.5 minification probe.

### Phase 2 — precis (SCSS Shape A)

**Variation: `precis-atelier`** — LMS surfaces get `--pc-*` tokens on top of the shared `--fu-*` fusion layer.

1. Create `assets/styles/theme/{_tokens,_light,_dark,_index}.scss` — every file banner starts `// Variation: precis-atelier — LMS academy on the shared fusion layer`; new `--pc-*` tokens are declared alongside the inherited `--fu-*` (via `@use '../precis/landi/theme' as fu` is *not* required — fu tokens are simply re-declared with the same values where LMS pages need them, but prefer importing the shared fusion theme when the fusion layer is present).
2. Move `_typography.scss`, `_buttons.scss` under `base/` / `components/`; keep `fusion.scss` + `globals.css` as entries.
3. Rename `webpack/precis.config.js` → `webpack/workspace.js` (theme entry + ts/tsx/html rules from the 4.1 template); update the `package.json` scripts (`build`, `dev`, `clean`) and Makefile `build` target to the new filename.
4. Delete the duplicated `assets/static/styles/fusion-theme.scss` and add `assets/static/css/*.css` to gitignore.
5. Add `$theme-variation: "precis-atelier" !default;` to `theme/_index.scss`.
6. **Verify:** `make build` (webpack + minified CSS probe per 4.5) + `python manage.py check`; the LMS renders with identical tokens (compare computed `--` values before/after); `grep -r '^// Variation:' assets/styles` shows `precis-atelier` everywhere.

### Phase 3 — syntara (SCSS Shape A)

**Variation: `syntara-chat`** — dark AI chat terminal; new `--sy-*` token namespace.

1. `git mv assets/static/styles/{_variables.scss → theme/_tokens.scss}`; create `theme/_light.scss`, `theme/_dark.scss` (from the current single palette, add dark overrides where the app already has them), `theme/_index.scss` — banners `// Variation: syntara-chat — AI chat terminal, dark, bootstrap-BEM`, `$theme-variation: "syntara-chat" !default;`.
2. Rename the flat partials' tokens from the legacy names to `--sy-*` (role-based, e.g. `--sy-bg`, `--sy-ink`, `--sy-accent`) and group: `base/` (_reset), `layout/` (_layout, _navigation, _sidebar, _responsive), `components/` (_chat, _editor, _input, _enhancements, _bootstrap-bem, _animations), keep `main.scss` as the entry with `@use 'theme'` first.
3. Create `workspace.js` at the project root (theme entry + ts/tsx/html rules) and repoint the Makefile `build` target to `npx webpack --config workspace.js`.
4. **Verify:** `make build` compiles (minified CSS probe per 4.5); chat UI renders with the same palette; dark mode (if present) flips; `grep -r '^// Variation:'` shows only `syntara-chat` in the theme dir.

### Phase 4 — formint-client (two surfaces)

**Variations: `formint-bezel`** (POS) and **`fu-paper-ink`** (storefront, shared — no fork).

**POS (Vue):** `src/assets/css/` already has `base/ components/ utilities/` + `pos-theme.css`.
1. `git mv src/assets/css/pos-theme.css → src/assets/css/theme/tokens.css`; banner `// Variation: formint-bezel — machined bezel register`; add `$theme-variation: "formint-bezel" !default;` (CSS: `--pos-*` prefix already matches the variation id namespace — keep `--pos-*` as the documented prefix for this variation). Split any dark overrides into `theme/dark.css`; add `theme/index.css` imported by `main.css` (`@import "./css/theme"`).
2. Keep `main.css` as the Tailwind entry (`@import "tailwindcss"` + daisyui plugin) — theme dir is purely the token layer; set `<html data-theme="formint-bezel">` in the POS shell.
3. Create `workspace.js` — theme entry `src/assets/css/theme/index.css`, `app` TS entry, `html-loader` for any shell, output to the Vite/Tauri static dir; keep Vite as the dev server (workspace.js is the production bundle path).
4. **Verify:** `vue-tsc --noEmit` + `pnpm lint` + production `workspace.js` build emits minified theme CSS; live check the register (Dashboard/Menu) tokens unchanged.

**Storefront (Astro):** `frontend/src/styles/globals.css` is the single source — Shape B in-file: add the `/* 1. TOKENS 2. PALETTES 3. LAYERS */` banner and ensure `:root`/`.dark` blocks are contiguous. Banner line: `/* Variation: fu-paper-ink — “the page as its own document” (shared) */`; no structural move (Astro scans one file). `frontend/workspace.js` covers any non-Astro TS/HTML shell assets (4.4 rule).

**Storefront (Astro):** `frontend/src/styles/globals.css` is the single source — Shape B in-file: add the `/* 1. TOKENS 2. PALETTES 3. LAYERS */` banner and ensure `:root`/`.dark` blocks are contiguous. No structural move (Astro scans one file).

### Phase 5 — formint-community & formint-standard (Shape B directory)

**Variation: `formint-flyon`** (both editions, same id).

Both have identical `assets/styles/` shape:
1. `git mv assets/styles/base/_variables.css → assets/styles/theme/tokens.css`; add `theme/light.css`, `theme/dark.css` (FlyonUI `data-theme` palettes → `:root`/`[data-theme="dark"]`); every file banner `/* Variation: formint-flyon — FlyonUI POS, warm paper surfaces */`.
2. Update `index.css` to `@import "theme/tokens.css"; @import "theme/light.css"; @import "theme/dark.css"; …` before base/components; set `<html data-theme="formint-flyon">` in both Astro layouts.
3. Keep `base/_reset.css` and the components dir as-is.
4. Add `workspace.js` in each edition (theme entry `assets/styles/theme/index.css` + tsx/html rules); repoint the Makefile/package scripts.
5. **Verify:** build the Astro/React app; FlyonUI theme variables resolve; light/dark toggle works; `grep -r '^/\* Variation:' assets/styles` lists `formint-flyon` on every file; production `workspace.js` output is minified (4.5).

### Phase 6 — formint-pro (Shape B single-file + tokens)

**Variation: `formint-verdigris`** — oklch semantic tokens, verdigris brand.

1. `frontend/src/styles/tokens.css` is already the token layer — single-file convention → keep `tokens.css` (it's referenced), append `:root`/`.dark` palette blocks, and add the banner `/* Variation: formint-verdigris — oklch semantic verdigris */` at the top of both `tokens.css` and `global.css`; add `$theme-variation` equivalent via the CSS custom property `--theme-variation: formint-verdigris;` on `:root`.
2. Add `frontend/workspace.js` (theme entry `src/styles/tokens.css` + `global.css`, tsx/html rules) wired into the package scripts alongside `astro build` (4.4 interop).
3. **Verify:** `astro check` + build + `workspace.js` minified probe; POS pages keep the verdigris palette.

### Phase 7 — formint-cloud (Shape B single-file)

**Variation: `formint-cloud`** — FlyonUI + Remix cloud dashboard.

1. `frontend/assets/styles/index.css` is the only style file — add the in-file theme banner (`/* Variation: formint-cloud — FlyonUI + Remix cloud dashboard */` + tokens → `:root` light → `.dark`), pulling any inline colors into tokens; set `<html data-theme="formint-cloud">`; FlyonUI variant imports stay (they are the theme engine).
2. Add `workspace.js` (theme entry `assets/styles/theme/index.css` or the bannered `index.css`, tsx/html rules); repoint scripts.
3. **Verify:** app builds; colors resolve from tokens; production CSS minified (4.5).

### Phase 8 — loop-crm (Shape B single-file)

**Variation: `loop-crm`** — dark CRM ops console (`--loop-*` prefix = variation namespace).

1. `frontend/src/styles/globals.css` — same in-file theme banner (`/* Variation: loop-crm — dark CRM ops console */`); `--loop-*` tokens already exist, group them under a `/* THEME: tokens */` block, split `:root` (light) from any dark overrides; add `--theme-variation: loop-crm;` to `:root`.
2. Add `frontend/workspace.js` (theme entry = bannered globals.css, tsx/html rules) alongside the Astro build (4.4 interop).
3. **Verify:** `astro check` + build + `workspace.js` minified probe; CRM renders with the existing `--loop-*` palette.

### Phase 9 — shared assets

- `projects/assets/static/` remains the sink for genuinely shared CSS (e.g. a future `fusion-tokens.css` consumed by multiple products). Only add there when ≥2 products share the file; keep product themes in product dirs.

---

## 6. Cross-cutting integration steps

1. **Every theme dir gets an `_index.scss`/`index.css`** that is the only file the build imports — components can never import tokens directly (single seam).
2. **Tokens naming = variation namespace:** `--{variation-id}-{role}-{state}` (`--fu-*`, `--pos-*`, `--loop-*` stay and are documented as the id prefixes for their variation; new tokens follow the pattern). No raw hex outside `theme/`.
3. **Dark mode:** every project gets a `theme/_dark` (SCSS) or `.dark` block (Tailwind) even if the current product is light-only — the seam exists, values default to light copies.
4. **Variation banner everywhere:** `grep -r '^// Variation:' <project>/assets/styles` (or `^/\* Variation:`) must list exactly the project's variation id(s) on every file — add to CI as `make theme-check`.
5. **`$theme-variation` / `--theme-variation` seam:** the identity var is declared in `theme/_index.scss` (SCSS) or `:root` (CSS) and is the assert point for composition (`@if $theme-variation != '<expected>' { @error }` in a build-time test).
6. **Build wiring = one `workspace.js` per project:** every project's webpack config is `webpack/workspace.js` (or root `workspace.js`) extending `projects/webpack/base.config.js`; the theme dir is the only style entry; ts/tsx/html rules come from the Section 4 template; `.astro` is compiled by Astro itself (4.4). Makefile/package scripts point at `workspace.js`.
7. **Minification is inherited and probed:** `CssMinimizerPlugin` + `TerserPlugin` come from `base.config.js` (`minimize: !isDev`); each phase's verify step asserts the emitted `theme.*.css`/`theme.*.js` is minified (no comments, `drop_console`).
8. **Do not touch generated output:** compiled CSS (`static/css/*.css`, `dist/`, bundles) is never edited — only sources.

---

## 7. Suggested execution order

Every phase first stamps the project's **variation id** (banner + token
namespace + `$theme-variation`/`--theme-variation` + `data-theme`), then moves
files.

| Step | Variation id | Effort | Risk | Why this order |
|---|---|---|---|---|
| Phase 0 groundwork + precis de-dup + workspace.js template + `base.config.js` extraRules | — | S | M | Contract first; removes the one committed-artifact problem; gives every phase its build scaffold |
| Phase 2 precis | `precis-atelier` | M | M | Largest SCSS surface; establishes Shape A outside LF |
| Phase 3 syntara | `syntara-chat` | M | M | Second SCSS surface; renames 13 partials to `--sy-*` |
| Phase 5 community + standard | `formint-flyon` | M | L | Nearly identical — do together |
| Phase 4 formint-client | `formint-bezel` + `fu-paper-ink` | M | M | Two surfaces; POS is the active dev target |
| Phases 6–8 (pro, cloud, loop-crm) | `formint-verdigris` / `formint-cloud` / `loop-crm` | S–M | L | Single-file banner passes — fast wins |
| Phase 1 precis-landing verify + pin | `fu-paper-ink` | S | L | Already correct; just add the sync check |

**Total:** ~9 focused PRs (or 4-5 if batched per product family), each with the
project's existing `make check`/`make build` + `manage.py check` as the gate,
plus a `grep '^// Variation:'` pass per project as the variation check.

---

## 8. Definition of done

- [ ] Every project with styles has a `theme/` dir (directory form) or a
      clearly-bannered theme section (single-file form) with tokens → light → dark.
- [ ] **Every theme file carries its variation banner** — `grep -r '^// Variation:'`
      (or `^/\* Variation:`) returns only the project's own variation id(s),
      and each file's token namespace matches its variation id.
- [ ] `$theme-variation` (SCSS) or `--theme-variation` (CSS) is declared per
      project; composition asserts on it.
- [ ] Runtime selector `<html data-theme="{variation-id}">` present in each
      project's shell/layout (or documented mapping onto FlyonUI data-theme).
- [ ] Zero hex colors outside theme files (grep `#[0-9a-fA-F]{3,6}` across
      components returns only theme).
- [ ] **Every project has a `workspace.js`** (extending `projects/webpack/base.config.js`)
      whose theme entry is the unified `theme/` dir; `npx webpack --config … --mode=production`
      emits hashed, minified `theme.*.css`/`theme.*.js` (probe per 4.5) and `bundles.json`
      for `django-webpack-loader` (or a plain dist for Astro/Vite consumers).
- [ ] `make check`-equivalent passes per project; rendered pages are pixel-
      identical in the default theme before/after (compare computed styles).
- [ ] precis duplicated SCSS + committed compiled CSS removed.
- [ ] Contract documented in `docs/dev/customization/design-system.md` and referenced by
      each project's AGENTS.md.
- [ ] `.astro` files are never bundled by webpack — the 4.4 interop rule is
      documented in each Astro project's AGENTS.md (Astro compiles its own pages).
