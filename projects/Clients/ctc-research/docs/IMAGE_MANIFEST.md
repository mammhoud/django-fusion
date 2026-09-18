# CTC Research — Image Manifest

> **Canonical project:** `projects/precis/precis-ctc/`
> **Public identity:** `ctc-research.com` · **Runtime identity:** `precis-ctc`

Complete inventory of every seeded image in the project. All paths are relative to
`projects/precis/precis-ctc/`. Static images are collected into `assets/staticfiles/`
and served under `/static/images/` on `ctc-research.com`.

---

## 🕯️ Brand & Logo

| File | Size | Dimensions | Usage |
|---|---|---|---|
| `assets/static/images/logo.png` | 439 KB | 640×640 | **Primary site logo** — CANDLE TRAINING & RESEARCH CENTRE circular emblem. Used in all Django templates referencing `/static/images/logo.png`. Placed 2026-08-24 from the client-provided `ctc-research.logo.jpeg` (source, repo root). |
| `assets/static/images/brand/logo.png` | 439 KB | 640×640 | Copy of primary logo in the brand directory. |
| `assets/static/images/favicon.png` | 62 KB | 192×192 | Favicon — resized from primary logo. Referenced as `<link rel="shortcut icon" href="/static/images/favicon.png">` in all skeleton templates. |
| `assets/static/images/logo-enhanced.svg` | 0.9 KB | — | SVG variant (legacy; should be updated to match CTRC logo). |
| `assets/static/images/favicon-enhanced.svg` | 0.5 KB | — | SVG favicon variant (legacy). |
| `assets/static/images/brand/precis-logo-lockup.svg` | 2.2 KB | — | Precis wordmark lockup (shared brand asset). |
| `assets/static/images/brand/precis-protocol-mark.svg` | 2.5 KB | — | Precis protocol icon mark. |
| `assets/static/images/brand/structa-cloud-mark.svg` | 4.3 KB | — | Structa Cloud parent brand mark. |
| `assets/static/images/brand/logo-email.svg` | 1.8 KB | — | Email template logo. |
| `assets/static/images/brand/logo-error.svg` | 1.4 KB | — | Error page logo. |
| `assets/static/images/brand/logo-login.svg` | 2.3 KB | — | Auth/login page logo. |
| `frontend/public/static/images/ctc-logo.png` | 439 KB | 640×640 | Astro frontend logo (copied from primary logo). |
| `frontend/public/favicon.png` | 62 KB | 192×192 | Frontend favicon. |

### Logo design

The CANDLE TRAINING & RESEARCH CENTRE (CTRC) logo is a circular emblem with:

- **Outer ring:** Dark blue band with "CANDLE TRAINING & RESEARCH CENTRE" (English, top) and "مركز كاندل للتدريب والبحوث" (Arabic, bottom) with gold five-pointed stars and blue laurel wreaths.
- **Inner circle:** Dashed border enclosing a lit candle with yellow-orange flame, an open book with white pages and a science/atom graphic on the left page, and the acronym "CTRC" at the bottom.
- **Primary palette:** Dark blue `#0b2341`, orange-brown `#d97736`, yellow/gold `#f4b41a`.
- **Source file:** `ctc-research.logo.jpeg` (repo root, 640×640 JPEG, 65 KB).

---

## 🎨 LMS / CRM Brand SVGs

| File | Size | Usage |
|---|---|---|
| `assets/static/images/brand/crm-isometric.svg` | 2.9 KB | CRM isometric illustration. |
| `assets/static/images/brand/crm-isometric-enhanced.svg` | 0.5 KB | Enhanced CRM isometric (simplified). |
| `assets/static/images/brand/lms-ribbon.svg` | 3.0 KB | LMS ribbon badge. |
| `assets/static/images/brand/lms-ribbon-enhanced.svg` | 0.7 KB | Enhanced LMS ribbon. |
| `assets/static/images/brand/pos-crest.svg` | 3.7 KB | POS crest (original). |
| `assets/static/images/brand/pos-crest-static.svg` | 1.5 KB | POS crest static variant. |
| `assets/static/images/brand/pos-crest-enhanced.svg` | 0.7 KB | POS crest enhanced variant. |

---

## 📚 Content & Page Images

