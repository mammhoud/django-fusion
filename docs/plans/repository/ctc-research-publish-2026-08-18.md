# CTC Research — Publish Plan & Analyzed Todo List

> **Status:** Active — execution checklist for publishing `ctc-research.com`
> **Date:** 2026-08-18
> **Canonical path:** `projects/precis/precis-ctc/`
> **Tags:** #precis-ctc #publish #i18n #media #proxy #redeploy #content
> **Related:** ceptor-ai removal (✅ complete — recorded as a finished milestone in [`docs/agenda/feature-tracking.md`](../../agenda/feature-tracking.md) § CTC Research; the plan file was deleted, git history is the archive), [`../README.md`](../README.md)

This plan consolidates every task raised across the 2026-08-18 session for the
CTC Research site (full content/component audit, translations, media/bundles
serving, email parity, redeploy tooling, environment docs, Nx, and
cross-module automation). It is the single analyzed todo list to reference
when working toward a ctc-research publish.

---

## 0. Session context (what was asked, consolidated)

| # | Request | Where it lands |
|---|---------|----------------|
| 1 | Full check of `ctc-research.com` — preview contents & components, write docs, identify enhancements | §1 audit, §2 docs |
| 2 | Enrich contents for a medical research website; no code blocks in HTML components → media gallery / medical-enriched content | §3 |
| 3 | Check the backend dumped data at archive (`dump-data.json`, `medical_research_catalog.json`, `events.json`, …) | §4 |
| 4 | Complete translations + data loaded with full translated contents (es/sv/pt-br catalogs are stubs) | §5 |
| 5 | Email configuration parity with `ctc-research.bak` / archives; add the Precis Gmail credentials; test email to `mahmoud.ezzat.moustafa@gmail.com` | §6 |
| 6 | Shared media + bundles dirs under `projects/assets/` (project-named), webpack bundle rendering, proxy/nginx serving for filegator + site servers, collected statics, better naming | §7 |
| 7 | `make redeploy` at precis-ctc (front + back + attached containers) with delegation to the right precis command; document the full environment with requirements remarks; consider Nx monorepo | §8 |
| 8 | Cross-module automation — 16 ready workflow definitions, Dramatiq as the single execution boundary (publishing, refresh, analytics, attribution) | §9 |
| 9 | Commit, push, merge, pull (`pull → merge → push`) | §10 |

---

## 1. Content & component audit (done — baseline recorded)

The audit is complete. The site surface is:

- **Frontend (Astro 5, static):** 16 public pages + `blog/[slug]`, `courses/index`,
  `courses/[slug]`, `products/[slug]`; 13 block components (Hero, Stats,
  OutcomeFramework, CTA, Features, Pricing, FAQ, Testimonials, Timeline,
  TeamSection, BlogPreview, NewsletterSubscribe, ContactForm); 23 UI
  components; `Layout.astro` shell with HTMX/Alpine/Redux bridge; `lib/api.ts`
  API client against `/apis/*` + `/api/*` backend roads.
- **Backend (Django 5.2 + Wagtail 7.4):** `apps/pages/pages/landing_api.py`
  serves the Astro contract; `apps/learning` owns the catalog/LMS; fixtures
  seed pages (6 locales) + courses + events + tags + specializations.
- **Frontend check:** `npm run check` → 0 errors, 0 warnings, 0 hints after fixing Alpine interpolation, endpoint injection, and the `__FUSION_AUTH` window type.

**Enhancement candidates identified (some now executed):**
- Unify the two dump copies (`backend/assets/fixtures/dump-data.json` vs
  `assets/fixtures/dump-data.json` — same object count, different hashes).
- Enrich the LMS fixture with medical rich-text descriptions, modules, and lessons; review course-copy translations separately from UI catalogs.
- Complete human review of generated locale fallbacks.
- Add the proposed 16-workflow Dramatiq actors.

---

## 2. Documentation (complete)

The CTC-specific documentation set is now written and linked from the plans
registry and docs sidebar:

