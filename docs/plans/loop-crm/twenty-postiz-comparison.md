# Loop-CRM: Twenty + Postiz DNA — Package Findings & Feature Comparison

**Date:** 2026-08-17 · **Branch:** `generic` @ `6b506c798`

Loop-CRM is explicitly built from two open-source products: **Twenty** (CRM
DNA) and **Postiz** (social scheduling DNA). This document answers three
questions for the demo-state work:

1. Which npm packages exist for Twenty and Postiz, and is there **one package
   that has both features**?
2. Complete feature comparison: Twenty vs Postiz vs Loop-CRM (the merged
   product).
3. What "design enhancement with packages" actually means here, given the
   findings.

---

## 1. Package findings (verified against the npm registry, 2026-08-17)

| Package | Version | Type | What it is |
|---|---|---|---|
| [`@postiz/node`](https://www.npmjs.com/package/@postiz/node) | 1.0.8 | HTTP SDK | Thin Node client for the Postiz **Public API** — schedule posts, manage integrations, upload media against a running Postiz instance. Single dependency: `node-fetch`. It is an *SDK for a self-hosted service*, not a library with UI. |
| [`twenty-sdk`](https://www.npmjs.com/package/twenty-sdk) | 2.31.0 | CLI + SDK | Toolchain to **build, develop, and publish applications that extend Twenty CRM** — GraphQL client (axios + graphql + graphql-sse), scaffolding, and a CLI (commander + esbuild). It targets Twenty's extension model, not its UI. |
| `@twenty-ui/*` (any) | — | — | **Not published.** Twenty's design system (`packages/twenty-ui` inside `twentyhq/twenty`) is internal to the monorepo. No usable npm design package. |
| Postiz UI packages | — | — | **Not published.** Postiz's frontend (Next.js + Tailwind + shadcn/ui + Radix) lives inside `gitroomhq/postiz-app`; nothing is extracted to npm. |

### Is there ONE package with both features?

**No.** Nothing on npm (or PyPI) combines CRM + social scheduling in a single
package:

- `@postiz/node` is scheduling-only (and it is a *client* for the Postiz
  server, not a feature bundle).
- `twenty-sdk` is CRM-extension-only.
- Neither ships a design/UI system as a package.
- The only place the two feature sets meet is **this repository** — Loop-CRM
  *is* the merged implementation (Django + django-fusion, Dramatiq replacing
  both Temporal and BullMQ, one workspace, one source of truth).

**Conclusion for "enhance the designs with a package":** there is no package
to install that grants both feature sets or a ready-made merged design system.
The honest enhancement path is (a) keep Loop-CRM's own design language, (b)
map each surface to the borrowed Twenty/Postiz pattern it already mirrors,
and (c) use the two official SDKs only as **contract references** for the API
road (never as runtime dependencies).

---

## 2. Feature comparison — Twenty vs Postiz vs Loop-CRM

| Capability | Twenty (CRM DNA) | Postiz (scheduling DNA) | Loop-CRM (merged) |
|---|---|---|---|
| Companies / contacts / deals | ✅ native | — | ✅ `apps/crm` |
| Pipelines + kanban board | ✅ core (board UI) | — | ✅ `PipelineBoard` (React island, CSRF-protected move) |
| Custom fields / objects | ✅ core concept | — | ✅ `CustomFieldDefinition` + custom-object catalog |
| Saved views / record tables | ✅ core | — | ✅ `SavedView` + resource tables |
| Roles & permissions | ✅ workspaces/roles | — | ✅ 7 role profiles + capability matrix |
| Multi-tenant isolation | ✅ workspaces | — | ✅ every path workspace-scoped (`tenancy.py`) |
| Content calendar | — | ✅ calendar + composer | ✅ `Post` lifecycle (draft → approval → scheduled → published) |
| Multi-channel publishing | — | ✅ 30+ platforms | ✅ provider-neutral connector catalog (LinkedIn/X OAuth, capability surface) |
| Approvals workflow | — | ✅ review queues | ✅ approval states + `/marketing/approvals/` surface |
| Media library | — | ✅ media management | ✅ media model + `/marketing/media/` |
| Post analytics | — | ✅ analytics | ✅ `PostAnalytics` + impressions/clicks/likes |
| **Attribution (touch → revenue)** | partial (deal link) | — | ✅ **unique**: `AttributionTouchpoint` + linear/first/last/time-decay/position models |
| **Finance ledger** | — | — | ✅ **unique**: invoice → payment → recognized revenue from won deals |
| **Revenue reports** | — | — | ✅ **unique**: campaign revenue + pipeline value rollups |
| Workflow automation | ✅ (custom code) | ✅ (AI pipeline) | ✅ **merged**: cross-module triggers/actions on one Dramatiq runtime |
| Background jobs | Temporal (NestJS) | Temporal (NestJS) | **replaced with Dramatiq** (both sources' Temporal dropped) |
| API | REST + GraphQL | Public REST API | ✅ Bolt (JWT, `/bolt/`) + `/api/v1` compatibility road |
| Realtime | websockets | websockets | ✅ Channels SSE + WebSocket, workspace-scoped |
| Import/export | ✅ | — | ✅ CSV import (companies/contacts/deals) + export |
| Email inbox sync | — | — | ✅ Gmail/Outlook connectors (optional) |
| Open source | AGPL-ish (custom) | AGPL | AGPL-3.0 |

**Loop-CRM's net-new value over either parent:** attribution and finance are
missing from both Twenty and Postiz; the merged product turns "impression →
closed deal" into one auditable trail.

---

## 3. Design enhancement (what to actually do)

Both parents use the **same component ecosystem Loop-CRM already ships**:
Radix primitives, shadcn/ui, lucide icons, Tailwind (Postiz's frontend is
shadcn/ui + Tailwind; Twenty is Radix-based). Loop-CRM's frontend already
depends on `radix-ui`, `shadcn`, `lucide-react`, `tailwind-merge`,
`tw-animate-css` — so the design enhancement is **pattern mapping + token
formalization**, not new packages:

| Loop-CRM surface | Borrowed DNA | Enhancement (already present or next step) |
|---|---|---|
| Side nav + app shell | Twenty (record-app chrome) | ✅ `AppShell.astro`, breadcrumbs, mobile drawer |
| Deals board | Twenty kanban | ✅ `PipelineBoard` island |
| Content calendar / approvals | Postiz | ✅ calendar + approvals states; **next:** data-backed Astro page for `/marketing/approvals/` |
| Landing DNA strip | both | ✅ `.loop-dna` band naming Twenty / Postiz heritage |
| Design tokens | both | ✅ `globals.css` (emerald accent, `Bricolage Grotesque` + `JetBrains Mono`, dark substrate); **next:** document as a `DESIGN.md` token map so future pages stay consistent |

Concrete next-step enhancements (folded into the gap-fixing plan as Task 7):

1. **Add a `DESIGN.md`** for Loop-CRM capturing the 4-6 named tokens (substrate,
   ink, muted, line, accent, accent-bright), the type scale, radius/shadow
   rules, and the borrowed-pattern map from the table above — so every new
   page (the six new Astro shells, future CRUD screens) ships consistent.
2. **Wire the six new Astro pages to the Bolt API** (tasks, approvals, email,
   custom-objects, saved-views, import) so they show live workspace data
   instead of highlight cards — this is the "feature completeness" half of the
   gap fixing, sequenced in the plan.
3. **Keep `@postiz/node` and `twenty-sdk` out of the runtime** — reference
   their API contracts (Postiz Public API shape, Twenty GraphQL schema) when
   extending Loop-CRM's own `/bolt/` road, but never import them as
   dependencies (they expect their own servers; Loop-CRM is the server).

---

## 4. Recommendation

- Do **not** adopt a package for the design — no merged package exists, and
  Loop-CRM's own visual language is already more distinctive than either
  parent's default.
- Do **formalize the merged feature story** in the marketing surface: the
  landing already names Twenty + Postiz DNA; extend it to call out the two
  net-new capabilities (attribution, finance) that neither parent has.
- Do **finish the feature wiring** (Task 7 in the gap-fixing plan) so the
  merged feature set is actually reachable from the side nav after demo login.
