# M6 — Theme guidelines & ThemeForest publishing

> **Status:** Proposed — awaiting review · **Owner:** Mahmoud · **Validator:** Moustafa
> **Precedent:** [`projects/formints/PUBLISH.md`](../../../projects/formints/PUBLISH.md)
> **Depends on:** [M5](05-landing-sample-library.md)
> **Tags:** `#guidelines` `#themeforest` `#licensing` `#packaging` `#publish`

<!-- AI-generated: review needed -->

## Goal

A **theme guidelines** document that makes theme authoring mechanical, and a
**ThemeForest publish pack** that turns selected samples into submittable items —
with licensing resolved *before* packaging.

## Blockers (resolve before any submission)

| # | Blocker | Resolution |
|---|---|---|
| 1 | No repository `LICENSE` file (only `formints/` AGPL-3.0 and `django-fusion/`) | Operator decision — record what covers authored themes |
| 2 | AGPL-derived blocks are not sellable — AGPL copyleft is incompatible with the marketplace licence | Exclude them from the publish set (the M5.5 gate) |
| 3 | Real client/product names must not appear in samples | Fictional-name rule + a grep gate; verify each fixture |
| 4 | Fonts, icons, images, diagrams each carry their own licence | Per-asset audit in the pack (`LICENSES.md`) |
| 5 | No live demo target, which the marketplace requires | Operator-owned static host per item |

## Decisions

- **1 item = 1 variation = its samples as pages.** That is how buyers shop, and the
  manifest library stays the source of truth.
- **Sold themes are generated, never hand-edited.** `package-item.mjs` assembles
  from the M5 manifests; `--check` fails when a package is stale.
- **Three items is the minimum.** A mixed-variation bundle only if it is genuinely
  cohesive — assembled-looking bundles are a common rejection reason.
- **Structural inspiration only.** Samples are re-authored against our own tokens and
  components; no template source is copied, and provenance is recorded per block.

| Item | Variation | Pages | Category |
|---|---|---|---|
| `paper-ink-saas` | `fu-paper-ink` | 01, 04, 06, 08, 10, 12, 13, 18, 20 (9) | Business / Corporate |
| `loop-crm-ops` | `loop-crm` | 02, 05, 07, 11, 14, 16, 19 (7) | Business / SaaS |
| `atelier-learning` | `precis-atelier` | 03, 09, 15, 17 (4) | Education |
| `structa-multi-niche` (optional) | mixed | a curated 8-page subset | Multipurpose |

## Guidelines the pack enforces

Variation banner in every theme file · tokens named `--{variation}-{role}-{state}`
with no hex outside `theme/` · light + dark always present · palettes never
redeclared by a consumer · BEM block prefix per variation · HTML components are
canonical, framework wrappers consume the same classes · no placeholder text, one
`h1`, labels on controls, visible focus, contrast ≥ 4.5:1 body · licensed assets
listed, no external CDN at runtime · fictional kebab-cased names only.

## Tasks

| # | Task | Done when | Effectful |
|---|---|---|---|
| M6.1 | Resolve blockers | Licence decision, demo host, and asset audit recorded — nothing is packaged before this | operator |
| M6.2 | `themes/GUIDELINES.md` | Published and linked from the design-system docs; runs the M4.6 checks as its executable form | no |
| M6.3 | Packaging tool + templates | `package-item.mjs` plus `submit.md`/`LICENSES.md`/`CHANGELOG.md` templates; proven on one item | no |
| M6.4 | Reference item | `paper-ink-saas` packaged end to end with previews and buyer docs | no |
| M6.5 | Remaining items | `loop-crm-ops` and `atelier-learning` packaged from the same manifests | no |
| M6.6 | Quality gate | Console errors, three widths, heading order, contrast, no external requests, docs complete, licences complete, `--check` clean | no |
| M6.7 | Submission notes | Metadata, demo URL, support policy, rejection-recovery list, and how a repo theme change becomes a marketplace update | no |

## Gates

- Three items package reproducibly with complete docs, previews, licences, and metadata.
- No AGPL-derived asset anywhere in a publish set.
- The demo renders from the zip's contents alone.
- Previews show the **actual** HTML output, not a design mockup.

## Effectful — confirm first

- Publishing is an external, money-affecting action. This milestone produces the
  pack and the notes; uploading, pricing, and submission stay operator actions
  requiring explicit confirmation.

## Links

- → [`README.md`](README.md) — Program index
- → [`05-landing-sample-library.md`](05-landing-sample-library.md) — The manifests being packaged
- → [`../../../projects/formints/PUBLISH.md`](../../../projects/formints/PUBLISH.md) — Marketplace kit precedent