- `projects/precis/docs/precis-ctc/CONTENTS.md` — page-by-page content map,
  data sources, fallbacks, and medical-content rules.
- `projects/precis/docs/precis-ctc/ENHANCEMENTS.md` — completed changes,
  publish blockers, and P1/P2 improvements.
- `projects/precis/docs/precis-ctc/ENVIRONMENT.md` — requirements, environment
  names, shared assets, redeploy, and rollback notes.
- `docs/precis-ctc/README.md` — repository entry point for architecture,
  content, media/proxy, and deployment guides.
- `docs/plans/repository/precis-ctc-workflows.md` — the 16-workflow Dramatiq
  execution plan.

---

## 3. No-code-blocks → media gallery (frontend)

Replace code blocks in HTML components with a media gallery / medical-enriched
content. Confirmed scope (from search):

| Location | Current | Target |
|----------|---------|--------|
| `frontend/src/components/blocks/Hero.astro` | Signature "View Source" toggle panel (`<pre><code>`, `sourceMarkup`, `source-panel`) | Media gallery panel fed from seeded `gallery` media (13 original images in `assets/media/original_images/`) — user selected **media gallery panel** |
| `frontend/src/pages/products/[slug].astro` | "Models & snippets" section (`<pre><code>`) | Media/reference gallery or medical content cards |
| `frontend/src/components/ui/CodeBlock.astro` | Unused standalone code-block component | Remove or repurpose |
| `RenderModeSwitch.astro` / `LiveFragment.astro` / `LiveFragmentTarget.astro` | Inline `<code>` in fallback notes | Plain styled text (keep semantics, drop `<code>`) |
| `assets/templates/examples/*`, error/admin templates | `<pre><code>` | Leave (developer/admin surfaces) unless user requests removal |

**Implemented:** added reusable `MediaGallery.astro` (grid + lightbox + captions), wired it into `Hero.astro` as the right-hand panel, and replaced the products snippets section. Public code panels and the unused `CodeBlock.astro` were removed; developer/admin/example templates remain out of scope.

---

## 4. Backend dumped data audit (done — baseline)

- `backend/assets/fixtures/dump-data.json` — 178 objects: 43 pages (root +
  home/about/contact/team/events/services/all-courses × 6 locales), 6 locales
  (en, fr, de, es, ar, pt-br), 1 site, 10 page-subscriptions, 22 images, 54
  renditions. StreamFields are in current ListBlock format (methods,
  team_members, skills, contact fields, gallery media_items). Loaded by
  `manage.py load_data` (prerequisite contenttypes, admin user, Collections,
  optional `--replace`, sequence reset, LMS app fixtures, default Site).
- `apps/learning/fixtures/medical_research_catalog.json` — 19 objects: 6
  medical courses, 8 tags, and 5 specializations.
- `apps/learning/fixtures/medical_research_curriculum.json` — 36 objects:
  12 modules and 24 rich-text lessons attached to the six medical courses;
  the fixture contains no `code` stream items.
- `events.json`, `courses.json`, `specializations.json`, `course_tags.json` —
  supporting LMS fixtures (loaded via `load_course_fixtures`, which now also
  loads the medical curriculum).
- Two dump copies exist (`backend/assets/fixtures` + `assets/fixtures`) with
  different hashes — reconcile to one canonical file.

---

## 5. Translations — complete es/sv/pt-br catalogs

**State:** the French reference contains 3,438 non-header entries and the
reference set includes multiline/plural messages. The generated `es`, `sv`,
and `pt_BR` catalogs now contain the complete message set and compiled `.mo`
files. This is catalog completeness, not a claim that every fallback has
received human editorial translation.

- `scripts/data/{es,sv,pt_BR}.py` provide exact dictionaries and recurring
  regex-pattern translations for common UI, LMS, research, and validation
  strings.
- `scripts/generate_locales.py` preserves multiline/plural PO structure,
  reports exact/pattern/fallback coverage, and compiles `.mo` files through the
  Python standard library when `msgfmt` is unavailable.