| File | Size | Dimensions | Source |
|---|---|---|---|
| `assets/static/images/auth-bg-default.jpg` | 1.0 MB | — | Default auth page background. |
| `assets/static/images/coming-soon.jpg` | 768 KB | — | Coming soon / maintenance page. |
| `assets/static/images/default-avatar.jpg` | 21 KB | — | Default user avatar for profile, courses, comments. |
| `assets/static/images/default-course.jpg` | 768 KB | — | Default course thumbnail when none is uploaded. |
| `assets/static/images/loader.svg` | 1.1 KB | — | Loading spinner SVG. |
| `assets/static/images/about/ab-pattern.png` | 60 KB | — | About section background pattern. |

---

## 🎭 Background Patterns

| File | Size | Usage |
|---|---|---|
| `assets/static/images/backgrounds/pattern.jpg` | 290 KB | Primary background pattern. |
| `assets/static/images/backgrounds/pattern-2.jpg` | 46 KB | Background pattern variant 2. |
| `assets/static/images/backgrounds/pattern-3.jpg` | 56 KB | Background pattern variant 3. |
| `assets/static/images/backgrounds/pattern-4.jpg` | 64 KB | Background pattern variant 4. |

---

## 🧩 Element Illustrations (SVG, 50+ files)

All under `assets/static/images/element/`. These are purpose-built SVG illustrations from
the Eduport LMS template used on category cards, course landing pages, and feature sections.

### Category & Subject

| File | Size | Topic |
|---|---|---|
| `element/category-1.svg` | 47 KB | Development / Coding |
| `element/category-2.svg` | 43 KB | Design |
| `element/abc.svg` | 5.0 KB | Language / Literacy |
| `element/coding.svg` | 7.7 KB | Programming |
| `element/data-science.svg` | 8.3 KB | Data Science |
| `element/engineering.svg` | 5.3 KB | Engineering |
| `element/medical.svg` | 11 KB | Medical / Health |
| `element/photography.svg` | 16.6 KB | Photography |
| `element/marketing.svg` | 13 KB | Marketing |
| `element/music.svg` | 9.6 KB | Music |
| `element/online.svg` | 11.3 KB | Online learning |
| `element/sport.svg` | 14.2 KB | Sports |
| `element/artist.svg` | 6.5 KB | Arts |
| `element/child.svg` | 7.7 KB | Early education |
| `element/lego.svg` | 10.4 KB | LEGO / Construction |

### Feature & UI

| File | Size | Purpose |
|---|---|---|
| `element/01.svg` through `element/30.svg` | Various | Generic feature illustrations (30 files, 2–493 KB). |
| `element/home.svg` | 6.4 KB | Home/dashboard. |
| `element/account.svg` | 5.3 KB | User account. |
| `element/cart.svg` | 6.7 KB | Shopping cart. |
| `element/contact.svg` | 43 KB | Contact form. |
| `element/exam.svg` | 29.5 KB | Exam / quiz. |
| `element/hand.svg` | 6.0 KB | Hand / gesture. |
| `element/help.svg` | 21 KB | Help / support. |
| `element/help-center.svg` | 158 KB | Help center. |
| `element/idea.svg` | 9.8 KB | Idea / innovation. |
| `element/rocket.svg` | 28.3 KB | Launch / rocket. |
| `element/earn-money.svg` | 56 KB | Earnings. |
| `element/profit.svg` | 7.1 KB | Profit / revenue. |
| `element/medal.svg` | 27 KB | Achievement / medal. |
| `element/medal-badge.png` | 1.2 KB | Medal badge (PNG, small). |
| `element/gallery.svg` | 1.9 KB | Gallery. |
| `element/map.svg` | 453 KB | Map illustration. |
| `element/coming-soon.svg` | 91 KB | Coming soon. |
| `element/error404-01.svg` | 74 KB | 404 error illustration. |
| `element/create-account.svg` | 29 KB | Registration / signup. |
| `element/instructor-course.svg` | 95 KB | Instructor dashboard. |
| `element/add-course.svg` | 22 KB | Add course. |

### Education Levels

| File | Size | Topic |
|---|---|---|
| `element/primary-school.svg` | 6.6 KB | Primary school. |
| `element/middle-school.svg` | 36 KB | Middle school. |
| `element/high-school.svg` | 174 KB | High school. |

