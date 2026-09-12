# M4 — Theme Files & HTML Components

> **Status:** Proposed — awaiting review
> **Milestone:** M4 of [Workspace CRM Program](README.md)
> **Tags:** `#themes` `#design-tokens` `#variations` `#components` `#bem` `#ctc-research` `#precis-lms`
> **Contract:** [`THEME_DIRECTORY_STRATEGY.md`](../THEME_DIRECTORY_STRATEGY.md) (this plan implements it; it does not replace it)

<!-- AI-generated: review needed -->

## 1. Goal

Every styled surface gets a real `theme/` directory — tokens → light/dark
palettes → components — each stamped with its **variation id**, plus a portable
**HTML component layer** that the sample landings (M5) and the publishable
themes (M6) are assembled from.

## 2. Verified state

| Surface | Today | Missing |
|---|---|---|
| **Precis LMS** (`projects/precis/precis-main/`) — the "rock lms" reference | `assets/styles/theme/_light.scss`, `theme/_dark.scss` (Shape A started) | `theme/_tokens.scss`, `theme/_index.scss`, variation banner, `$theme-variation` |
| **CTC Research** (`projects/precis/precis-ctc/`) | `assets/styles/{_index.scss,_theme-tokens.scss,fusion-theme.scss,components/,vendors/}` + **generated** `assets/staticfiles/styles/theme`, `assets/static/js/theme` | A real `theme/` dir; tokens centralised; generated output must stay untouched |
| **Loop-CRM** (`projects/loop-crm/`) | `frontend/src/styles/globals.css` (single file, `--loop-*`) | Shape B banner + tokens/palettes split; `frontend/workspace.js` |
| **structa.cloud** | Root `structa.cloud/` directory exists and is **empty**; the deployed platform marketing surface is `precis-landing` (`fu-paper-ink`) | **Decision (M4.1):** own variation vs declared reuse of `fu-paper-ink` |
| Other products | Per `THEME_DIRECTORY_STRATEGY.md` Phases 1–8 (precis-landing done; syntara, formints pending) | Out of scope here unless a sample needs them |

Recommended variation ids follow the strategy's table: `precis-atelier`
(LMS), `fu-paper-ink` (CTC + structa.cloud reuse, unless M4.1 decides otherwise),
`loop-crm` (CRM).

## 3. Milestones (tasks)

### M4.1 — Confirm the two open homes (do first)

1. **structa.cloud theme home.** Confirm whether the platform site is the empty
   root `structa.cloud/` directory or `projects/precis/precis-landing/`. Record
   the answer in this plan's Remarks; create nothing until it is answered. If it
   is reuse, declare `fu-paper-ink` and add no new variation id.
2. **CTC theme home.** Confirm the authored SCSS root
   (`assets/styles/`) and record that `assets/staticfiles/**` and
   `assets/static/js/theme/**` are **generated/collected output** — never edited,
   never migrated by this plan.

### M4.2 — Precis LMS (`precis-atelier`)

- Add `assets/styles/theme/_tokens.scss` (color/type/space/radius/motion maps) and
  `theme/_index.scss` (`@use 'tokens'; @use 'light'; @use 'dark';`).
- Every file in `theme/` gets the mandatory banner:
  `// Variation: precis-atelier — LMS academy on the shared fusion layer`.
- Declare `$theme-variation: "precis-atelier" !default;` in `theme/_index.scss`.
- New tokens use the `--pc-*` namespace; the shared `--fu-*` fusion tokens stay
  for fusion/CMS pages (no forking, no re-declaration of fu values).
- Runtime selector: `<html data-theme="precis-atelier" data-mode="light|dark">` in
  the LMS shell templates.

### M4.3 — CTC Research (`fu-paper-ink`, shared)

- Create `assets/styles/theme/{_tokens,_light,_dark,_index}.scss`; migrate the
  values from `_theme-tokens.scss` and `fusion-theme.scss` (that pair becomes
  the `theme/` entry; `_index.scss` keeps `@use 'theme'` first).
- Banner on every theme file: `// Variation: fu-paper-ink — "the page as its own document" (shared)`.
- Since it reuses precis-landing's variation, it must **not** redeclare `--fu-*`
  values differently — the strategy's composition rule applies
  (`$theme-variation` assert at build).
- Leave `assets/staticfiles/**` and `assets/static/js/theme/**` untouched;
  confirm they are gitignored or explicitly recorded as generated.

### M4.4 — Loop-CRM (`loop-crm`, Shape B)

- `frontend/src/styles/globals.css` is the Tailwind v4 entry — keep one file but
  organise it: `/* 1. TOKENS */` (`@theme`), `/* 2. PALETTES */` (`:root` light,
  `.dark` overrides), `/* 3. COMPONENT LAYERS */`.
