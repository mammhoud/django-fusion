# CTC Research — Learning Cases

> **Canonical project:** `projects/precis/precis-ctc/`
> **Purpose:** precise, worked examples for the techniques this site uses. Each
> case is a recipe: **Goal → Files → Steps → Verify → Gotcha.**

<!-- AI-generated: review needed -->

These cases are the "how" behind the content map
([`CONTENTS.md`](CONTENTS.md)) and the publishing workflow
([`../../../../docs/precis-ctc/publishing-and-production.md`](../../../../docs/precis-ctc/publishing-and-production.md)).
They assume the render-first / data-API / HTMX-fragment contract from
[`CONTENTS.md`](CONTENTS.md) §1.

---

## Case 1 — Publish a research publication

**Goal:** add one multilingual document to the research library and expose it
on `/apis/research/publications/`.

**Files**
- `backend/apps/content/models/publication.py` — `Publication` model (already exists).
- `backend/assets/fixtures/research_publications.json` — seed rows.
- `backend/apps/pages/pages/landing_api.py` — `research_publications_api` serializer.

**Steps**
1. Add a `PublicationCategory` row (e.g. `{"model": "pages.publicationcategory", "pk": 1, "fields": {"name": "Protocol design", "slug": "protocol-design"}}`).
2. Add a `Publication` row with `language`, `authors`, `abstract`, `is_published: true`.
3. Load via the data command (see `publishing-and-production.md` §4).
4. Verify:
   ```bash
   curl -sS 'http://localhost:5070/apis/research/publications/?lang=en&category=protocol-design'
   ```
5. Confirm the document appears on `/documents/` and in the OpenAPI spec.

**Verify:** the response has `documents`, `total`, `language`, and `guidance`.

**Gotcha:** the model's `app_label` is `"pages"` (the `apps.content` app label).
Do not reference it as `apps.content.Publication` in fixtures — use
`"pages.publication"`.

---

## Case 2 — Query the publications API with filters

**Goal:** use the django-fusion query surface.

```bash
# search title/authors/abstract
curl -sS 'http://localhost:5070/apis/research/publications/?q=cohort'
# order newest first, page 2
curl -sS 'http://localhost:5070/apis/research/publications/?ordering=-published_at&page=2&limit=10'
```

Supported: `lang`, `q`, `category`, `ordering`, `limit`, `page`, `offset`.

**Verify:** `count ≤ limit`, `page` reflects `offset`, `total` is the full set.

**Gotcha:** undeclared params are ignored (safe), but the endpoint only honours
the allowlist above — `?sort=` is not supported; use `?ordering=`.

---

## Case 3 — Add a multilingual course + module + lesson

**Goal:** extend the seeded curriculum.

**Files**
- `backend/apps/learning/fixtures/medical_research_courses.json`
- `backend/apps/learning/fixtures/medical_research_curriculum.json`

**Steps**
1. Add a course with the research-focused metadata (title, slug, tags, specialization).
2. Add a `Module` row (requires `created_at`/`updated_at`) and a `Lesson` row
   with rich-text content.
3. Load with the learning fixture command, then verify:
   ```bash
   curl -sS http://localhost:5070/api/courses/<slug>/
   ```

**Gotcha:** module fixtures must include `created_at`/`updated_at`; the lesson
contract is rich text, not code blocks (see the medical-content rules in
`CONTENTS.md`).

---

## Case 4 — Add a BEM content block (frontend + backend)

**Goal:** add a reusable block rendered both by Astro and by a Django template.

**Files**
- `frontend/src/components/blocks/<Name>.astro` — Astro block (BEM classes).
- `frontend/src/styles/_blocks.scss` — styles, imported by `fusion.scss`.
- `backend/apps/templates/.../<include>.html` — server-rendered equivalent.

**Steps**
1. Model the block on an existing one (`EventCard.astro`, `CounterCard.astro`,
   `CertificateCard.astro`) — BEM root class e.g. `fu-event-card`, elements
   `fu-event-card__title`, modifiers `fu-event-card--featured`.
2. Add styles to `_blocks.scss`; do not use IDs for styling.
3. In the Django template, mirror the same BEM class names so the two roads
   share one visual contract.
4. Verify: `make frontend-check` (Astro build) and
   `curl -sS http://localhost:5070/fragment/pages/<slug>/` (server road).

**Gotcha:** a server-rendered fragment and the Astro block must produce the same
BEM contract; otherwise render-mode switching breaks the layout.

---

## Case 5 — Understand the three rendering roads

**Goal:** pick the right road for a change.

| Road | URL | Returns | Use when |
|---|---|---|---|
| Render-first (HTML) | `/<slug>/` via Wagtail | Full HTML | Server-side content |
| Data API (JSON) | `/apis/pages/<slug>/` | JSON payload | Astro client data |
| HTMX fragment | `/fragment/pages/<slug>/` | Content-only HTML | In-page swap |

- Header `X-Fusion-Render-First: true|false` overrides the configured default.
- `/apis/render-mode/` reports the active mode.

**Gotcha:** a fragment request must never return the full layout — it returns
only the content region. Keep these three contracts separate.

---

## Case 6 — Add a Wagtail page + About subpage

**Goal:** add a new localized page and a frontend route.

**Files**
- Wagtail page model (or an existing page type) under `backend/apps/content/`.
- `frontend/src/pages/<route>.astro` (e.g. `about/research.astro`,
  `about/education.astro`).
