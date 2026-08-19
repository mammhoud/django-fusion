# Wagtail Pages — Content Sections & i18n Summary

> Complete inventory of every Wagtail page model across both websites, the content sections each page exposes in the CMS, and the language configuration applied to all content.

**Date:** 2026-04-25
**Site:** Both (ctc-research.com · structa.cloud)
**Status:** Complete

---

## 1. Language Configuration

Both websites share an identical i18n setup defined in `configs/base/i18n.py`.

### Supported Languages

| Code | Language | Direction |
|---|---|---|
| `en` | English | LTR (default) |
| `fr` | French | LTR |
| `de` | German | LTR |
| `es` | Spanish | LTR |
| `ar` | العربيّة | **RTL** |

### Key Settings

| Setting | Value |
|---|---|
| `LANGUAGE_CODE` | `en` |
| `WAGTAIL_I18N_ENABLED` | `True` |
| `WAGTAIL_CONTENT_LANGUAGES` | all 5 languages above |
| `LANGUAGES_BIDI` | `["ar", "he", "fa", "ur"]` |
| `BILINGUAL_SUPPORT` | enabled, fallback → `en` |
| `AUTO_TRANSLATE` | `False` (manual translation) |
| Locale paths | `BASE_DIR/locale`, `assets/locale` |
| Cookie lifetime | 1 year |
| Cookie secure | `True` in production |

### Language Detection Order (per request)

URL path prefix → user profile → session → cookie → `Accept-Language` header

### Translation Backends

- `modeltranslation` — model-level field translations
- `parler` — multilingual model support
- `rosetta` — translation UI (development only)

---

## 2. Page Model Hierarchy

```
Page (Wagtail)
└── BasePage  (abstract — WagtailPageMixin, footer control, context injection)
    ├── BaseFormPage  (abstract — contact form, email notifications, styling)
    │   ├── HomePage
    │   └── ContactPage
    ├── BaseIndexPage  (abstract — pagination, header/CTA)
    │   ├── ServicesPage
    │   ├── TeamPage
    │   └── EventPage
    └── AboutPage
```

Blog pages live separately under `www/apps/models/blog/`:

```
Page (Wagtail)
├── BlogIndexPage  (RoutablePageMixin — listing, filtering, pagination)
└── BlogPage       (full article — authors, tags, SEO, analytics)
```

---

## 3. Page-by-Page Content Sections

### 3.1 HomePage

**Model:** `www/core/content/models/pages/home.py`
**Template:** `home/main.html` · fragment `home.main`
**Identical on both websites.**

#### Tabs in Wagtail Admin

| Tab | Purpose |
|---|---|
| Content | All StreamField sections below |
| Promote | SEO meta, slug |
| Form Settings | Contact form behaviour, email recipients |
| Settings | Footer visibility |

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Header** | `head` | **Slider** — one or more slides, each with: background image, subtitle (max 100 chars), title (max 200 chars), optional video URL |
| **Header** | `head` | **Features strip** — repeating feature cards: icon class, image, title, description |
| **Summary** | `summary` | **About block** — background image, years of experience, welcome text, main title, rich-text description, repeating service items (icon, title, description) |
| **Summary** | `summary` | **Listing section** — subtitle, title, repeating index-page references each with page chooser, icon class, description |
| **CTA** | `CTA` | **Contact card** — `ContactCardBlock` from ceptor-ai |
| **CTA** | `CTA` | **Why Choose Us** — subtitle, title, description, highlight text, bullet methods list, image, page-link button |
| **CTA** | `CTA` | **Clients** — repeating Organization snippet choosers |
| **Contact Form** | `contact_form` | Styled contact form block (inherited from `BaseFormPage`) |

---

### 3.2 AboutPage

**Model:** `www/core/content/models/pages/about.py`
**Template:** fragment `about.main`
**Identical on both websites.**

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Header** | `head` | Page title background image, page title text (max 200 chars), breadcrumb home text |
| **Facts & Testimonials** | `facts` | **About block** — background image, welcome text, main title, description, years of experience, rich-text experience description, optional video link, optional media gallery, repeating counters (icon class, number, label) |
| **Facts & Testimonials** | `facts` | **Testimonials block** — subtitle, title, background image, optional video URL, repeating testimonials (rich-text content, client photo, client name, client position) |
| **Facts & Testimonials** | `facts` | **Clients block** — repeating Organization snippet choosers |

---

### 3.3 ContactPage

**Model:** `www/core/content/models/pages/contact.py`
**Template:** `base_page.html` · fragment `contact.main`
**Identical on both websites.**

#### Tabs in Wagtail Admin

| Tab | Purpose |
|---|---|
| Content | All StreamField sections |
| Promote | SEO meta |
| Form Settings | Email recipients, success/error messages |
| Settings | Footer visibility |

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Header** | `head` | Page title background image, page title text, breadcrumb home text |
| **Contact Info** | `contact_info` | Subtitle (max 100), title (max 200), multi-line description |
| **Contact Form** | `contact_form` | Styled contact form block (inherited from `BaseFormPage`) |
| **Contact Details** | `contact_details` | Repeating detail items: icon class, label, value (address / phone / email) |
| **Map** | `map` | Embedded map block (Google Maps embed URL) |
| **FAQ** | `faq` | `FAQSectionBlock` from ceptor-ai — section title + repeating Q&A pairs |

---

### 3.4 ServicesPage