- Banner at the top: `/* Variation: loop-crm — dark CRM ops console */` and
  `--theme-variation: loop-crm;` on `:root`.
- Extract every inline hex into a `--loop-*` token (Done = `grep '#[0-9a-fA-F]\{3,6\}' frontend/src` outside `styles/` returns nothing).
- Add `frontend/workspace.js` per the strategy § 4 template (theme entry =
  bannered `globals.css`, tsx/html via `extraRules`) alongside the Astro build
  (strategy § 4.4: webpack never bundles `.astro`).

### M4.5 — HTML component layer (the portable unit)

Themes are only publishable if their sections are standalone. Per variation,
add a component dir that is framework-agnostic HTML + the theme's CSS classes:

```text
<project>/assets/styles/theme/
├── _tokens.scss / tokens.css
├── _light.scss / light.css
├── _dark.scss  / dark.css
└── components/                 # NEW — portable, no build step required
    ├── index.html              # every component rendered on one page (the visual index)
    ├── nav.html  hero.html  features.html  pricing.html
    ├── testimonials.html  faq.html  cta.html  footer.html
    └── README.md               # class contract + which tokens each block reads
```

- Every component uses the variation's BEM block prefix (`.fu-*`, `.pc-*`,
  `.loop-*`) and only reads tokens from the theme — no raw hex, no inline styles.
- Astro/Django equivalents import the same classes (an Astro component wraps the
  same markup); the HTML files stay the canonical reference so M5/M6 can render
  them without a framework.
- Add `components/README.md` per theme listing the block + the tokens it reads.

### M4.6 — `make theme-check` (contract enforcement)

One target per project (and a repo aggregate) asserting the strategy's rules:

```bash
grep -r '^// Variation:\|^/\* Variation:' <project>/assets/styles/theme   # exactly the project's id(s)
grep -rn '#[0-9a-fA-F]\{3,6\}' <project>/{src,assets,frontend/src} --include='*.css' --include='*.scss' \
  | grep -v '/theme/'                                                    # zero hits
grep -rn 'data-theme' <project>/templates <project>/frontend/src/layouts  # runtime selector present
```

- Wire into each project's existing `make check`; do not create a new CI system.
- Report the count rather than just failing, so a partially migrated project is
  measurable.

## 4. Verification

```bash
# LMS
cd projects/precis/precis-main && make check && make build          # webpack + astro per strategy §4.4
grep -r '^// Variation:' assets/styles/theme

# CTC
cd projects/precis/precis-ctc && make check
docker compose -f docker-compose.yml config -q                      # compose still valid

# CRM
cd projects/loop-crm/frontend && npm run build && npx astro check
npx webpack --config ../workspace.js --mode=production             # minified probe (strategy §4.5)

# Generated output untouched
git status --porcelain projects/precis/precis-ctc/assets/staticfiles | wc -l   # 0
```

Pass criteria: each surface has `theme/` (or a bannered theme section), the
banner grep returns only that surface's variation id, no hex outside `theme/`,
and components render standalone by opening `theme/components/index.html`.

## 5. Risks

| Risk | Mitigation |
|---|---|
| Editing generated/collected CSS (`ctc-research/assets/staticfiles/**`, `assets/static/js/theme/**`) | M4.1 records them as generated; verification asserts zero diff |
| Token drift between `:root` (CSS) and `_light.scss` (SCSS) in dual-dialect projects | Keep one direction: SCSS → compiled CSS; add the strategy's sync check rather than two hand-maintained copies |
| Two variations (`fu-paper-ink` shared by CTC + storefronts) diverge silently | `$theme-variation` assert + composition rule; a consumer never redeclares another's tokens |
| Renaming tokens breaks rendered pages | Verify computed styles before/after on the default theme; token renames land in their own commit |
| Client theme moves under the Formint merge plan | Target `formint-community/client/…`, not `formint-client/…` (see [program index](README.md) § Reconciliation) |

## 6. Remarks & Notes

- This plan implements the existing strategy's Phases 2/5/8 plus the two
  surfaces the strategy does not yet cover (CTC, structa.cloud) and adds the
  component layer the strategy assumed but never materialised.
- The variation inventory stays owned by `THEME_DIRECTORY_STRATEGY.md` § 3.3 —
  new ids here are appended there, not duplicated in a second table.
- "Theme files as added at ctc-research and another dir as rock lms" resolves to
  **CTC Research** and **Precis LMS** respectively (confirmed in review).
- Components are deliberately plain HTML so the sample library (M5) and the
  ThemeForest pack (M6) can render them without any product's build chain.
