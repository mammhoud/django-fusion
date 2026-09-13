# Loop-CRM — Merge & Architecture Plan

> **Status:** Most of the merge is shipped: realtime SSE/WebSocket, webhooks + email/Slack connectors, finance CSV export, pagination/filtering, Activities + Media screens, custom objects (runtime schema), saved views, approval/report queues, CSV import, a no-code step workflow editor, the consent-gated AI hub foundation, per-resource Bolt OpenAPI metadata, and the Loop-CRM backend translation sweep. All 12 social platforms now publish for real behind `SocialConnector` — the six formerly credential-gated catalog adapters (Instagram/Facebook/TikTok/YouTube/Reddit/WhatsApp) are real HTTP publishers, and the composer/media row now attaches image/video to posts. Remaining open work is connect-flow polish, the reviewed monorepo catalog merge, translated frontend copy, and visual DAG/editor polish. See §12 for the ordered roadmap.
> **Source projects:** [twentyhq/twenty](https://github.com/twentyhq/twenty) (CRM) · [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) (social scheduling)
> **Canonical path:** [`projects/loop-crm/`](../../../projects/loop-crm/)
> **Last reviewed:** 2026-08-15

Loop-CRM merges Twenty's CRM (custom objects, pipelines, workflows) with
Postiz's social scheduling (30+ platforms, AI post generation) into one
django-fusion modular monolith. The value proposition is **"from social
impression to closed deal — one platform, one source of truth"**: every social
interaction is attributable to a deal, workflows span the whole customer
journey, and RevOps sees marketing ROI in real time.

---

## 1. Why django-fusion (not django-cotton)

| Aspect | Benefit |
|---|---|
| Single transaction | Create a social post AND link it to a deal atomically |
| Unified auth | One login for sales reps AND social managers |
| Zero network overhead | Django ORM hits one PostgreSQL database — sub-50ms dashboards |
| Simplified DevOps | One Compose file: Django, Postgres, Redis, Dramatiq |
| Shared components | `{% comp %}` + fragments replace django-cotton's component layer |

django-fusion (`libs/django-fusion`) provides the `{% comp %}` component tag,
fragment serving, the dual render-first / data-API pipeline, and the
`FUSION_RENDER_FIRST` switch. Loop-CRM consumes those directly — it does **not**
use django-cotton.

---

## 2. Architecture

```text
User browser
  → Astro frontend (:4321)
      ├── Static pages (marketing site, docs)
      ├── SSR pages (dashboard, deals, post calendar)
      └── React islands (RevOps board, attribution, analytics)
      ├── Redux (RTK) — data-API road source of truth
      ├── Alpine.js — modal toggles, dropdowns, form validation
      └── HTMX — list pagination, form submission, inline editing
  → Django backend (:8000)
      ├── django-bolt API — /bolt/companies|deals|posts|dashboard (canonical)
      ├── Django fallback — /api/v1/* (compatibility when Bolt is absent)
      ├── Django views   — HTMX responses (/dashboard/, /deals/, /posts/)
      ├── Django ORM     — core | crm | marketing | attribution | finance | pos
      └── Django admin   — internal management
  → Dramatiq task queue (publishing, OAuth refresh, analytics, attribution)
  → PostgreSQL (unified DB) + Redis (cache/queue)
```

**Substitutions from the sources:** Dramatiq replaces both Temporal (Twenty)
and BullMQ (Postiz); django-fusion replaces django-cotton; a single Django
project replaces the NestJS/Twenty and NextJS/Postiz service split.

---

## 3. Module organization

```text
projects/loop-crm/
├── backend/
│   ├── settings.py          # SQLite (dev) / PostgreSQL (prod via USE_POSTGRES)
│   ├── urls.py              # admin + browser + /bolt/ + /api/v1/* mounts
│   ├── plugins/
│   │   └── workers/         # Dramatiq actors (publish, refresh, analytics, webhooks)
│   └── apps/
│       ├── core/            # Workspace (tenancy), User (RBAC), AuditLog, permissions
│       ├── crm/             # Company, Contact, Pipeline, PipelineStage, Deal, Activity
│       ├── marketing/       # Campaign, SocialChannel, Post, Media, PostAnalytics
│       ├── attribution/     # AttributionModel, AttributionTouchpoint + engines/
│       ├── finance/         # Invoice, Payment, RevenueEvent + HTMX screens
│       └── pos/             # PosSale, PosSaleItem, PosPayment (Formint ingest ledger)
├── frontend/                # Astro 5 + Tailwind 4 + HTMX + Alpine + Redux + GSAP
├── docker-compose.yml       # Django + Postgres + Redis + Dramatiq worker + scheduler
└── Makefile                 # dev | build | check | backend-*
```

---

## 4. Unified data model

- **core** — `Workspace` (multi-tenant root), `User` (AbstractUser + 7 RBAC
  roles), `AuditLog` (append-only trail).
- **crm** — `Company`, `Contact`, `Pipeline`, `PipelineStage` (probability,
  color, order), `Deal` (with `campaign` FK → marketing), `Activity`.
- **marketing** — `SocialChannel` (12 platforms + WhatsApp), `Campaign`,
  `Media`, `Post` (draft/pending approval/approved/scheduled/publishing/published/failed),
  `PostAnalytics` (impressions/clicks/engagement/spend).
- **attribution** — `AttributionModel` (first/last/linear/time-decay/
  position-based) and `AttributionTouchpoint` (fractional weight 0..1 per deal).
- **finance** — `Invoice`, `Payment`, and `RevenueEvent` are workspace-scoped
  records linked to CRM companies/deals and marketing campaigns. A closed-won
  workflow can idempotently create the invoice and recognized revenue event;
  payments update invoice status without allowing overpayment.

The attribution glue is `crm.Deal.campaign` — a closed deal rolls revenue back
to the campaign (and posts) that influenced it. Companies, contacts, and deals
also expose tenant-scoped `custom_attributes`; the custom-object catalog makes
those Twenty-style fields discoverable without hard-coding workspace schemas.

---

## 5. RBAC matrix (summary)

| Role | Sales | Marketing | Attribution |
|---|---|---|---|
| Super Admin | full | full | full |
| Sales Manager | manage | view | view |
| Sales Rep | own deals | — | — |
| Marketing Manager | view | manage | view |
| Marketing Specialist | — | own posts | — |
| RevOps Manager | manage | manage | manage |
| Viewer | view | view | view |

Helpers live in `apps/core/permissions.py`; django-bolt's JWT/API-key
backends and `IsAuthenticated` guards protect the canonical API road. The
Django compatibility road (`/api/v1/`) is session-authenticated
(`@login_required`) and workspace-scoped; anonymous callers are redirected to
`/accounts/login/` instead of receiving unscoped (cross-tenant) rows or counts.

---

## 6. Roadmap (remaining work)

- **Phase 4 — AI hub:** local foundation shipped — consent-gated lead scoring,
  sales-email drafting, and social-post drafting are exposed through provider-
  neutral adapters with audit-safe status records. External provider activation
  remains credential-gated; no operation auto-publishes or auto-sends.
- **Phase 6 — API surface:** per-resource Bolt OpenAPI metadata is shipped —
  every registered resource carries a human-readable tag, singular label,
  description, CRUD route summaries, pagination/filter descriptions, and
  secret-safe projections. The optional Bolt runtime still skips runtime schema
  assertions when django-bolt is not installed.
- **Phase 7 — locale foundation:** Loop-CRM now points at the shared
  `projects/assets/locale/` catalog root and exposes a CSRF-protected `en/ar`
  locale preference contract in the app shell; catalog merge and translated
  frontend copy remain open.
- **Phase 5 — domain screens:** shipped — the approval queue
  (`/marketing/approvals/`), real revenue reports (`/attribution/reports/`),
  custom objects (`/settings/custom-objects/`), saved views
  (`/settings/saved-views/`), and CSV import (`/settings/import/`) now replace
  the navigation-ready module surfaces.

### Navigation contract

Every active web road consumes the same hierarchy: **module → subpage →
current breadcrumb**. Django uses `apps/core/navigation.py` plus a top-level
`LoopCrmSite` containing the `LoopCrmApplication`; django-fusion owns the root
URL composition and `menu_path` metadata. Astro keeps a typed compile-time
route contract, but its initial navigator is loaded from the backend HTMX
fragment, cached in session storage, and refreshed after page navigation by
changing only active classes/ARIA state. The JSON `/api/v1/navigation/`
contract carries the same tree with private cache headers for data-road clients.

### Integration boundary

The repository can validate route shape, capabilities, workflow definitions,
queue state transitions, and attribution contracts locally. It cannot complete
external OAuth handshakes or publish to third-party networks without workspace
credentials, redirect URLs, encryption policy, and provider approval. Those
adapters must be added behind `SocialConnector`, never in templates or views.

---

## 7. Verification

```bash
cd projects/loop-crm/backend
make check        # Django system checks
make migrate      # makemigrations + migrate (SQLite by default)
make test         # Django tests

cd ../frontend
npm run check     # astro check
npm run build     # Astro build
```

For the optional API runtime, install `django-fusion[bolt]`, set
`FUSION_BOLT_JWT_SECRET`, and validate `/bolt/health`, `/bolt/auth/token`, and
one protected resource with either a bearer token or `X-API-Key`. No provider
credentials are needed for these local contract checks.

Reference clones (for the connector/API phases, kept outside the tree):
`twentyhq/twenty` and `gitroomhq/postiz-app`.

### Browser verification

The scoped Playwright suite covers complete navigation state across CRM
subpages, workflow creation → activation → queued run, and content draft →
approval → scheduled transitions. The deterministic `seed_playwright` command
creates only the records needed by those browser flows; it never fabricates
production data.

---

## 8. Data tables and extensible fields plan

### Package analysis

| Capability | Existing package/convention | Decision |
|---|---|---|
| Server-rendered tables | `django-tables2` is already a workspace dependency and django-fusion exposes `TableView`/table mixins | Use `django-tables2` for interactive members/roles and future domain tables; keep querysets tenant-scoped and allowlisted. Do not add a second table library. |
| Authentication pages | `django-allauth` is already a workspace dependency and is used by Precis Landing | Add allauth account URLs, middleware, branded Loop-CRM templates, and the existing `auth.User` + `UserProfile` role boundary. Keep social providers opt-in. |
| Dynamic fields | Existing `custom_attributes` JSON is provider-neutral and already used by Company, Contact, and Deal | Add persisted `CustomFieldDefinition` metadata with field type, validation, choices, and object key. Validate values at the service/form boundary, then store values in the existing JSON column. |
| Polymorphic records | No polymorphism package is installed for this product | Do not introduce `django-polymorphic` or model inheritance for custom fields. A definition catalog plus JSON values avoids multi-table joins, preserves tenant isolation, and maps cleanly to Bolt/OpenAPI. Use `ContentType` only for a future audited cross-model relation, never for unvalidated field keys. |
| API identity | django-fusion Bolt helpers already issue/verify JWTs and API keys | Add user-bound verification that resolves `sub` to an active Django user and checks role/workspace claims. Token routes must never mint an identity from an unauthenticated arbitrary subject. |

### Delivery slices

1. **Tables** — ship the members/roles table first using `django-tables2`, with explicit columns, search, role filtering, and no secret/token fields. Reuse the table contract for companies, deals, posts, and audit rows as those screens become real.
2. **Fields** — persist field definitions per workspace/object type; support text, number, boolean, date, URL, email, select, and multi-select with JSON-safe validation. Keep field definitions versionable and archive rather than hard-delete fields.

## 9. Source parity gap audit — partial & missing

Loop-CRM is a **feature merge**, not a port. Shipped parity and the net-new
merge layer are omitted here; the tables below record only what remains partial
or deferred against each source.

### Twenty (CRM) — partial & missing

| Twenty capability | Loop-CRM status | Notes |
|---|---|---|
| Custom **fields** | ⚠️ partial | `CustomFieldDefinition` (9 types) validated into the JSON column |
| Custom **objects** (arbitrary) | ✅ added | `CustomObjectDefinition` + `CustomObjectRecord` (validated JSON rows, no migrations per object) |
| Saved views (list/kanban per user) | ✅ added | member- + workspace-scoped `SavedView`; `?view=` applies safe sort/filter |
| No-code workflow editor | ⚠️ partial | step editor (trigger + ordered actions) shipped; visual DAG (canvas) editor remains |
| Email sync (Gmail/Outlook) | ✅ added | OAuth connect (authorize + callback) + incremental sync matched to contacts/deals |
| Notes/tasks/favorites as first-class | ⚠️ partial | folded into `Activity` types only |
| GraphQL / webhooks / CSV import | ⚠️ partial | webhooks + CSV import shipped; GraphQL not added (REST only) |
| AI agents | ❌ not added | Phase 4 |

### Postiz (social scheduling) — partial & missing

| Postiz capability | Loop-CRM status | Notes |
|---|---|---|
| Real publish adapters | ✅ 12 of 12 | LinkedIn, X, Mastodon, Bluesky, Discord, Slack (webhooks), Facebook (Page feed/photo/video), Instagram (container + publish), TikTok (direct-post init/upload/status), YouTube (`videos.insert` multipart upload), Reddit (`api/submit`), WhatsApp (Cloud API messages) |
| Media attachments | ✅ added | composer + Media row attach image/video to a post; URL-pull providers gate on `PUBLIC_SITE_URL`, byte uploads read through Django storage |
| Analytics | ⚠️ partial | X metrics real; others return `{}` honestly |
| OAuth connect | ⚠️ 2 flows + tokens | LinkedIn + X redirect OAuth; the six promoted connectors use per-channel tokens (manual entry); Mastodon/Bluesky app-password pending |
| 30+ channels | ❌ not added | 12 cataloged, all with real publish implementations |
| AI generation / copilot | ❌ not added | Phase 4 |
| Canva editor / RSS / marketplace | ❌ not added | |

---

## 10. Page-by-page interaction inventory

| Route | Screen | Interactions |
|---|---|---|
| `/overview/` | RevOps dashboard island | fetch dashboard/board/trend in parallel, KPI cards, funnel→board deep-links, revenue-trend bars with tooltips, skeleton/error/empty states |
| `/crm/companies/` | Companies | real list + HTMX create form, error/empty states, tactile rows |
| `/crm/contacts/` | Contacts | list + create form, cross-workspace relationship rejection |
| `/crm/pipelines/` | Pipelines | resource table (real data) |
| `/crm/deals/` | Deals board island | GSAP drag, keyboard chevrons, optimistic move + rollback, CSRF echo, pipeline tabs, stage focus chip, deep-link scroll |
| `/crm/activities/` | Activities | resource table (real, workspace-scoped) via the `activities` resource |
| `/marketing/` | Marketing landing | module cards |
| `/marketing/calendar/` | Content calendar | composer + lifecycle transitions (submit/approve/schedule/publish/retry), channel status chips |
| `/marketing/channels/` | Channels | connect (OAuth), disconnect, refresh, capability/status display |
| `/marketing/campaigns/` | Campaigns | resource table |
| `/marketing/media/` | Media library | real list table (workspace-scoped; upload stays a file/multipart concern) |
| `/marketing/approvals/` | Approvals | pending-approval queue with approve/reject HTMX transitions |
| `/finance/` + `/invoices/` + `/payments/` + `/revenue/` | Finance | ModelForms, HTMX reset/list fragments, revenue trend |
| `/attribution/`, `/touchpoints/`, `/reports/` | Attribution | touchpoints table; real revenue report (campaign revenue + pipeline value) |
| `/tasks/` | Task center | shared+local job history |
| `/settings/members/` | Members | django-tables2 + role matrix |
| `/settings/workflows/` | Workflows | create/toggle/queue-run fragments |
| `/settings/integrations/` | Integrations | platform catalog table |
| `/settings/email/` | Email inbox | connect (Gmail/Outlook OAuth), list connected mailboxes + synced messages with contact/deal deep-links |
| `/settings/custom-fields/` | Custom fields | field catalog table |
| `/settings/custom-objects/` (+ `/records/`) | Custom objects | runtime object schema + validated JSON rows, columns derived from the definition |
| `/settings/saved-views/` | Saved views | member's list/kanban view configs |
| `/settings/import/` | Import | CSV upload → companies/contacts/deals (tenant-scoped, per-row errors) |
| `/settings/audit/` | Audit log | append-only trail table |
| `/account/*` | allauth | login/signup/logout, password reset/change, email, social connections, profile |

---

## 11. Enhancement & optimization guide

### Performance
- Keep every animation on `transform`/`opacity` (never `top`/`left`/`width`/`height`);
  the board uses GSAP `x,y` and the dash uses CSS `transform` only.
- Use `will-change` sparingly; add it only to the drag cards and the trend bars.
- Scope `backdrop-filter` to the sidebar/topbar; never on scrolling containers.
- `async for` + `acount()` on the Bolt road; `limit`/`offset` + `values(*fields)`
  on the compatibility road; keep `select_related` on the render-first row helpers.
- The dual road already shares `apps/core/resources.py` — do not fork it.

### Motion & accessibility
- Honor `prefers-reduced-motion` everywhere (the shell disables transition and
  animation; the board skips GSAP drag and uses keyboard chevrons).
- Use staggered reveal (`animation-delay` cascade) for lists; never mount grids
  instantly.
- Use `min-h-[100dvh]`, never `h-screen`; grid (`grid-cols-…`) not flex-math.
- One accent, desaturated; no pure black, no neon glows, no emoji/symbols
  (SVG icons instead), tactile `:active` on every interactive surface.

### Data & API
- Add a resource by extending `RESOURCES` in `apps/core/resources.py` — both
  roads and the generic table screen pick it up automatically.
- Keep FK validation in `_resolve_relation`; never accept an unscoped FK.
- New writes must set `workspace_id` from `current_workspace_id` and reject a
  null workspace rather than defaulting to unscoped.
- Collection GETs honor `limit` (1–200, default 100), `offset`, and `search`
  (case-insensitive across the resource's text fields, tenant-scoped); the
  response `count` is the filtered total and `next`/`previous` are offsets.

### Testing
- `apps/core/test_tenancy.py` owns cross-tenant isolation; add a read + a
  mutation assertion for every new screen.
- Frontend contract tests read source for behavior; add one per island/screen.

---

## 12. Feature-merge roadmap — clone → complete multi-functional CRM

Ordered by impact; each phase is independently shippable.

1. **Real publish implementations for all 12 catalog adapters** — ✅ shipped:
   Instagram/Facebook/TikTok/YouTube/Reddit/WhatsApp are real HTTP publishers
   behind the `SocialConnector` contract (Meta Graph feed/photo/video +
   container flow, TikTok direct-post init/upload/status, YouTube
   `videos.insert` multipart upload, Reddit `api/submit`, WhatsApp Cloud API),
   the composer attaches media (`Post.media`), and URL-pull providers gate on
   `PUBLIC_SITE_URL`. Discord and Slack remain real incoming-webhook
   publishers. Remaining polish: per-provider connect flows beyond manual
   token entry.
2. **AI hub (Phase 4)** — post generation, sales-email drafting, lead scoring
   behind provider adapters with workspace consent + `AuditLog` writes; reuse
   the `workflow_actions` deferred-action pattern.
3. **Twenty-style extensibility** — ✅ saved views per user, ✅ arbitrary custom
   objects (`CustomObjectDefinition` + generic JSON record table, not
   polymorphic models), ✅ a no-code **step** workflow editor, and ✅ a visual
   **DAG (canvas)** editor: trigger-rooted node/edge graph with drag, port-to-
   port branching/merging, cycle + orphan rejection, and a topological
   ``actions`` order persisted alongside the ``graph`` JSON column.
4. **Domain screens (Phase 5)** — ✅ paginated HTMX screens for the
   approval queue (`/marketing/approvals/`) and real revenue reports
   (`/attribution/reports/`). Activities + media are also real
   workspace-scoped tables; resource-table pagination/filtering is shipped.
5. **Realtime + integrations** — ✅ WebSocket pipeline/board sync, ✅ webhooks
   for deal-won/post-published, ✅ CSV import, ✅ CSV/JSON export of arbitrary
   resource tables (``GET /api/v1/export/?resource=<slug>&format=csv|json``,
   workspace-scoped), and ✅ email sync (Gmail/Outlook): ``EmailAccount`` +
   ``EmailMessage`` models, stdlib-HTTP Gmail/Outlook adapters with honest
   unconfigured degradation + token refresh, an idempotent contact/deal-
   matching ``sync_account`` service, a Dramatiq actor + ``sync_email``
   command, ``/api/v1/email/`` routes that never project OAuth tokens, and a
   Gmail/Outlook OAuth connect flow (``/connect/email/<provider>/`` authorize
   + callback) that upserts the ``EmailAccount`` with server-side tokens —
   mirroring the social channel flows. ``email_accounts``/``email_messages``
   are also registered Bolt CRUD resources with per-resource OpenAPI tags
   (``label``/``singular``/``description``); OAuth tokens and the sync cursor
   are excluded from both the read and write projections.
6. **Data/API surface** — ✅ per-resource OpenAPI docs on the Bolt road: each
   registered resource carries a ``label``/``singular``/``description`` in the
   ``RESOURCES`` registry, every CRUD route is tagged + summarized under that
   resource (``List/Create/Retrieve/Update/Delete``), and the top-level config
   declares the per-resource tags. Pagination/filtering shipped: both roads
   accept ``limit``/``offset``/``search`` on collection GETs, ``count`` is the
   filtered total, and ``next``/``previous`` are offsets.

> **Finance + workflows + integrations** shipped (2026-08-14/15): Formint POS
> financial-data ingestion into the finance module, workflow action/template
> expansion, and webhooks/email/Slack/social/export connectors. Recorded as a
> finished milestone in [`docs/agenda/feature-tracking/loop-crm.md`](../../agenda/feature-tracking/loop-crm.md)
> § Loop-CRM; the separate plan file was deleted (git history is the archive).

---

## 13. Build guide — adding an animated interactive screen

1. **Choose the road** — render-first (Django template + HTMX, like the
   calendar/channels) or data (Astro shell + a React island, like the board).
   Islands mount their own `<StoreProvider>`; never nest Astro `<slot/>` inside
   React.
2. **State cycle** — always ship loading (skeleton, not spinner), empty
   ("how to populate"), error (inline + retry), and success states.
3. **Data** — the island fetches `/api/v1/…` with same-origin cookies (echo the
   `csrftoken` cookie as `X-CSRFToken` for mutations); the render-first screen
   uses `apps/core/resources.py` + a `LoopPageView` subclass + a partial.
4. **Schemas** — register the resource in `RESOURCES` so `/bolt/` + `/api/v1/`
   and the generic table inherit the contract; add a msgspec schema on the Bolt
   road for typed bodies.
5. **Motion** — GSAP for drag/scrolltelling (isolated in `useEffect` with
   cleanup); CSS for reveal/breathe/tactile. `transform`/`opacity` only;
   `prefers-reduced-motion` fallback; no framer-motion + GSAP in the same tree.
6. **Integrations** — provider I/O stays behind `SocialConnector` in a Dramatiq
   actor; templates/views never call a provider directly.

## Related

- [`../../../projects/loop-crm/README.md`](../../../projects/loop-crm/README.md)
- [`../README.md`](../README.md)
- [`../../../libs/django-fusion/README.md`](../../../libs/django-fusion/README.md)