---

## 🖼️ Image Usage Patterns

| Template path | Image referenced | Purpose |
|---|---|---|
| `templates/account/login.html` | `/static/images/favicon.png` | Browser tab icon |
| `templates/account/login.html` | `/static/images/brand/logo-login.svg` | Auth page brand visual |
| `templates/learning/course.html` | Default / Wagtail image | Course hero background |
| Blog templates | `assets/img/logo/logo.png` | Legacy blog template logo (pre-Wagtail migration) |
| `frontend/` Astro shell | `static/images/ctc-logo.png` | Astro-rendered shell pages |

---

## 🔧 Update Log

| Date | Change | Who |
|---|---|---|
| 2026-08-24 | Replaced `logo.png` and `favicon.png` with CTRC circular emblem from `ctc-research.logo.jpeg`; placed copy in `brand/` and frontend `public/`. | Codebuff |
| 2026-07-26 | Initial images seeded from Eduport LMS theme. | — |
| 2026-08-07 | Added auth-bg-default, avatar, backgrounds, element SVGs. | — |
| 2026-08-18 | Added brand/enhanced SVGs, favicon-enhanced, logo-enhanced. | — |
| 2026-08-22 | Added brand/pos-crest*, lms-ribbon*, logo-email, logo-error, logo-login. | — |

---

## 🚀 Deployment Notes

After adding or updating any asset in `assets/static/`:

```bash
cd projects/precis/precis-ctc/backend
make collectstatic        # copies to assets/staticfiles/
```

Docker containers pick up changes immediately via bind mounts. No rebuild required for
static image changes.

---

## 📂 Directory Map

```
assets/static/images/
├── logo.png                    ← 🔥 PRIMARY LOGO (CTRC circular emblem, 640×640)
├── favicon.png                 ← 🔥 FAVICON (192×192, resized from logo)
├── logo-enhanced.svg           ← Legacy SVG (update pending)
├── favicon-enhanced.svg        ← Legacy SVG favicon
├── loader.svg                  ← Loading spinner
├── auth-bg-default.jpg         ← Auth page background
├── coming-soon.jpg             ← Maintenance page
├── default-avatar.jpg          ← Fallback user avatar
├── default-course.jpg          ← Fallback course thumbnail
├── about/
│   └── ab-pattern.png          ← About section pattern
├── avatar/
│   └── 01.jpg                  ← Sample avatar
├── backgrounds/
│   ├── pattern.jpg             ← Primary background
│   ├── pattern-2.jpg
│   ├── pattern-3.jpg
│   └── pattern-4.jpg
├── brand/
│   ├── logo.png                ← Logo copy
│   ├── logo-email.svg
│   ├── logo-error.svg
│   ├── logo-login.svg
│   ├── crm-isometric.svg / enhanced
│   ├── lms-ribbon.svg / enhanced
│   ├── pos-crest.svg / static / enhanced
│   ├── precis-logo-lockup.svg
│   ├── precis-protocol-mark.svg
│   └── structa-cloud-mark.svg
└── element/                    ← 50+ Eduport LMS SVG illustrations
    ├── 01–30.svg               ← Generic feature
    ├── category-*.svg           ← Course categories
    ├── abc.svg                  ← Language
    ├── coding.svg              ← Programming
    ├── data-science.svg
    ├── engineering.svg
    ├── medical.svg
    ├── photography.svg
    ├── marketing.svg
    ├── music.svg
    ├── online.svg              ← Online learning
    ├── sport.svg
    ├── artist.svg
    ├── child.svg
    ├── lego.svg
    ├── primary-school.svg
    ├── middle-school.svg
    ├── high-school.svg
    ├── home.svg / account.svg / cart.svg
    ├── contact.svg / exam.svg / help.svg / help-center.svg
    ├── idea.svg / rocket.svg / earn-money.svg / profit.svg
    ├── medal.svg / medal-badge.png
    ├── gallery.svg / map.svg
    ├── coming-soon.svg
    ├── error404-01.svg
    ├── create-account.svg
    ├── instructor-course.svg
    └── add-course.svg
```

---

## 🤖 Generated with Codebuff

*Last updated: 2026-08-24*