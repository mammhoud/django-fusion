# M5 — Landing Sample Library (20 Samples from Merged Components)

> **Status:** Proposed — awaiting review
> **Milestone:** M5 of [Workspace CRM Program](README.md)
> **Tags:** `#samples` `#landing-pages` `#components` `#merge` `#provenance` `#themes`
> **Home:** repo-root `themes/` (shared samples) — depends on [M4](04-theme-files-and-components.md)

<!-- AI-generated: review needed -->

## 1. Goal

Twenty landing-page samples that are **compositions, not copies**: each sample
declares a theme variation plus an ordered block manifest, and a build tool
assembles it from the merged canonical component library. Every sample builds
standalone and every block traces back to the product component it came from.

## 2. Where this lives

```text
themes/                                  # repo-root shared samples library (new)
├── README.md                            # purpose, provenance + licensing rules
├── INDEX.md                             # the 20 samples table (below)
├── registry.json                        # canonical block names ← merged aliases ← source paths
├── fixtures/                            # content per archetype (no lorem ipsum filler)
├── tools/
│   ├── build-sample.mjs                 # manifest → standalone dist/
│   └── audit-provenance.mjs             # every block resolves + licence is allowed
└── samples/
    ├── 01-northwind-saas/
    │   ├── sample.json                  # { variation, blocks[], fixture }
    │   ├── content.json
    │   └── dist/index.html              # generated — never hand-edited
    └── … (20)
```

> The request's "desktop themes dir `documents/themes`" maps here: the shared
> **samples** library is `themes/`. Authored theme sources stay in each
> project's `theme/` dir (M4) — the samples dir never becomes a second source
> of truth. No `documents/` directory is created.

## 3. Step 1 — find and merge related components

Component discovery, then merge by purpose (keeping one canonical block per
purpose per variation):

| Source surface | Path | Contributes |
|---|---|---|
| Precis Landing | `projects/precis/precis-landing/` (frontend sections + Django-stream blocks) | hero, feature grid, pricing, FAQ, CTA band, footer, testimonial, stats |
| CTC Research | `projects/precis/precis-ctc/assets/styles/components/`, `frontend/src/components/` | research/program blocks, publication lists, team/bio, contact |
| Loop-CRM landing | `projects/loop-crm/frontend/src/components/landing/` | product hero, dashboard preview, integration grid, comparison |
| Formint landings | `projects/formints/formint-pro|cloud/frontend/` | POS/vertical blocks, device mockups, feature table |
| Syntara | `projects/syntara/` | chat/terminal hero, editor preview |
| docs / brand | `docs/design/`, root `assets/*.svg` | brand marks, diagram blocks |

**Merge rules**

1. Same purpose + different names → one canonical block; the older name becomes a `registry.json` alias so nothing silently disappears.
2. Same purpose + genuinely different DNA → two blocks, explicitly named (`hero-cinematic`, `hero-terminal`), never a fork of one block with inline overrides.
3. A block that cannot be expressed without product JS is **out of scope** for a sample — samples are static HTML + the theme CSS (progressive enhancement only).
4. Blocks read tokens only (M4 contract): no hex, no inline styles.

Deliverable: `themes/registry.json` — canonical block → aliases → per-theme source path → licence origin.

## 4. Step 2 — the build tool

```bash
node themes/tools/build-sample.mjs --all
node themes/tools/build-sample.mjs samples/07-atlas-crm
node themes/tools/build-sample.mjs --all --check     # CI: dist is current + provenance valid
```

