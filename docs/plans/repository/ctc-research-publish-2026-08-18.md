# CTC Research — Publish Plan & Analyzed Todo List

> **Status:** Active — execution checklist for publishing `ctc-research.com`
> **Date:** 2026-08-18
> **Canonical path:** `projects/precis/precis-ctc/`
> **Tags:** #precis-ctc #publish #i18n #media #proxy #redeploy #content
> **Related:** [`ctc-research-ceptor-ai-migration.md`](ctc-research-ceptor-ai-migration.md) (✅ code-level complete), [`../README.md`](../README.md)

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
- **Frontend check:** `npm run check` → 0 errors, 9 hints (unused vars in
  `BackToTop`, `Modal`, `ShareButtons`, `LoginModal` `__FUSION_AUTH` typing,
  unused `Features` import in `services.astro`).

**Enhancement candidates identified (not yet executed):**
- Clear the 9 frontend check hints (unused declarations/imports).
- Unify the two dump copies (`backend/assets/fixtures/dump-data.json` vs
  `assets/fixtures/dump-data.json` — same object count, different hashes).
- `products/[slug].astro` still renders a raw `<pre><code>` snippets section
  (see §3).

---

## 2. Documentation (partial — complete per §A)

Existing project docs: `docs/COMPONENTS.md`, `docs/SETUP_AND_BUILD.md`,
`docs/TEMPLATES.md`. Repo docs: `docs/precis/{ARCHITECTURE,configuration,courses,deployment}.md`
(target `precis-main`, not ctc). **To write:**
- `projects/precis/precis-ctc/docs/CONTENTS.md` — page-by-page content map
  (sections, data sources, fallbacks).