**Model:** `www/core/content/models/pages/services.py`
**Type:** Index page (inherits `BaseIndexPage`)

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Header** | `head` | Page title background, title, breadcrumb |
| **CTA** | `cta` | Optional call-to-action block |

Child pages (individual service pages) are listed automatically via pagination.

---

### 3.5 TeamPage

**Model:** `www/core/content/models/pages/team.py`
**Type:** Index page (inherits `BaseIndexPage`)

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Header** | `head` | Page title background, title, breadcrumb |
| **Team Members** | inline | Photo, name, position, social links (LinkedIn, Twitter, GitHub), skills list, bio rich text |

---

### 3.6 EventPage

**Model:** `www/core/content/models/pages/event.py`
**Type:** Index page stub (inherits `BaseIndexPage`)

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Header** | `head` | Page title background, title, breadcrumb |

> Event detail pages are planned but not yet implemented.

---

### 3.7 BlogIndexPage

**Model:** `www/apps/models/blog/post.py`
**Mixin:** `RoutablePageMixin` — provides `/tag/<slug>/`, `/author/<slug>/`, `/category/<slug>/` sub-routes

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Introduction** | `introduction` | Plain text intro shown above the listing |
| **Featured Posts** | `featured_posts` | Up to 3 manually chosen `BlogPage` choosers |
| **Header** | `head` | Optional page title background + breadcrumb |

Listing is auto-generated from child `BlogPage` instances with tag/author/category filtering and pagination.

---

### 3.8 BlogPage

**Model:** `www/apps/models/blog/post.py`

#### Content Sections

| Section | Field | Content |
|---|---|---|
| **Basic** | `subtitle` | Optional subtitle / tagline (max 255) |
| **Basic** | `introduction` | Plain-text intro for listing cards and SEO |
| **Basic** | `excerpt` | Rich-text brief summary |
| **Basic** | `featured_image` | Landscape image (1000–3000 px wide recommended) |
| **Basic** | `date` | Published date |
| **Body** | `body` | `BaseStreamBlock` — full article content (headings, paragraphs, images, embeds, code, quotes) |
| **Authors** | inline `BlogAuthor` | One or more authors with role and primary-author flag |
| **Tags** | `tags` | `ClusterTaggableManager` — free-form tags |
| **SEO** | `seo_title` | Override meta title |
| **SEO** | `search_description` | Meta description |
| **SEO** | `canonical_url` | Canonical URL override |
| **SEO** | `og_image` | Open Graph image |
| **Analytics** | `page_views` | Read-only view counter |
| **Analytics** | `reading_time` | Auto-calculated reading time (minutes) |

---

## 4. Shared Infrastructure

### BaseFormPage (abstract)

Both `HomePage` and `ContactPage` inherit from `BaseFormPage`, which adds:

| Field | Purpose |
|---|---|
| `contact_form` | `MinimalContactFormBlock` — styled form with HTMX submission |
| `form_style` | Visual style selector (default / card / minimal) |
| `success_message` | Shown after successful submission |
| `error_message` | Shown on validation failure |
| `notification_emails` | Comma-separated recipient list for new submissions |

Form submissions are stored in `ContactSubmission` (model in `www/core/content/models/contact.py`) with: form ID, page ID/title/URL, submitted JSON data, file data, IP address, user agent, referrer, processed flag, and internal notes.

### BasePage (abstract)

All pages inherit:

| Field | Purpose |
|---|---|
| `show_page_at_footer` | Toggle to include page in footer navigation |

Context always includes: active partners (from `Organization`), footer pages (locale-aware), services summary.

---

## 5. Website-Specific Differences

| Feature | ctc-research.com | structa.cloud |
|---|---|---|
| LMS pages | ✅ Course, Enrollment, Certificate pages | ⬜ Planned |
| Blog | ✅ Full BlogIndexPage + BlogPage | ✅ Full BlogIndexPage + BlogPage |
| Core pages | HomePage, About, Contact, Services, Team, Event | HomePage, About, Contact, Services, Team, Event |
| Language default | `en` | `en` |
| Languages | en, fr, de, es, ar | en, fr, de, es, ar |
| RTL support | ✅ Arabic | ✅ Arabic |
| Time zone (dev) | Africa/Cairo | Africa/Cairo |

---

## 6. Translation Coverage per Page

Every user-facing string in all page models uses `gettext_lazy(_)`. The following content requires translation in each of the 5 languages:

| Page | Translatable content |
|---|---|
| HomePage | Slider subtitles/titles, feature titles/descriptions, about text, service item titles, listing section titles, CTA text, why-choose-us bullets |
| AboutPage | Page title, about section text, counter labels, testimonial content, client section labels |
| ContactPage | Page title, contact info subtitle/title/description, detail labels, FAQ questions and answers |
| ServicesPage | Page title, breadcrumb, CTA text |
| TeamPage | Page title, member bios, position titles, skill labels |
| BlogIndexPage | Introduction text, section headings |
| BlogPage | Subtitle, introduction, excerpt, body content, author roles |

Translation files live in:
- `BASE_DIR/locale/<lang>/LC_MESSAGES/django.po`
- `assets/locale/<lang>/LC_MESSAGES/django.po`

---

## Related

- [Architecture Overview](../architecture/01_system_overview.md)
- [ctc-research.com Product Docs](../../ctc-research.com/PRODUCT.md)
- [structa.cloud README](../../structa.cloud/README.md)
