# Precis — Marketplace Publish Kit

> **Related Names:** `publish`, `ThemeForest`, `CodeCanyon`, `Gumroad`, `marketplace`, `listing`, `screenshots`, `pricing`
> **Tags:** `#publish` `#themeforest` `#marketplace` `#licensing` `#packaging`

Use this file when listing **Precis** products on any digital marketplace.
The canonical product lives in `projects/structa.cloud/` — merging precis-landing + precis-lms.
Statuses follow the product release board in [`docs/plans/README.md`](../../../docs/plans/README.md).

---

## Editions Available

| Edition | Contents | Status |
|---------|----------|--------|
| **Main** | Unified LMS courses/enrollment/progress/profile + landing marketing/catalog shell | ✅ done in code |
| **Landing** | Public marketing/catalog site; Astro frontend and Django/Wagtail backend | ✅ done in code |
| **CTC** | Medical research center site, standalone | ✅ done in code |

---

## Item Name

**Precis — Unified LMS & Landing Platform**

> Maximum 100 characters. No HTML or emoji.

---

## Short Description

Precis is a unified platform combining LMS course management, student enrollment & progress tracking, user profile management, and a marketing landing shell with catalog functionality. Built with Django/Wagtail, Astro, and django-fusion. Supports course creation, instructor workflows, and customer-facing catalog browsing.

---

## Visual Preview

Screenshots captured via headless Chromium.

### 1. Precis Landing — Homepage
![Precis Landing](../precis/landing/backend/assets/static/related/precis-landing-home.jpg)

### 2. Precis LMS — Course Dashboard
![Precis LMS Course Dashboard](../precis/landing/backend/assets/static/related/precis-lms-dashboard.jpg)

### 3. Precis LMS — Course Detail
![Precis LMS Course Detail](../precis/landing/backend/assets/static/related/precis-lms-course-detail.jpg)

### 4. Precis CTC — Research Center Site
![Precis CTC Site](../precis/ctc/backend/assets/static/related/prec-ctc-site.jpg)

---

## Key Features (for marketplace listing)

- Unified LMS + landing platform in one product
- Course creation, enrollment, and progress tracking
- Instructor and student role-based dashboards
- Marketing landing page with catalog browsing
- Django/Wagtail admin with Unfold interface
- Astro frontend with HTMX interactivity
- django-fusion fragments for reusable UI
- Multi-tenant capable (schema-per-tenant)
- Responsive design with light and dark mode
- i18n support (English, Arabic, French)
- REST API and WebSocket sync
- Backups, monitoring, and schema-per-tenant deployment

---

## Claim-Evidence Checklist (truth gate)

Every claim in a marketplace listing or public page must pass this gate before publish. It is the lightweight gate from Phase 0 of the [Product audit plan](../docs/plans/README.md).

- [ ] **Edition names are canonical.** Use Main, Landing, CTC. Do not use retired names.
- [ ] **Status is accurate.** `done in code` (implemented + locally tested) · `staging` (implemented, deployment pending). Never use "live" or "shipped" for code that has not been deployed and verified.
- [ ] **Every feature claim cites a code path.** Link the feature to its edition directory or plan file (`docs/plans/`), or label it explicitly as roadmap/planned.
- [ ] **No live demo target required.** Landing items may use static preview; LMS items require a functional demo host.
- [ ] **No external placeholder media.** Images come from the shared asset registry (`projects/assets/`) or approved brand photography. No `picsum.photos` or other external placeholders.
- [ ] **Real client/product names must not appear in samples.** Fictional-name rule + a grep gate; verify each fixture.
- [ ] **Fonts, icons, images, diagrams each carry their own licence.** Per-asset audit in the pack (`LICENSES.md`).
- [ ] **AGPL-derived blocks are excluded.** AGPL copyleft is incompatible with marketplace licence; exclude from publish set.

---

## Category & Attributes

| Field | Value |
|-------|-------|
| Category | Software Template / Education |
| High Resolution | Yes |
| Compatible Browsers | Chrome, Edge, Firefox, Safari |
| Compatible With | Django, Wagtail, Astro, HTMX, Tailwind, React |
| Files Included | TSX, TS, PY, JSON, SCSS, HTML, PNG, ICO |
| Layout | Responsive |
| Demo URL | https://structa.cloud |

---

## Tags (15 max for marketplace)

```
prec, lms, learning, course, education, landing, catalog, django, wagtail, astro, htmx, fusion, responsive, education
```

---

## Pricing Guidance

| License | Suggested Price |
|---------|-----------------|
| Regular License | $29 – $49 |
| Extended License | $200 – $300 |

---

## Message to Reviewer

All images, sounds, video, code, and other assets included in this item are either original work or appropriately licensed. This work is entirely my own and I have full rights to sell it on ThemeForest/CodeCanyon.

The product family ships 3 editions:
- **Main**: Unified LMS + Landing (course management + profile + catalog)
- **Landing**: Public marketing/catalog site only
- **CTC**: Standalone medical research center site

All source code is included, documented, and buildable from scratch.

---

## Licensing Notes

- Precis core code is under custom open-source license compatible with marketplace requirements
- django-fusion is under MIT license — compatible with marketplace sale
- Wagtail core and Django framework files are excluded from the publish set (framework, not authored work)
- Authored templates, components, and HTML are original work
- No AGPL-derived assets included in the publish package

---

## Effectful — confirm first

- Publishing is an external, money-affecting action. This milestone produces the pack and the notes; uploading, pricing, and submission stay operator actions requiring explicit confirmation.