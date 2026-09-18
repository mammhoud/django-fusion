# Precis CTC Research changelog

## 2026-08-19 — Marketing routes, schema migrations & production verification

### Added

- **Wagtail marketing pages** — added `MarketingPage` and migration
  `0012_marketingpage` for `/faq/`, `/pricing/`, `/features/`, `/projects/`,
  and `/products/`, with editable hero, FAQ, pricing, feature, project,
  product, statistics, and CTA blocks.
- **Localized seed data** — seeded five English pages and five Arabic
  translations using one Wagtail `translation_key` chain per route; the
  canonical backend and project fixtures contain the same rows.
- **Route regression coverage** — added browser coverage for the five marketing
  routes and verified the complete CTC Playwright suite after the frontend
  rebuild.
- **Products schema** — added `apps/pages/products/migrations/0001_initial.py`
  for `Cart` and `CartItem`, plus Django admin registrations with inline cart
  items.
- **Delete-cascade schema** — added the missing profile migration and the
  shared `django_fusion` initial migration needed by user deletion cascades.
  The latter is owned by the `libs/django-fusion` submodule and must be
  committed in that submodule separately from the CTC repository.

### Fixed and verified

- Corrected Wagtail `ListBlock` seed serialization so pricing tiers and project
  cards expose their values instead of `null` in the API.
- Rebuilt the CTC frontend after seeding so the five Astro routes contain the
  current backend data.
- Verified the backend test suite and full Playwright suite after deployment;
  the live marketing routes return backend content in English and Arabic when
  the locale is selected.

### Follow-up

- Human linguistic review remains required for translated medical/course copy.
- Remaining SEO enhancements are `hreflang`, JSON-LD structured data, and
  per-article/per-event Open Graph images.
- The backend system check still reports Treebeard future-compatibility
  warnings; they are not silenced by this release.

## 2026-08-19 — SEO metadata, Wagtail-driven content & admin routing

### Added

- **Site-level SEO settings** — `SiteSettings` gained `og_type`, `robots_meta`
  and `canonical_url` (migration `0010`); `get_seo_context()` now returns
  robots + canonical + og type alongside description/keywords/author/OG image,
  and `/apis/site/settings/` exposes them.
- **Per-page SEO block** — `/apis/pages/<slug>/` now returns a `seo` object
  (title, description, keywords, author, og_type, og_image_url,
  twitter_handle, robots, canonical) built from the page's Wagtail SEO fields
  with SiteSettings fallbacks; canonical falls back to the request URL.
- **Django render-road meta tags** — a `seo_context_processor` + Wagtail
  `before_serve_page` hook populate `seo_context`; `base.html` now renders
  description/keywords/author/robots/OG/Twitter/canonical from Wagtail-managed
  settings instead of a hardcoded string.
- **Astro render-road meta tags** — `Layout.astro` resolves SEO from
  `pageData.seo` + `siteSettings` (og:type, og:site_name, keywords, author,
  robots, twitter:site, canonical) with only config-level fallbacks.
- **About page mission/skills/FAQ blocks** — `AboutPage.facts` now accepts
  `mission`, `skills` and `faq` blocks (migration `0011`); the fixture seeds
  all three across all 7 locales (EN/AR/DE/ES/FR/PT-BR/SV) and
  `/apis/pages/about/` exposes `mission_values`/`skills`/`faq` (+ titles).
- **Swedish content** — seeded the missing SV home (`hem`) and About
  (`Om CTC Research`) translations, localized counters and facts, and added
  the SV locale + rows to the canonical fixture.
- **Traefik admin routing** — exact `Path(/admin)` and `Path(/django-admin)`
  matchers added to the backend router so Django's `APPEND_SLASH` handles the
  301 (previously the Astro catch-all served its own 404 for `/admin`).

### Fixed

- **Localized-slug translation resolution** — `_live_page` now falls back to
  the Wagtail translation chain (`translation_key`) when the requested locale
  renames the page slug (e.g. the Arabic About page), passing a `Locale`
  object (not a string) to `get_translation_or_none`. Arabic About now serves
  Arabic content instead of the English edition.
- **About facts KeyError** — the container's baked fixture predated the
  StreamBlock `counters` wrapper (`{id, type, value}`); the live DB was
  repaired from the canonical fixture and the reference-index task no longer
  crashes.
- **About extraction early-break** — `_extract_seeded_blocks` no longer
  `break`s after the first `about` block, so mission/skills/faq blocks are
  exposed alongside counters/gallery/video.

