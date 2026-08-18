# CTC Research — Publishing Workflow & Production Notes

> **Canonical project:** `projects/precis/precis-ctc/`
> **Public site:** `ctc-research.com`
> **Applies to:** blog posts, publications, courses/lessons, Wagtail pages, and
> translated copy.

<!-- AI-generated: review needed -->

## Bottom line

Publishing at CTC Research is a **two-track system**: editor-managed Wagtail
content (pages, snippets, publications) and seed-driven content (fixtures for
courses/curriculum). Both tracks converge on the same review gates — medical,
legal, and CTC-owner — and both must be reflected in the locale catalogs before
a translation is declared complete. Never ship a public claim without a source,
and never imply clinical advice from educational material.

---

## 1. Content tracks

| Track | Source of truth | Editable via | Example |
|---|---|---|---|
| **Wagtail pages** | `Page` tree (localized per locale) | Wagtail admin `/admin/` | About, Services, Events, Contact |
| **Wagtail snippets** | registered snippets | Wagtail admin | `Publication`, `PublicationCategory` |
| **Seed fixtures** | `backend/assets/fixtures/*.json` | `load_data` management command | `medical_research_courses.json`, `medical_research_curriculum.json`, `research_publications.json` |
| **Translations** | `assets/locale/<lang>/LC_MESSAGES/django.po` | `makemessages` → edit → `compilemessages` | UI strings and `_DOCUMENT_GUIDANCE` copy |

---

## 2. Publishing workflow (per piece)

### 2.1 Brief (before writing)

One paragraph that names: the persona (see
[`content-strategy.md`](content-strategy.md)), the job-to-be-done, the single
takeaway, and the target keyword/route. If no keyword and no persona, do not
start — this is the same gate as content-production's "vague topic" push-back.

### 2.2 Draft

Write against the medical-content rules in
[`../../projects/precis/precis-ctc/docs/CONTENTS.md`](../../projects/precis/precis-ctc/docs/CONTENTS.md):

1. Lead with the research question, population, method, evidence, outcome.
2. Every factual claim has a source or is labeled as opinion.
3. No invented statistics, trial results, patient claims, or approvals.

### 2.3 Review gates (blocking)

| Gate | Required for | Sign-off |
|---|---|---|
| **Medical review** | any clinical/methods claim | subject-matter expert |
| **Legal review** | ethics, privacy, publication claims | legal owner |
| **CTC owner review** | public positioning, pricing, marketing copy | product owner |
| **Linguistic review** | any non-English public copy | qualified speaker |

### 2.4 Publish

1. Add the content in Wagtail (page/snippet) **or** the fixture JSON.
2. If fixture-based, run the load command (see §4).
3. Rebuild assets if templates/styles changed: `make assets-full`.
4. Verify routes and API payloads (see §5).
5. Redeploy: `make redeploy` (or the dispatcher:
   `cd projects && make redeploy-with-stack WEBSITE=precis-ctc`).

---

## 3. Production notes

### 3.1 Publications (the research library)

- Model: `apps/content/models/publication.py` (`Publication`,
  `PublicationCategory`) — Wagtail snippets with `app_label = "pages"`.
- Migration: `apps/content/migrations/0008_publication.py`.
- Fixture: `backend/assets/fixtures/research_publications.json`
  (one `PublicationCategory` per research theme; multilingual `Publication`
  rows via the `language` field).
- Public API: `GET /apis/research/publications/` — see §5.

### 3.2 Courses & curriculum

- Course metadata: `backend/apps/learning/fixtures/medical_research_courses.json`.
- Modules/lessons: `backend/apps/learning/fixtures/medical_research_curriculum.json`
  (12 modules, 24 rich-text lessons across six published courses).
- Course copy is mostly English-only today; add editorial translations before
  declaring a course multilingual.

### 3.3 Multilingual copy

- Catalogs: `assets/locale/{en,sv,fr,de,es,ar,pt_BR}/LC_MESSAGES/django.po`.
- `sv`, `pt_BR` were rebuilt as full-set catalogs this pass; human review is
  still required before treating them as editorially complete.
- Compile after editing: `django-admin compilemessages` (run inside the backend
  environment), then verify the `.mo` is newer than the `.po`.

### 3.4 SEO + readability gates

- Title tag ≤ 60 chars with the primary keyword; meta description 150–160 chars.
- Readability ≥ 70 on the content scorer; paragraphs ≤ 4 sentences.
- 2–4 internal links: pillar guide ↔ matching course ↔ publication.
- Alt text on every microscopy/imaging/lab/event image.

---

## 4. Loading seed data

```bash
# Backend environment (fixtures are loaded by the management command, not raw loaddata)
cd projects/precis/precis-ctc/backend
make check

# Publication + course fixtures are wired through the load commands:
#   apps/core/management/commands/load_data.py          (pages, publications, site)
#   apps/learning/management/commands/load_course_fixtures.py  (courses, curriculum)
```

Do **not** run `--replace` against a shared/production database without explicit
approval (safety rule from the root `AGENTS.md`).

---

## 5. Verifying a piece after publish

```bash
# API contract (data road) — publications with filters
curl -sS 'http://localhost:5070/apis/research/publications/?lang=en&q=cohort&limit=10'
# Render-first HTML road (page)
curl -sS http://localhost:5070/apis/pages/about/
# HTMX fragment road
curl -sS http://localhost:5070/fragment/pages/about/
# OpenAPI docs (interactive) + raw spec
#   http://localhost:5070/apis/docs/
#   http://localhost:5070/apis/openapi.json
```

Filter parameters for `/apis/research/publications/`: `lang`, `q`, `category`,
`ordering` (`published_at`, `-published_at`, `title`, `-title`), `limit`,
`page`, `offset`. The endpoint contract is in
`backend/apps/pages/pages/landing_api.py`; the OpenAPI surface is defined in
`backend/apps/core/openapi.py`.

---

## Remarks & Notes

- The render-first / data-API / HTMX-fragment roads are **separate contracts**
  — do not substitute a JSON payload for a server-rendered fragment or vice
  versa. Details: [`../../projects/precis/precis-ctc/docs/CONTENTS.md`](../../projects/precis/precis-ctc/docs/CONTENTS.md)
  and [`LEARNING_CASES.md`](../../projects/precis/precis-ctc/docs/LEARNING_CASES.md).
- `backend/assets/fixtures/dump-data.json` is the canonical backend load source;
  `assets/fixtures/dump-data.json` is a historical/export copy — reconcile or
  explicitly label before publishing.
- Generated bundles (`projects/assets/bundles/ctc-research/`), collected static,
  and runtime media are different asset classes; follow
  [`ENVIRONMENT.md`](../../projects/precis/precis-ctc/docs/ENVIRONMENT.md) rather
  than copying one into another.
- Every public medical, legal, and research claim requires a sign-off; this
  document describes implementation state, not clinical validation.