- `_FRONTEND_ROUTES` / `_FRAGMENT_TEMPLATES` maps in
  `backend/apps/pages/pages/landing_api.py` if it needs a fragment/nav entry.

**Steps**
1. Create/locate the page, add localized copies per `Locale`.
2. Add the Astro route and wire any shared blocks.
3. Register the route in the landing API maps so navigation/fragments resolve.
4. Verify: `make check`, `make frontend-check`, then
   `curl -sS http://localhost:5070/apis/pages/<slug>/`.

**Gotcha:** the site registry maps page slugs to frontend routes — if you add a
page but no frontend route, the nav/fragment lookups will miss it.

---

## Case 7 — Document an endpoint in OpenAPI

**Goal:** make a new `/apis/*` endpoint discoverable at `/apis/docs/`.

**Files**
- `backend/apps/core/openapi.py` — `build_spec()`.
- `backend/apps/urls.py` — the route itself.

**Steps**
1. Add the endpoint view (e.g. in `landing_api.py`).
2. Register the route in `apps/urls.py`.
3. Add `spec.add_path(...)` with `summary`, `tags`, `params`, and
   `responses` (see `django-fusion` DF-019: `libs/django-fusion/docs/19-openapi-and-filtering.md`).
4. Verify:
   ```bash
   curl -sS http://localhost:5070/apis/openapi.json | grep -A2 '<your-path>'
   ```

**Gotcha:** the OpenAPI spec is a Django-native `OpenAPISpec`, not a Bolt Rust
server — keep `/apis/*` and `/bolt/*` prefixes distinct (DF-019 §"Choosing a road").

---

## Case 8 — Resolve localized pages when locales rename the slug

**Goal:** make `/apis/pages/about/?lang=ar` return the Arabic edition even
though the Arabic page uses a translated slug (`عن-سي-تي-سي-للبحث-العلمي`)
while every other locale keeps the slug `about`.

**Files**
- `backend/apps/pages/pages/landing_api.py` — `_live_page(slug, language)`.

**Steps**
1. First try the direct slug match:
   `pages.filter(slug=normalized).filter(locale__language_code=language)`.
2. When that misses (locale renamed the slug), resolve the base (EN) page and
   walk the Wagtail translation chain by `translation_key`:
   `base.get_translation_or_none(locale=locale_obj)`.
3. Pass a `Locale` instance, **not** a language-code string —
   `get_translation_or_none(locale="ar")` raises
   `Field 'id' expected a number but got 'ar'`.
4. Return the translation if found, otherwise the base page (default
   language fallback).

**Verify:**
```bash
curl -sS 'http://localhost:5070/apis/pages/about/?lang=ar' | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["title"], (d.get("mission_values") or [{}])[0].get("title"))'
# → Arabic title + Arabic mission value
```

**Gotcha:** keep the translation chain resolution on the *page* (Wagtail
`translation_key`), not the locale prefix on the URL path — locales with
localized slugs have different `url_path`s, but share one `translation_key`.

---

## Case 9 — Expose SEO metadata from Wagtail settings on both roads

**Goal:** every page returns a `seo` block (`/apis/pages/<slug>/`) and both
render roads emit the meta tags from backend data — no hardcoded meta copy.

**Files**
- `backend/apps/content/models/settings.py` — `SiteSettings` (`og_type`,
  `robots_meta`, `canonical_url` + `get_seo_context()`).
- `backend/apps/pages/pages/landing_api.py` — `_page_data` `seo` block +
  `site_settings_api` exposure.
- `backend/apps/pages/pages/wagtail_hooks.py` + `apps/pages/context_processors.py`
  — `seo_context` for the Django road.
- `backend/templates/base.html` — meta block.
- `frontend/src/layouts/Layout.astro` — `resolveSeo()` + meta tags.

**Steps**
1. Extend `SiteSettings.get_seo_context()` with the new fields and merge them
   into `_page_data["seo"]`: page `seo_title`/`search_description` win, site
   defaults fill the gaps.
2. Resolve settings with `SiteSettings.for_request(request)`; when no request
   is available (build-time), fall back to `SiteSettings.load()` inside a
   `try/except` (the load signature requires an argument in some Wagtail
   versions).
3. On the Django road, set `request.seo_context` in `before_serve_page` and
   expose it via a context processor; `base.html` renders the meta block.
4. On the Astro road, `Layout.astro` computes SEO from `pageData.seo` +
   `siteSettings` and renders og:type/og:site_name/keywords/robots/twitter:
   site/canonical.

**Verify:**
```bash
curl -sS 'http://localhost:5070/apis/pages/about/' | python3 -c 'import json,sys; print(json.load(sys.stdin)["seo"]["robots"])'
# → "index, follow" (or the site-level override)
```

**Gotcha:** `PageData.seo` and the `SiteSettings` frontend type must declare
all the new keys, or the Astro check fails with `Property 'seo' does not
not exist` — keep `frontend/src/lib/api.ts` in sync with the API response.

---

## Remarks & Notes

- All commands assume the backend is reachable on `localhost:5070`; adjust for
  your Compose/port layout (see `ENVIRONMENT.md`).
- These cases document **implementation technique**, not clinical validity.
  Public copy still requires the review gates in the publishing doc.
- If a case and `CONTENTS.md` disagree, `CONTENTS.md` is the source of truth for
  the public surface; this file is the technique reference.
