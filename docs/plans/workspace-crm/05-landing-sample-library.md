# M5 — Landing sample library (20 samples from merged components)

> **Status:** Proposed — awaiting review · **Owner:** Yahia · **Validator:** Moustafa
> **Home:** repo-root `themes/` (shared samples) · **Depends on:** [M4](04-theme-files-and-components.md)
> **Tags:** `#samples` `#landing-pages` `#components` `#merge` `#provenance`

<!-- AI-generated: review needed -->

## Goal

Twenty landing-page samples that are **compositions, not copies**: each declares a
theme variation plus an ordered block manifest, and one tool assembles it from the
merged canonical component library. Every sample builds standalone and every block
traces back to the product component it came from.

The request's "desktop themes dir `documents/themes`" maps here: the shared
**samples** library is `themes/`. Authored theme sources stay in each project's
`theme/` (M4). No `documents/` directory is created.

## Merge rules

Sources: Precis Landing (hero, pricing, FAQ, CTA, testimonial, stats) · CTC Research
(program, publication, bio, contact) · Loop-CRM landing (product hero, dashboard
preview, integration, comparison) · Formint landings (device mockups, feature table)
· Syntara (chat/terminal hero) · docs + brand (marks, diagrams).

1. Same purpose, different names → one canonical block; the old name becomes a
   registry alias so nothing silently disappears.
2. Same purpose, genuinely different design → two explicitly named blocks
   (`hero-cinematic`, `hero-terminal`) — never one block with inline overrides.
3. A block that needs product JS is out of scope; samples are static HTML + theme CSS.
4. Blocks read tokens only: no hex, no inline styles.

## The 20 samples

Ten archetypes × four variations, so each variation is proven on more than one shape.

| # | Sample | Variation | Archetype | Blocks |
|---|---|---|---|---|
| 01 | Northwind SaaS | `fu-paper-ink` | SaaS product | nav · hero · logo-cloud · feature-grid · pricing · faq · cta-band · footer |
| 02 | Atlas CRM | `loop-crm` | CRM / RevOps | nav · hero-dashboard · integration-grid · comparison · pricing · testimonial · footer |
| 03 | Meridian Academy | `precis-atelier` | Course / LMS | nav · hero · course-grid · curriculum-steps · instructor-bio · pricing · faq · footer |
| 04 | Helix Research | `fu-paper-ink` | Research center | nav · hero · program-list · publication-list · team-grid · contact · footer |
| 05 | Service Desk POS | `loop-crm` | POS / vertical | nav · hero-device · vertical-grid · feature-table · pricing · testimonial · cta-band · footer |
| 06 | Quiet Launch | `fu-paper-ink` | Waitlist | nav · hero-minimal · value-steps · waitlist-form · faq · footer |
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
| 20 | Paper Atelier | `fu-paper-ink` | Design system | nav · hero-editorial · token-showcase · component-gallery · typography-scale · footer |

**Coverage rule:** every canonical block appears in ≥ 2 samples; every variation
appears in ≥ 4. Fixtures are domain-plausible per archetype — no placeholder text —
so samples double as visual references.

## Tasks

| # | Task | Done when | Effectful |
|---|---|---|---|
| M5.1 | Component inventory + merge map | `themes/registry.json` resolves canonical block → aliases → source path → licence origin | no |
| M5.2 | Build + audit tools | `build-sample.mjs` and `audit-provenance.mjs` exist; one sample proves the path end to end | no |
| M5.3 | Samples 01–10 | Built; `INDEX.md` generated from manifests, not hand-typed | no |
| M5.4 | Samples 11–20 | Built; coverage minimums asserted by the tooling | no |
| M5.5 | Licence gate | A block from an AGPL-derived or unlicensed source is refused; attribution recorded | no |
| M5.6 | Visual QA | All 20 built; screenshots at desktop/tablet/mobile; heading order, focus, contrast checked per theme | no |
| M5.7 | Wire into the pipeline | `--check` runs with the repo's existing checks — no second CI system | no |

## Gates

- 20 samples build offline and deterministically; a re-run produces byte-identical
  output and `--check` fails when `dist/` is stale.
- Samples hold **no** component markup — only manifests, so they cannot drift.
- Zero samples contain AGPL-derived assets.

## Effectful — confirm first

- None. Samples are static references; nothing is deployed or served from here.

## Links

- → [`README.md`](README.md) — Program index
- → [`04-theme-files-and-components.md`](04-theme-files-and-components.md) — The component layer being composed
- → [`06-theme-guidelines-and-themeforest.md`](06-theme-guidelines-and-themeforest.md) — Packages a subset for sale