### Removed

- **Hardcoded frontend fallback copy** — the About, FAQ, Pricing, Features,
  Projects and Products Astro pages no longer ship static English arrays
  (mission values, skills, testimonials, FAQs, pricing tiers, project cards,
  product cards, stats). All such sections render from backend `pageData`
  only; empty sections render nothing. (Seed the corresponding Wagtail pages
  to populate the auxiliary routes.)
- **Dead `privacy:` namespace reference** in the register fragment — now uses
  the live `handlers:policy_modal` route (fixes a 500 on the custom register
  form).

### Verified

- 193 backend tests + 62 fixture/API/content tests + Astro check (0 errors) +
  43 Playwright tests pass.
- `/admin` → 301 → `/admin/` → Wagtail admin login/dashboard;
  `/django-admin` → Django admin (Unfold). Full login flow verified with a
  throwaway superuser and removed afterwards.

## 2026-08-19 — Legacy cleanup: −94 MB of generated static from git

### Removed

- **`backend/assets/staticfiles/` (38 MB)** — generated `STATIC_ROOT` output
  (third-party collected statics) committed to git; `/prepare` re-runs
  `collectstatic --noinput` at every container start, so the copy is dead
  weight in the repo and the image build.
- **`backend/assets/static/` (3 stale files)** — legacy `site/precis-ctc/`
  namespace source (`skeleton-manifest.json`, `css/fusion.css`,
  `js/fusion-bridge.js`) that `settings/assets.py` itself flags as a
  collectstatic duplicate; nothing references `/static/site/precis-ctc/`.
- **`assets/staticfiles/site/precis-ctc/` (28 MB) + `assets/staticfiles/workspace-assets/` (27 MB)** —
  stale collected duplicates inside the nginx-served static tree; no template,
  bundle, or proxy reference points at either namespace.

### Verified

- `manage.py check` clean (only pre-existing treebeard warnings);
  `collectstatic --dry-run` succeeds (1733 unmodified); live site + admin +
  bundles + media all 200 after removal. Full deletion record in
  [`docs/plans/deletion-manifest.md`](../../docs/plans/deletion-manifest.md)
  (DOC-0025 … DOC-0028).

## 2026-08-19 — Blur-free reveals, spring motion & calmer palette

### Fixed

- **Reveal blur stuck on cards** — `globals.css` carried two competing
  `.reveal` rules; the later one dropped `filter` from the transition list, so
  `blur(4px)` lingered after load (the `p-7 reveal` cards looked soft-focus
  forever). The duplicate rule is gone and the canonical `.reveal` no longer
  uses `filter` at all — a clean translate+scale rise on the premium bezier.
  Hero blocks, the course-detail `reveal-up`, and the GSAP hero intro also
  dropped their blur filters.
- **No-JS / reduced-motion safety** — hidden reveal states are now gated on
  the `.js` class (set inline in the Layout head), so without JavaScript
  content is fully visible and nothing can be stuck at `opacity: 0`; a
  `prefers-reduced-motion` override forces everything visible.

### Changed

- **Calmer colors** — desaturated the teal primary (`187 55% 32%` vs the old
  `186 100% 35%`) and soft periwinkle accent (`244 48% 57%` vs `243 100% 69%`),
  softened paper/ink/line, and matched dark-mode accents. Mirrored in
  `_variables.scss` and the theme-color meta (`#F8FAFB`).
- **Backend `fusion.css` rebuilt** — the served file was a stale Dec-2025
  artifact (no `.reveal` styles at all, old palette). It is now compiled from
  `globals.css` via the Tailwind CLI, so both render roads share the same
  calm palette and reveal system.
- **Animations** — reveals upgraded to `0.8s var(--ease-premium)` spring
  motion with a subtle scale; no `ease`/`ease-in-out`/linear remains in the
  reveal paths.

## 2026-08-19 — Live media pack, course-carousel slider & breadcrumbs

### Fixed

- **Media serving chain** — the backend compose mounted the rendition-only tree
  (`projects/precis/assets/media/ctc-research`) instead of the monorepo-shared
  source tree (`projects/assets/media/ctc-research`), so the media manifest
  reported 0 available items and every image 404'd. The mount now points at the
  shared tree; `prepare_ctc_media` populates `ctc-content/` + `original_images/`
  aliases, and the shared Nginx proxy was recreated to drop its stale
  `/home/coder/...` mount. The manifest now serves **58/58 items** and every
  page image resolves 200.