- Current generated coverage is reported by the command; English fallback
  entries remain an explicit human-review queue rather than being presented as
  fully translated editorial content.
- Site-facing strings not present in the reference catalog must be added via
  the normal extraction workflow before they can be translated.

---

## 6. Email configuration parity + Gmail + test

- **Find** the archived email config in `ctc-research.bak` / archive dirs and
  mirror it into `projects/precis/precis-ctc/backend` (settings/env).
- **Add** the Precis Gmail credentials (EMAIL_HOST=smtp.gmail.com, TLS/SSL,
  the supplied app password) to the ctc backend env (`.env` / `.env.example`
  without printing secrets).
- **Test** by sending to `mahmoud.ezzat.moustafa@gmail.com` via the existing
  `send_test_email` management command (registered in `apps/pages/accounts` and
  `apps/core`).
- Verify `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`, and the notification paths
  (welcome, enrollment confirmation, certificate) use the configured backend.

---

## 7. Shared media + bundles + proxy/nginx serving

Consolidate runtime assets under `projects/assets/` (project-named) so
backend, frontend, and the shared proxy serve one tree.

| Item | Current | Target |
|------|---------|--------|
| Media | `projects/precis/precis-ctc/assets/media/{images,original_images}` (23 runtime files) | Moved to `projects/assets/media/ctc-research/` |
| Bundles | project-local/generated output | Shared `projects/assets/bundles/ctc-research/` |
| Webpack | `webpack/precis.config.js` | Emits to the shared CTC bundle namespace |
| Collected statics | per-project `collectstatic` | CTC static volume is mounted at the proxy’s `ctc-research` site root |
| Proxy | `application/proxy/` (nginx/traefik) | `/media/`, `/static/bundles/`, and `/sites/` route to shared-proxy |
| Naming | mixed `ctcResearch`/`precis-ctc`/`precis` names | Public asset identity is consistently `ctc-research` |

**Implemented:** `MEDIA_ROOT` points to the shared tree by default, Compose
binds that tree into `/app/media`, and shared-proxy mounts it read-only. The
asset verifier and both relevant Compose configs pass validation.

---

## 8. `make redeploy` + environment docs + Nx

- **Implemented `redeploy`:** `projects/precis/precis-ctc/Makefile` runs backend/frontend checks, builds backend/worker/frontend, and recreates backend, worker, scheduler, and frontend.
- **Implemented dispatcher alias:** `cd projects && make redeploy-with-stack WEBSITE=precis-ctc` delegates to the project target. The existing `make redeploy WEBSITE=precis-ctc` remains the dispatcher’s web-only path.
- **Environment docs:** `projects/precis/docs/precis-ctc/ENVIRONMENT.md` records requirements, variable names, asset mounts, safety, and rollback remarks without secrets.
- **Nx:** remains a P2 follow-up; do not add a second package-manager install until the root Nx workspace ownership and target conventions are accepted.

---

## 9. Cross-module automation (16 workflows, Dramatiq boundary)

The companion plan [`precis-ctc-workflows.md`](precis-ctc-workflows.md) defines 16 workflows covering publishing, refresh, email, analytics, and attribution. It makes Dramatiq the single execution boundary and documents the message-replacement semantics, actor contract, rollout, and verification gates.

---

## A. Analyzed todo list (execution order)

> Priority: P0 = publish blocker, P1 = should-have, P2 = nice-to-have.