- `projects/precis/precis-ctc/docs/ENHANCEMENTS.md` — the audit findings +
  enhancement list (this session's §1 + §3 + §7 + §9).
- Repo `docs/precis-ctc/` index (architecture, content, media/proxy, deploy)
  linked from `docs/_sidebar.md` and `docs/plans/README.md`.

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

**Approach:** add a reusable `MediaGallery.astro` (grid + lightbox + captions,
reusing the about-page gallery mapping already in `about.astro`), wire it into
`Hero.astro` as the right-hand panel, and replace the products snippets section.

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
  courses (en only, no rich_description/modules/lessons yet), 8 tags, 5
  specializations. **Gap:** courses have no modules/lessons — enrich before
  publish.
- `events.json`, `courses.json`, `specializations.json`, `course_tags.json` —
  supporting LMS fixtures (loaded via `load_course_fixtures`).
- Two dump copies exist (`backend/assets/fixtures` + `assets/fixtures`) with
  different hashes — reconcile to one canonical file.

---

## 5. Translations — complete es/sv/pt-br catalogs

**State:** fr/de/ar catalogs under `assets/locale/<lang>/LC_MESSAGES/django.po`
are complete (3,433 entries, ~96% translated). **es/sv/pt-br are stubs (4
strings each).** User chose **full catalogs (all ~3,400 strings).**

- Generator scaffolded: `projects/precis/precis-ctc/scripts/generate_locales.py`
  rebuilds es/sv/pt-br from the fr reference (preserves comments/order,
  substitutes translations, safe English fallback).
- **To do:** author `scripts/data/{es,sv,pt_BR}.py` translation dicts for the
  full msgid set (3,433), run the generator, then `compilemessages` so `.mo`
  files exist for runtime. Verify with `msgattrib`/`msgfmt` and a Django
  `activate('es')` smoke test.
- Also surface site-facing strings currently missing from the catalog (809
  `{% trans %}` strings used by templates but not in the fr set) — decide
  whether to add them to the catalog or leave untranslated.

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
| Media | `projects/precis/precis-ctc/assets/media/{images,original_images}` (23 files) | Move to `projects/assets/media/ctcResearch/` (dir exists, empty); keep project-named subdir for easy mapping |
| Bundles | `projects/precis/precis-ctc/assets/bundles/` (webpack output) | Move beside media → `projects/assets/bundles/precis-ctc/` |
| Webpack | `webpack/precis.config.js` → `assets/bundles/` | Emit to shared `projects/assets/bundles/precis-ctc/` |
| Collected statics | per-project `collectstatic` | Serve from shared static tree so backend + frontend agree |
| Proxy | `applications/proxy/` (nginx/traefik/caddy) | Add routes so `/media/`, `/bundles/`, `/static/` are served by `shared-proxy`; restrict to filegator / website servers matching the site name |
| Naming | `ctcResearch` (camelCase) | Prefer lowercase `ctc-research` for consistent mapping (align with `precisLanding` decision) |

**Note:** `projects/assets/media/{precisLanding,filegator,ctcResearch}` already
exist — this is the intended shared layout. Update `MEDIA_ROOT` / `STATIC_ROOT`
in ctc `settings.py` to point at the shared tree, and wire nginx location
blocks in `applications/proxy/nginx/`.

---

## 8. `make redeploy` + environment docs + Nx

- **Add `redeploy` target** to `projects/precis/precis-ctc/Makefile` that:
  1. runs the backend checks/tests,
  2. rebuilds + restarts backend, worker, frontend (and other attached
     containers) via `docker compose build/up -d --force-recreate`,
  3. delegates to the correct precis command (respect `WEBSITE=` dispatch;
     `make check/test/run-dev` already delegate to `backend/` Makefile).
- **Environment docs:** write `docs/SETUP_AND_BUILD.md` "Environment" section
  (or a new `docs/ENVIRONMENT.md`) with every env var + requirement remarks,
  `.env.example` names only (no secrets).
- **Nx:** precis-ctc has `project.json` (build target only). Consider adding
  `check`/`test`/`dev`/`redeploy` Nx targets mirroring the Loop-CRM wiring
  (`nx run precis-ctc:<target>` ←→ `make <target>`), then root `npm install`
  to enable `npx nx` at the monorepo root.

---

## 9. Cross-module automation (16 workflows, Dramatiq boundary)

Add a plan section/companion doc for cross-module automation:
- **16 ready workflow definitions** covering publishing, refresh, analytics,
  and attribution across modules.
- **Dramatiq as the single execution boundary** for publishing, refresh,
  analytics, and attribution (align with the shared Dramatiq baseline in
  `repository/active-monorepo-consolidation-2026-08-14.md`).
- Message-replacement semantics: workflows replace direct in-process calls with
  a queue boundary so modules publish/refresh/attribute through one pipeline.
- **To do:** draft `docs/plans/repository/precis-ctc-workflows.md` with the 16
  definitions, triggers, and Dramatiq actor list; register in the plans README.

---

## A. Analyzed todo list (execution order)

> Priority: P0 = publish blocker, P1 = should-have, P2 = nice-to-have.

| # | Task | Priority | Status |
|---|------|:---:|:---:|
| A1 | Complete es/sv/pt-br catalogs (author `scripts/data/*.py`, run generator, compilemessages) | P0 | ⬜ |
| A2 | Replace Hero view-source panel with media gallery; remove `<pre><code>` from products snippets; drop unused CodeBlock | P0 | ⬜ |
| A3 | Add/verify email config (Gmail) + send test to `mahmoud.ezzat.moustafa@gmail.com` | P0 | ⬜ |
| A4 | Move ctc media + bundles to `projects/assets/media/ctcResearch` + `projects/assets/bundles/precis-ctc`; point settings at shared tree | P0 | ⬜ |
| A5 | Wire nginx/shared-proxy routes for `/media/`, `/bundles/`, `/static/` (filegator + site servers) | P0 | ⬜ |
| A6 | Add `make redeploy` (front + back + attached containers) with precis delegation | P1 | ⬜ |
| A7 | Enrich LMS course fixtures (rich_description, modules, lessons) + reconcile the two dump-data copies | P1 | ⬜ |
| A8 | Write `docs/CONTENTS.md`, `docs/ENHANCEMENTS.md`, repo `docs/precis-ctc/` + sidebar + plans registry links | P1 | ⬜ |
| A9 | Environment docs with requirements remarks + `.env.example` names | P1 | ⬜ |
| A10 | Nx targets for precis-ctc (check/test/dev/redeploy) + root npm install | P2 | ⬜ |
| A11 | Cross-module automation plan (16 workflows, Dramatiq boundary) | P2 | ⬜ |
| A12 | Clear the 9 frontend check hints | P2 | ⬜ |
| A13 | Decide on the 809 template strings missing from the fr catalog | P2 | ⬜ |

---

## B. Verification gates

- [ ] `cd projects/precis/precis-ctc/frontend && npm run check` → 0 errors
- [ ] `cd projects/precis/precis-ctc/backend && make check` (needs working uv/venv)
- [ ] `uv run pytest` (workspace) — targeted ctc tests pass
- [ ] `compilemessages` succeeds; `activate('es'/'sv'/'pt-br')` smoke test renders
- [ ] Test email delivered to `mahmoud.ezzat.moustafa@gmail.com`
- [ ] `make redeploy WEBSITE=precis-ctc` brings backend/worker/frontend back healthy
- [ ] `/media/`, `/bundles/`, `/static/` respond through the shared proxy

---

## Related

- [`ctc-research-ceptor-ai-migration.md`](ctc-research-ceptor-ai-migration.md) — ceptor-ai removal (complete)
- [`../README.md`](../README.md) — plans registry
- [`active-monorepo-consolidation-2026-08-14.md`](active-monorepo-consolidation-2026-08-14.md) — shared Dramatiq baseline
- [`../../recent-changes.md`](../../recent-changes.md) — session log