- **Restored missing archive images** — copied 32 fixture-referenced renditions
  into the shared `images/` tree and the missing `DashboardDesign` hero original
  into `original_images/`, so Wagtail-rendered blocks no longer reference
  absent files.

### Added

- **Course-carousel slider on the homepage** — `CourseSlider.astro` renders the
  featured catalog as an archive-style card carousel (autoplay, dots, arrows,
  1/2/3-per-view responsive). Alpine moves a server-rendered strip, so no-JS
  still shows every course. Slides dedupe per-language editions (prefer
  English), capped at 6, with archive media-pack card art.
- **Breadcrumbs across every page** — new `Breadcrumb.astro` BEM component
  (archive `fu-breadcrumb__list` adapted). Wired into `PageHeader` and `Hero`
  (auto `Home / title`), with explicit parent trails on About subpages
  (`About / Founder|Research|Education`), Courses, Blog index + detail, and a
  bespoke crumb trail on the cinematic course-detail hero.

## 2026-08-19 — About dropdown navigation & founder subpage

### Added

- **About dropdown navigation** — the About nav item now carries curated
  children (Founder, Research, Education, Team, Services) mirroring the
  Precis Landing contract. Desktop shows a hover/click dropdown; the mobile
  menu expands a sub-list. Backend serves `children` from `navigation_api`
  (`_NAV_CHILDREN_CURATED`), the frontend `NavItem` type + Header render it.
- **Founder subpage** — `/about/founder/` profiles the center's cofounder,
  modeled on the research subpage design; linked from the About dropdown and
  covered by backend nav, node e2e and Playwright assertions.

## 2026-08-19 — Interactive course catalog, editorial blog & admin routing

### Added

- **Course catalog toolbar** — `/courses/` now carries the archive-theme feature
  set: live search, difficulty/language/specialization/topic/offer/certificate
  filters, sort (rating, price, duration, title), grid↔list view toggle, results
  counter and active-filter count, and a catalog badge in the hero. Pure
  client-side Alpine over the SSR grid (no-JS shows every course); component
  lives in `src/alpine.js` (`courseCatalog`).
- **Course detail "Keep exploring" strip** — up to 3 related courses under the
  syllabus (uses the cached catalog; no extra build-time fetches).
- **Editorial blog** — `apps/pages/blog/management/commands/seed_blog_posts.py`
  seeds 4 published posts (categories + tags); `/blog/` index and
  `/blog/<slug>/` detail now render real content (previously a fallback error).
- **Course card meta** — price, rating, language badge and topic tags on every
  catalog card; `data-*` attributes drive the filters.

### Fixed

- **Course detail syllabus** — `/api/courses/<slug>/` filtered modules/lessons
  by a nonexistent `is_published` field (silently swallowed, so every course
  returned an empty syllabus). Modules now use their real fields
  (`Lesson.is_active`) and the API logs on failure. Regression asserted in
  `tests/test_fixture_data.py`.
- **Navigation** — removed the auto-added "Documents" header item; `/documents/`
  (publications) and `/profile/` (learner summary) are now Astro-owned routes
  instead of being intercepted by the backend prefix router.
- **e2e correctness** — page checks assert against *rendered* content
  (`<template>`/`<script>`/`<style>` stripped); backend requests send
  `X-Forwarded-Proto` so the local stack's HTTPS redirect does not break them;
  stale blog/product/team/service assertions updated to the seeded copy.

### Proxy (application/proxy)

- Every Django+frontend project now routes its admin/CMS on the public domain:
  `/admin` + `/django-admin` (precis-landing, lms-fusion, precis-ctc) and
  `/admin` + `/django-admin` + `/cms` (loop-crm Wagtail). Recreated the Traefik
  container so its bind mounts point at the current `application/proxy/` paths.

### Verification

- Backend suite: **192 passed, 6 subtests** (incl. course-modules regression).
- Frontend: smoke 1/1, section-placement 11/11, node e2e 12/12, Playwright
  **42 passed / 1 skipped / 0 failed**.

## 2026-08-18 — Research publications, OpenAPI & django-fusion filtering

### Added

- **Publication content** — `apps.content.models.publication.Publication` /
  `PublicationCategory` (Wagtail-registered, migration `0008_publication`).
- **Research library API** — `/apis/research/publications/` (localized, with
  `?category=`, `?q=`, `?ordering=`, and `?limit=`/`?page=`/`?offset=`).
