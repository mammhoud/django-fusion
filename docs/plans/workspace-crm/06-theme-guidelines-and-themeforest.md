# M6 — Theme Guidelines & ThemeForest Publishing

> **Status:** Proposed — awaiting review
> **Milestone:** M6 of [Workspace CRM Program](README.md)
> **Tags:** `#guidelines` `#themeforest` `#marketplace` `#licensing` `#packaging` `#publish`
> **Precedent:** [`projects/formints/PUBLISH.md`](../../../projects/formints/PUBLISH.md) (marketplace publish kit — follow its shape)

<!-- AI-generated: review needed -->

## 1. Goal

Two deliverables: a **theme guidelines** document that makes theme authoring
mechanical, and a **ThemeForest publish pack** that turns selected samples
(M5) into submittable items — with the licensing and asset-rights problems
resolved *before* packaging.

## 2. Blockers found (must be resolved before any submission)

| # | Blocker | Evidence | Resolution owner |
|---|---|---|---|
| 1 | **No repository LICENSE file** | Root has no `LICENSE*`; only `projects/formints/LICENSE` (AGPL-3.0) and `libs/django-fusion/LICENSE` exist | Operator decision — record the licence that covers authored themes |
| 2 | **AGPL-derived blocks are not sellable** as a marketplace item | `formint-community` is AGPL-3.0; AGPL's copyleft is incompatible with ThemeForest's standard licence terms | Exclude AGPL-derived blocks from the publish set ([M5.5](05-landing-sample-library.md)) |
| 3 | **Client/product names in samples** | Sample content must contain no real client (CTC Research) or product branding | Rename fixtures to fictional names (already the case in M5's table — verify per fixture) |
| 4 | **Asset rights** | Fonts, icons, images, and diagrams each carry their own licence | Per-asset audit in the pack (`assets/LICENSES.md`), reusing PUBLISH.md's rights assertion |
| 5 | **No live demo target** | ThemeForest requires a working demo URL | Static host for `dist/` (per-item) — operator-owned |

## 3. Theme guidelines

`themes/GUIDELINES.md` — the authoring contract, referenced from
`docs/dev/customization/design-system.md` (per
[`THEME_DIRECTORY_STRATEGY.md`](../THEME_DIRECTORY_STRATEGY.md) Phase 0):

| Section | Rule |
|---|---|
| Variation identity | Mandatory banner (`// Variation: <id> — <unique point name>`) in every theme file; `$theme-variation` / `--theme-variation` declared; `<html data-theme="<id>">` |
| Tokens | `--{variation}-{role}-{state}`; no hex outside `theme/`; light + dark always present even when the product is light-only |
| Palette | Tokens → palettes → components only; a variation may inherit another, never redeclare its values |
| Components | BEM block prefix per variation; `theme/components/*.html` is canonical; Astro/Django wrappers consume the same classes |
| Content | No placeholder text; headings in order (one `h1`); labels on every control; visible focus; contrast ≥ 4.5:1 body / 3:1 large |
| Assets | Fonts/icons/images licensed and listed; no external CDN at runtime; no client names |
| Build | One theme entry per project; `workspace.js` for webpack surfaces; `.astro` compiled by Astro (strategy § 4.4); compiled output never hand-edited |
| Naming | Item/page names are fictional and kebab-cased; a sample id never contains a real customer or product name |

Checklist form (each item runnable): `grep` banner check, hex check,
`data-theme` check (M4.6), heading-order + focus + contrast checks in M5.6.

## 4. Publish set

**1 item = 1 variation = its samples as pages.** That matches how buyers shop
(a theme with N pages) and keeps the manifest library as the source of truth.

| Item | Variation | Pages (samples) | Category |
|---|---|---|---|
| `paper-ink-saas` | `fu-paper-ink` | 01, 04, 06, 08, 10, 12, 13, 18, 20 (9 pages) | Site Templates → Business / Corporate |
| `loop-crm-ops` | `loop-crm` | 02, 05, 07, 11, 14, 16, 19 (7 pages) | Site Templates → Business / SaaS |
| `atelier-learning` | `precis-atelier` | 03, 09, 15, 17 (4 pages) | Site Templates → Education |
| `structa-multi-niche` (optional) | mixed | a curated 8-page subset spanning three variations | Site Templates → Multipurpose |

Three items is the recommended minimum; the fourth only if the mixed set is
genuinely cohesive (mixed-variation bundles are a common rejection reason when
they look assembled rather than designed).

## 5. Deliverables per item

```text
themes/publish/<item>/
├── README.md                 # what it is, variation, page list
├── CHANGELOG.md              # versioned; first entry = 1.0.0
├── LICENSES.md               # every asset + its licence + origin
├── item/
│   ├── dist/                 # standalone HTML per page (from build-sample.mjs)
│   ├── css/theme.min.css     # compiled + minified theme
│   ├── js/ (only if progressive enhancement is required)
│   └── assets/               # fonts, icons, images actually referenced
├── docs/index.html           # buyer documentation (install, customize tokens, blocks, credits)
├── preview/                  # thumbnail + screenshots (see § 6)
└── submit.md                 # title, category, tags, description, features, demo URL, support policy
```

Packaging tool: `themes/tools/package-item.mjs` — assembles from the M5
manifests, minifies CSS (reuse the repo's existing CSS minifier rather than
adding one), writes `CHANGELOG`/`LICENSES`, and emits a zip + checksums
(mirroring `projects/formints/scripts/publish/generate-checksums.cjs`).
`--check` fails when `dist/` or the zip is stale.

## 6. Previews

| Asset | Spec | Source |
|---|---|---|
| Thumbnail | 590 × 300 (marketplace grid) | composed from the item's hero + palette |
| Screenshots | 1 per page, full-width, no browser chrome | automated capture per page (M5.6 pipeline) |
| Feature image | optional banner | brand-safe, no client logos |

Automate with the existing browser tooling already used for POS/CTC screenshot
runs rather than a new capture stack. Previews must show the **actual** HTML
output, not a design mockup — marketplace review compares the two.

## 7. Submission metadata (`submit.md`)

- **Title / category / tags** — variation-led, no customer names, no "Structa" product branding used as the item name.
- **Description** — what it is, who it's for, page list, block list, tech (static HTML + Tailwind CSS build), browser support statement.
- **Files included** — HTML, CSS, docs, assets; explicitly state what is *not* included (no backend, no CMS, no Stripe).
- **Demo URL** — static host per item.
- **Support policy** — 6 months included, documented scope, response window.
- **Changelog** — semantic version + dated entries.

## 8. Quality gate before submission

| Check | Command / method |
|---|---|
| Every page has no console errors | headless run per page |
| Responsive at 3 widths | screenshots at desktop/tablet/mobile |
| Heading order + labels + focus | M5.6 checks |
| Contrast | token pairs verified against WCAG AA |
| No external network dependency | grep for `http(s)://` in `dist/` (fonts/icons local) |
| No placeholder text | grep common filler strings |
| Docs complete | `docs/index.html` covers install + token change + block swap |
| Licences listed | `LICENSES.md` complete, no AGPL origin |
| Dist is generated, not edited | `package-item.mjs --check` clean |
| Zip opens with the documented structure | unzip + tree diff |

Also record **rejection-recovery notes**: the common causes (incomplete
documentation, placeholder content, generic design, unlicensed assets,
non-functional features, mixed inconsistent bundles) and the fix for each, so a
resubmission is mechanical.

## 9. Milestones (tasks)

1. **M6.1** Resolve blockers § 2 (licence decision, demo host, asset audit) — operator-owned; nothing is packaged before this.
2. **M6.2** `themes/GUIDELINES.md` + link from `docs/dev/customization/design-system.md`; fold M4.6 checks in as the runnable form.
3. **M6.3** `package-item.mjs` + `submit.md`/`LICENSES.md`/`CHANGELOG.md` templates; prove on one item.
4. **M6.4** Package item 1 (`paper-ink-saas`) end-to-end incl. previews + docs; hold as the reference item.
5. **M6.5** Package items 2–3 (`loop-crm-ops`, `atelier-learning`).
6. **M6.6** Quality gate (§ 8) wired as `themes/tools/package-item.mjs --check` + the browser checks.
7. **M6.7** Submission notes + rejection-recovery list; versioning/update procedure (how a repo theme change becomes a marketplace update).

## 10. Verification

```bash
node themes/tools/build-sample.mjs --all --check
node themes/tools/package-item.mjs --all --check
node themes/tools/audit-provenance.mjs            # licence gate (no AGPL origin)
grep -rn 'AGPL' themes/publish/*/LICENSES.md      # 0
unzip -l themes/publish/paper-ink-saas/*.zip      # structure matches § 5
```

Pass criteria: three items package reproducibly with complete docs, previews,
licences, and metadata; no AGPL-derived asset; the demo renders from the zip's
contents alone.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Submitting without a licence decision (blocker 1) | Hard gate in M6.1; the plan stops before packaging |
| AGPL contamination via a reused block | Provenance audit per block; publish set drawn only from permissive/owned sources |
| Marketplace rejection for generic design | Samples are variation-specific with real content fixtures; mixed bundles only when cohesive |
| Client/product names leaking into samples | Fictional-name rule in guidelines + a grep gate |
| Support burden after sale | Explicit support scope, 6-month policy, documented customization path |
| Divergence between repo theme and sold theme | Sold items are generated from manifests; versioning procedure (M6.7) keeps them in sync |
| Third-party font/icon licence drift | `LICENSES.md` per item + audit tool |

## 12. Remarks & Notes

- The request's "references but with design related to main theme" is honoured
  by drawing structural inspiration from existing landings while the samples are
  re-authored against our own tokens and components — no template source is
  copied, and provenance is recorded per block.
- Publishing is an **external, money-affecting action**: this plan produces the
  pack and the notes; uploading, pricing, and submission stay operator actions
  requiring explicit confirmation.
- `projects/formints/PUBLISH.md` remains the precedent for marketplace kits;
  M6 mirrors its shape (screenshots, listing copy, rights assertion) instead of
  inventing a competing format.