| # | Task | Priority | Status |
|---|------|:---:|:---:|
| A1 | Complete es/sv/pt-br catalogs (author `scripts/data/*.py`, run generator, compilemessages) | P0 | ✅ Complete message-set PO/MO generation; human review of fallback entries remains |
| A2 | Replace Hero view-source panel with media gallery; remove `<pre><code>` from products snippets; drop unused CodeBlock | P0 | ✅ |
| A3 | Add/verify email config (Gmail) + send test to `mahmoud.ezzat.moustafa@gmail.com` | P0 | ⬜ |
| A4 | Move ctc media + bundles to `projects/assets/media/ctc-research` + `projects/assets/bundles/ctc-research`; point settings at shared tree | P0 | ✅ |
| A5 | Wire nginx/shared-proxy routes for `/media/`, `/bundles/`, `/static/` (filegator + site servers) | P0 | ✅; compose and asset verifier pass |
| A6 | Add `make redeploy` (front + back + attached containers) with precis delegation | P1 | ✅; `make redeploy-with-stack WEBSITE=precis-ctc` delegates to the full stack |
| A7 | Enrich LMS course fixtures (rich_description, modules, lessons) + reconcile the two dump-data copies | P1 | ◐ Seeded 12 modules/24 lessons; dump-copy reconciliation and editorial review remain |
| A8 | Write `docs/CONTENTS.md`, `docs/ENHANCEMENTS.md`, repo `docs/precis-ctc/` + sidebar + plans registry links | P1 | ✅ |
| A9 | Environment docs with requirements remarks + `.env.example` names | P1 | ✅; `projects/precis/docs/precis-ctc/ENVIRONMENT.md` |
| A10 | Nx targets for precis-ctc (check/test/dev/redeploy) + root npm install | P2 | ⬜ |
| A11 | Cross-module automation plan (16 workflows, Dramatiq boundary) | P2 | ✅ Proposed plan in `docs/plans/repository/precis-ctc-workflows.md` |
| A12 | Clear the 9 frontend check hints | P2 | ✅ 0 hints |
| A13 | Decide on the 809 template strings missing from the fr catalog | P2 | ⬜ |

---

## B. Verification gates

- [x] `cd projects/precis/precis-ctc/frontend && npm run check` → 0 errors, 0 warnings, 0 hints
- [ ] `cd projects/precis/precis-ctc/backend && make check` (blocked here by unavailable/stale uv environment)
- [ ] `uv run pytest` (workspace) — targeted CTC tests pass
- [x] Pure-Python locale generation and `.mo` compilation succeed; gettext smoke test loads all three catalogs
- [ ] Test email delivered to `mahmoud.ezzat.moustafa@gmail.com` (requires explicit authorized SMTP execution)
- [ ] `cd projects/precis/precis-ctc && make redeploy` brings backend/worker/scheduler/frontend back healthy (not run; effectful)
- [x] Nginx/Traefik/Compose asset mappings verify; live `/media/`, `/bundles/`, `/static/` check remains deployment-gated

---

## C. Interrupted session handoff TODOs

These items were not completed in this chat because the required environment,
credentials, editorial approval, or live-service authorization was unavailable.
They are intentionally recorded here rather than being represented as passed:

- [ ] Restore the approved workspace `uv` environment and run CTC backend
  `make check` plus the targeted fixture/API tests.
- [ ] Run the workspace pytest suite and verify the new curriculum/navigation
  regression tests against a disposable test database.
- [ ] Obtain explicit SMTP authorization, verify the configured sender/app
  password through the approved secret store, and send the requested test email
  to `mahmoud.ezzat.moustafa@gmail.com`.
- [ ] Build the Django-side CTC bundles in the dependency-enabled environment,
  run `collectstatic`, and verify the live `/media/`, `/bundles/`, and `/static/`
  responses through shared-proxy.
- [ ] Execute the effectful CTC full-stack redeploy and verify backend, worker,
  scheduler, frontend, health, and logs; do not load or replace database data.
- [ ] Decide whether Nx should own CTC `check`, `test`, `dev`, and `redeploy`
  targets before adding a second package-manager workflow.
- [ ] Complete qualified medical, legal, image-rights, and human translation
  review before public publication; generated locale fallbacks are not approval.

## Related

- ceptor-ai removal (complete — see [`docs/agenda/feature-tracking.md`](../../agenda/feature-tracking.md) § CTC Research)
- [`../README.md`](../README.md) — plans registry
- [`active-monorepo-consolidation-2026-08-14.md`](active-monorepo-consolidation-2026-08-14.md) — shared Dramatiq baseline
- [`../../recent-changes.md`](../../recent-changes.md) — session log