- **OpenAPI docs** — `/apis/openapi.json` + `/apis/docs/` (Swagger UI), built from
  `apps.core.openapi` (17 paths, 5 tags).
- **Research library page** — frontend `/documents/` (per-language library).
- **Docs** — `../docs/precis-ctc/LEARNING_CASES.md` (technique recipes) + `../docs/precis-ctc/CONTENTS.md`
  cross-links.

### Changed

- `landing_api.py` — `auth_status_api` mirrors precis-landing (session + learner
  summary); `content_languages_api` serves the 7-language catalog.
- `apps/urls.py` — mounted OpenAPI JSON/UI and the publications route.

### Library (django-fusion, consumed here)

- `FusionApiViewset` filtering/search/ordering/pagination + Django-native OpenAPI
  builder (`docs/19-openapi-and-filtering.md`).

### Verification

- Backend suite: **192 passed, 6 subtests**.
- Frontend suites green: smoke 1/1, e2e 11/11, section-placement 11/11.
  Updated stale content assertions (courses, products, about, services) to
  match the redesigned pages.
- Loaded the research-publication seed (8 objects → 1 doc per language, 7
  languages) into the running database; cleared the stale cache middleware TTL.
- Rebuilt + redeployed the Astro frontend so `/documents/`, `/about/research/`,
  and `/about/education/` serve (were 404 on the stale image).

## 2026-08-11 - Active deployment and plan closeout

### Changed

- Confirmed `projects/precis/precis-lms/` as the canonical LMS runtime after the former
  LMS-Fusion/CMS-Fusion consolidation.
- Added the project-owned `/api/fusion/health` and slash-terminated alias used
  by direct and Traefik deployment smoke checks.
- Made fixture loading explicit for the shipped canonical dump. The default
  command no longer silently loads historical fixture data.
- Rebuilt the backend/frontend images and verified API and rendered page routes
  through the Traefik host.

### Verification

- Focused API and fixture tests: 77 passed.
- Direct and proxy API/page curl checks returned HTTP 200.
- Backend, frontend, worker, PostgreSQL, Redis, and Traefik containers were
  running with no service restarts at closeout.

## 2026-07-30 - ceptor-ai cleanup + enhanced test coverage

### ceptor-ai dependency fully removed
- 0 ceptor_ai imports remaining in any fusion project
- Local models (Organization, Contact, ContactEmail, ContactPhone, Team, Workspace) ported from ceptor_ai
- PrivacyConsentMiddleware, PaymentProcessingMixin, ProfileMixin, dispatch_job stubs created locally
- Newsletter system already fully native (Subscriber, Campaign, email templates)

### tests: 113 tests, 0 failures
- Existing: 86 tests (smoke, API, domain models, fixture content)
- Enhanced: 27 new tests (test_enhanced_api.py)
  - CORS headers verification
  - HTMX request handling (HX-Request header)
  - Error handling (404, 405/400, bad params)
  - Trailing slash redirects for all endpoints
  - Branding detail structure (colors, site_name)
  - Pages fragment/data sub-endpoints
  - Courses filters structure validation
  - Content-Type: application/json on all endpoints
  - Security headers (X-Content-Type-Options)
  - Fusion assets endpoint accessibility
- Fixed: 3 trailing-slash failures in test_fixture_content.py

### API endpoints verified
- /api/fusion/health/ ✅
- /api/fusion/branding/ ✅
- /api/pages/ ✅
- /api/pages/<slug>/fragment/ ✅
- /api/pages/<slug>/data/ ✅
- /api/blog/ ✅
- /api/blog/categories/ ✅
- /api/blog/tags/ ✅
- /api/courses/ ✅
- /api/courses/filters/ ✅
- /api/products/ ✅

## 2026-07-26 — Fusion architecture migration (Phase 5 complete)

### django-fusion + django-bolt integration
- Backend API with django-fusion component system
- django-bolt BoltAPI for high-performance endpoints
- Next.js 14 frontend with fusion types/decoder/store/client
- Django server on port 5076, Next.js on port 3076

### Template reorganization
- App-specific templates moved to plugins/<app>/templates/
- Site-root templates remain in backend/templates/
- SCSS theme single source-of-truth in assets/styles/fusion-theme.scss
- Compiled CSS output to backend/assets/static/css/fusion.css

### Validation
- make check: ✅ (exit 0)
- Backend tests: 135 passed
- Frontend build: ✅ compiled successfully
- Workspace tests: 50 passed
