# CTC Research — Content Map

> **Canonical project:** `projects/precis/precis-ctc/`
> **Public site:** `ctc-research.com`
> **Runtime:** Astro 5 frontend + Django/Wagtail backend

<!-- AI-generated: review needed -->

This document maps the current public content surface and identifies the source
of truth for each part of the site. CTC Research is a medical research and
professional-learning site; visitor-facing pages should prefer evidence,
research context, investigator profiles, publications, events, and media over
software demonstrations or source-code panels.

## 1. Rendering model

```text
Browser
  ├─ Astro page shell and layout
  ├─ build-time/API catalog data
  └─ Django/Wagtail render-first and JSON/fragment roads
       ├─ landing_api.py — page, navigation, gallery, team, event data
       ├─ apps/learning — course catalog, enrollment, progress, profile
       └─ Wagtail page/image records — editor-managed content and media
```

The Astro frontend is located at `frontend/src/`. Backend contracts are owned
by `backend/apps/pages/pages/landing_api.py` and the learning app. Preserve the
existing render-first/data-API contract when adding content: a server-rendered
HTML response, an HTMX fragment, and an Astro JSON response are separate roads,
not interchangeable mock data.

## 2. Public page map

| Route | Primary content | Source and fallback |
|---|---|---|
| `/` | Research-center positioning, hero, outcomes, featured services, courses, events, CTA, medical evidence gallery | Localized home page from the landing API; seeded gallery media is the visual fallback |
| `/about/` | Mission, research priorities, team context, gallery, institutional story | Localized Wagtail About page; gallery media is passed to the reusable `MediaGallery` |
| `/services/` | Research support, education, evidence, analytics, and collaboration services | Localized page blocks; no hardcoded contact details |
| `/features/` | Platform capabilities framed as research workflows and learning outcomes | Localized page data and reusable feature blocks |
| `/projects/` | Research/project portfolio and outcome cards | Localized Wagtail content; media cards are preferred over code samples |
| `/products/` | Medical learning products and catalog entry points | Learning/catalog API with safe seeded fallbacks |
| `/products/[slug]/` | Product/course detail, outcomes, audience, enrollment CTA, media/reference gallery | Product API; the former “Models & snippets” code panel is now a medical media gallery |
| `/courses/` | Course catalog and filters | `apps/learning` catalog API and fixture data |
| `/courses/[slug]/` | Course detail, modules, lessons, enrollment, progress | `apps/learning`; seeded baseline is `medical_research_curriculum.json`, followed by editorial/Wagtail review |
| `/team/` | Investigator, educator, and operational profiles | Localized Team page and Wagtail image records |
| `/events/` | Seminars, workshops, research events, registration information | Localized Events page and event records |
| `/blog/` | Research notes, announcements, education articles | Blog API/page records |
| `/blog/[slug]/` | Article body, metadata, comments, share controls | Localized blog page; `ShareButtons` uses the page URL/title/text at runtime |
| `/contact/` | Contact methods and editor-managed form fields | Localized Contact page; `ContactForm` posts to the backend fragment endpoint |
| `/faq/` | Research, course, enrollment, and platform questions | Localized FAQ items; interactive search is Alpine-managed |
| `/pricing/` | Plans, access model, and enrollment CTAs | Localized pricing content; use medical-learning language rather than generic SaaS copy |
| `/profile/` | Authenticated learning state, next action, certificates, and progress | Headless allauth session + learning API |
| `/privacy/` | Privacy and data-use information | Legal content; review before production publication |
| `404` | Recovery navigation and site search/return paths | Static fallback |

## 3. Reusable frontend components

### Content blocks

- `Hero.astro` — positioning, primary/secondary CTA, and medical evidence panel.
  It no longer exposes a “View Source” code panel.
- `MediaGallery.astro` — responsive medical media grid with captions, source
  labels, and a native lightbox dialog.
- `OutcomeFramework.astro` — research/learning outcomes.
- `Features.astro` — capability and workflow cards.
- `Stats.astro` — impact and participation metrics.
- `Timeline.astro` — milestones, programs, and research stages.
- `TeamSection.astro` — people and roles.
- `Testimonials.astro` — participant or partner evidence.
- `FAQ.astro` — searchable questions.
- `CTA.astro` — conversion/action section.
- `ContactForm.astro` — backend-driven fields and contact methods.

### UI and integration components

- `Layout.astro` — SEO, locale, global scripts, navigation, toast, and auth shell.
- `LoginModal.astro` — django-allauth headless session/login integration.
- `ShareButtons.astro` — native share, network links, and copy-link behavior.
- `Modal.astro`, `BackToTop.astro`, `RenderModeSwitch.astro` — Alpine UI helpers.
- `LiveFragment.astro` and `LiveFragmentTarget.astro` — render-first/fragment bridges.
- `SkeletonBridge.astro` — backend skeleton/asset contract.

The unused `CodeBlock.astro` component was removed. Developer-only templates
under `assets/templates/examples/`, admin surfaces, and error diagnostics may
still contain code-oriented markup; those are not public medical content.

## 4. Data and fixture sources

| Source | Contents | Publish note |
|---|---|---|
| `backend/assets/fixtures/dump-data.json` | Wagtail pages, locales, images, renditions, subscriptions, site | Canonical backend load source; do not use `--replace` against shared production data without approval |
| `assets/fixtures/dump-data.json` | Historical/export copy | Reconcile or explicitly label before publishing |
| `backend/apps/learning/fixtures/medical_research_catalog.json` | Courses, tags, specializations | Course metadata and research-focused descriptions |
| `backend/apps/learning/fixtures/medical_research_curriculum.json` | 12 modules and 24 rich-text lessons across the six published courses | No code-block content; review medical/editorial copy before release |
| `assets/locale/*/LC_MESSAGES/django.po` | Django UI translations | `en`, `fr`, `de`, `ar` are existing references; `es`, `sv`, `pt_BR` are generated full-set catalogs |
| `projects/assets/media/ctc-research/` | Shared runtime media and Wagtail image files | Shared proxy and CTC containers use this project-named tree |
| `projects/assets/bundles/ctc-research/` | Shared webpack output and `bundles.json` | Generated; build before collectstatic or container rebuild |

## 5. Medical content rules

1. Lead with the research question, population, method, evidence, and outcome.
2. Label educational material clearly; do not imply clinical advice or patient-specific diagnosis.
3. Identify authors, affiliations, dates, review status, citations, and funding where available.
4. Use meaningful captions and alt text for microscopy, imaging, laboratory, and event media.
5. Prefer a media gallery, evidence card, chart, protocol summary, or publication card over source code.
6. Keep translations semantically reviewed by a qualified speaker before public release.
7. Avoid invented statistics, trial results, patient claims, or regulatory approvals.

## Remarks & Notes

- The generated locale catalogs contain the complete reference message set, but their build summary reports exact, pattern, and English-fallback entries. Human linguistic review is still required before declaring each locale editorially complete.
- The fixture audit found six localized page sets. The course catalog now has a seeded module/lesson hierarchy, but course copy remains mostly English-only and needs editorial translation review.
- Public medical copy, legal copy, and research claims require CTC subject-matter-owner review; this document describes implementation state, not clinical validation.