- Reads `sample.json` (`variation`, ordered `blocks`, `fixture`), resolves each block from that variation's `theme/components/`, injects `content.json` values, inlines the theme CSS (or links a copied `theme.css`), writes `dist/index.html`.
- **Deterministic:** identical inputs → byte-identical output; no network at build time.
- **Idempotent + checked:** `--check` fails if `dist/` differs (same discipline as the repo's other generators).
- No framework, no JS dependency required to view a sample.

## 5. The 20 samples

Ten archetypes across the four variations (5 × 4), so each variation is proven
on more than one content shape:

| # | Sample | Variation | Archetype | Block manifest (canonical) |
|---|---|---|---|---|
| 01 | Northwind SaaS | `fu-paper-ink` | SaaS product | nav · hero · logo-cloud · feature-grid · pricing · faq · cta-band · footer |
| 02 | Atlas CRM | `loop-crm` | CRM / RevOps | nav · hero-dashboard · integration-grid · comparison · pricing · testimonial · footer |
| 03 | Meridian Academy | `precis-atelier` | Course / LMS | nav · hero · course-grid · curriculum-steps · instructor-bio · pricing · faq · footer |
| 04 | Helix Research | `fu-paper-ink` | Research center | nav · hero · program-list · publication-list · team-grid · contact · footer |
| 05 | Service Desk POS | `loop-crm` | POS / vertical | nav · hero-device · vertical-grid · feature-table · pricing · testimonial · cta-band · footer |
| 06 | Quiet Launch | `fu-paper-ink` | Waitlist / pre-launch | nav · hero-minimal · value-steps · waitlist-form · faq · footer |
| 07 | Ledger Cloud | `loop-crm` | Finance / billing | nav · hero · metrics-band · feature-grid · pricing-toggle · security-band · footer |
| 08 | Studio Nine | `fu-paper-ink` | Agency / portfolio | nav · hero-editorial · work-grid · process-steps · testimonial · contact · footer |
| 09 | Brightpath Learn | `precis-atelier` | Cohort program | nav · hero · cohort-timeline · outcome-stats · pricing · faq · cta-band · footer |
| 10 | Cartographer | `fu-paper-ink` | Dev tool / docs | nav · hero-terminal · code-feature · api-table · changelog-feed · pricing · footer |
| 11 | Lantern CRM | `loop-crm` | Sales pipeline | nav · hero · pipeline-preview · feature-grid · testimonial · pricing · footer |
| 12 | Fieldnotes | `fu-paper-ink` | Editorial / blog | nav · hero-editorial · featured-post · post-grid · newsletter · footer |
| 13 | Verity Clinic | `fu-paper-ink` | Medical / clinic | nav · hero · service-grid · practitioner-grid · booking-form · faq · footer |
| 14 | Kiosk Ops | `loop-crm` | Multi-terminal ops | nav · hero · terminal-diagram · feature-table · uptime-band · pricing · footer |
| 15 | Northline Support | `precis-atelier` | Training + support | nav · hero · course-grid · support-tiers · pricing · faq · footer |
| 16 | Orbit Analytics | `loop-crm` | Data / dashboards | nav · hero-dashboard · metrics-band · integration-grid · pricing · security-band · footer |
| 17 | Commons Campus | `precis-atelier` | University dept. | nav · hero · department-stats · course-grid · faculty-grid · news-list · footer |
| 18 | Ember Commerce | `fu-paper-ink` | Commerce / retail | nav · hero-device · product-grid · value-steps · reviews · pricing · footer |
| 19 | Signal Launch | `loop-crm` | Product launch | nav · hero-announce · launch-timeline · feature-grid · metrics-band · waitlist-form · footer |
| 20 | Paper Atelier | `fu-paper-ink` | Design-system showcase | nav · hero-editorial · token-showcase · component-gallery · typography-scale · footer |

**Coverage rule:** every canonical block appears in ≥ 2 samples; every variation
appears in ≥ 4 samples; each archetype's fixture content is domain-plausible
(no placeholder text) so samples double as visual references.

## 6. Milestones (tasks)

1. **M5.1** Component inventory + merge map → `registry.json` (§ 3), including aliases and licence origin per block.
2. **M5.2** `build-sample.mjs` + `audit-provenance.mjs` + `themes/README.md`; prove on one sample end-to-end.
3. **M5.3** Samples 01–10 with fixtures; `INDEX.md` table filled from manifests (not hand-typed).
4. **M5.4** Samples 11–20; coverage check (block + variation minimums) as a script assertion.
5. **M5.5** Provenance + licence gate: refuse a block whose origin is AGPL-derived (`formint-community`) or unlicensed; record attribution in `themes/README.md`. See [M6](06-theme-guidelines-and-themeforest.md) § Licensing.
6. **M5.6** Visual QA: build all 20, screenshot each at 3 widths (desktop/tablet/mobile) into `themes/samples/<id>/preview/`, check heading order, focus visibility, and contrast against the theme tokens.
7. **M5.7** Wire `theme-samples` into the docs/Make pipeline so `--check` runs with the rest of the checks (no second CI system).

## 7. Verification

```bash
node themes/tools/build-sample.mjs --all
node themes/tools/build-sample.mjs --all --check      # dist current
node themes/tools/audit-provenance.mjs               # every block resolves + licence ok
node -e "const r=require('./themes/registry.json');/* coverage minimums */"
grep -rl 'AGPL' themes/samples/*/dist 2>/dev/null | wc -l   # 0
```

Pass criteria: 20 samples build offline and deterministically, each opens as
static HTML, coverage minimums hold, and no sample contains AGPL-derived assets.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Samples drift from product components (the classic copy-paste failure) | Samples hold **no** component markup — only manifests; `--check` fails on drift |
| 20 samples is a large surface to maintain | 10 archetypes × 4 variations with shared blocks; a new sample is a ~20-line manifest |
| Non-AGPL-compatible licensing on publishable themes | M5.5 gate + M6 licensing section; attribution recorded per block |
| Component merge loses a genuinely distinct design | Merge rule 2 keeps both, explicitly named — never an inline override |
| Fixture content looks like placeholder slop | Fixtures are domain-plausible per archetype and reviewed in M5.6 |
| Adding a root-level `themes/` confuses the nx project graph | Register it as a docs/asset library (no Nx app targets) or keep it out of `nx run-many` deliberately and document why |

## 9. Remarks & Notes

- The value of this milestone is the **merge**, not the count: twenty manifests
  over one canonical block set is maintainable; twenty copied page templates is
  not.
- Samples are static references, not deployments — nothing here is published or
  served until M6 explicitly packages a subset.
- Where a product block needs its own JS (charts, live pricing), the sample shows
  the static state and notes the enhancement in its README rather than
  re-implementing product behaviour.
