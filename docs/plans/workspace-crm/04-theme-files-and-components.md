# M4 — Theme files & HTML components

> **Status:** Proposed — awaiting review · **Owner:** Yahia · **Validator:** Mahmoud
> **Contract:** [`THEME_DIRECTORY_STRATEGY.md`](../THEME_DIRECTORY_STRATEGY.md) (this plan implements it)
> **Tags:** `#themes` `#design-tokens` `#variations` `#components` `#bem`

<!-- AI-generated: review needed -->

## Goal

Every styled surface gets a real `theme/` directory — tokens → light/dark
palettes → components — each stamped with its **variation id**, plus a portable
**HTML component layer** that the samples (M5) and the published themes (M6) are
assembled from.

## Decisions

- **Per-project `theme/`.** Authored theme sources live in each project, not in a
  shared dir. The samples library (M5) is a consumer, never a second source of truth.
- **Four surfaces, three variation ids.** Loop-CRM, CTC Research, Precis LMS get
  their own; structa.cloud reuses one unless M4.1 decides otherwise.
- **No orphaned theme files.** A theme is only publishable if its sections are
  standalone HTML; every component reads tokens and nothing else.
- **`formints` uses the merge target** (`formint-community/client/…`), not the old
  `formint-client/` path — see [`editions/11`](../editions/11-community-client-ui-mode.md).

| Surface | Variation id | Today |
|---|---|---|
| Precis LMS (`precis-main`) | `precis-atelier` | shape started; needs tokens + index + banner |
| CTC Research | `fu-paper-ink` (shared) | needs a real `theme/`; tokens centralised |
| Loop-CRM | `loop-crm` | single `globals.css`; needs split + banner |
| structa.cloud | reuse, or its own — **decide in M4.1** | directory exists, **empty** |

## Tasks

| # | Task | Done when | Effectful |
|---|---|---|---|
| M4.1 | Confirm the two open homes (**do first**) | structa.cloud theme home answered and recorded; CTC generated dirs recorded as generated/collected output | no |
| M4.2 | Precis LMS theme | `theme/_tokens.scss` + `_index.scss`; banner on every theme file; `$theme-variation` declared; runtime `data-theme`/`data-mode` in the shell | no |
| M4.3 | CTC Research theme | Values migrated out of the legacy token pair into `theme/`; it **must not** redeclare `fu-*` values differently | no |
| M4.4 | Loop-CRM theme | `globals.css` organised as tokens → palettes → components; banner + `--theme-variation`; **no hex outside `theme/`** | no |
| M4.5 | HTML component layer | Per variation: `theme/components/*.html` (nav, hero, features, pricing, testimonials, faq, cta, footer) + `index.html` visual index + `README.md` class contract | no |
| M4.6 | `make theme-check` | One target per project asserting: banner matches the variation id, zero hex outside `theme/`, runtime selector present; wired into each existing `make check` | no |

## Gates

- `grep -r '^// Variation:' <project>/assets/styles/theme` returns exactly that
  project's variation id.
- No hex outside `theme/` (outside `styles/` for the CRM frontend).
- Opening `theme/components/index.html` renders every block standalone, with no
  build step and no framework.
- Generated/collected CSS is untouched: `git status --porcelain` on it is empty.
- A consumer inherits another variation; it never redeclares its tokens.

## Effectful — confirm first

- None. This milestone edits authored sources only; it never writes into collected
  static output.

## Links

- → [`README.md`](README.md) — Program index
- → [`../THEME_DIRECTORY_STRATEGY.md`](../THEME_DIRECTORY_STRATEGY.md) — Variation inventory and contract
- → [`05-landing-sample-library.md`](05-landing-sample-library.md) — Consumes this component layer
