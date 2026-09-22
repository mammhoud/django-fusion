# Locale Fixture Content Audit Report

> Date: 2026-07-31
> Source: `projects/precis-lms/backend/assets/fixtures/dump-data.json`
> Coverage: 6 locales × 7 page types = 42 pages

---

## 1. Locale Structure

| PK | Locale | Code |
|----|--------|------|
| 1 | English | `en` |
| 2 | French | `fr` |
| 3 | German | `de` |
| 4 | Spanish | `es` |
| 5 | Arabic | `ar` |
| 6 | Portuguese (Brazil) | `pt-br` |

✅ All 6 locales are properly defined in the `wagtailcore.locale` table.

---

## 2. Page Coverage by Locale

| Slug | en | fr | de | es | ar | pt-br |
|------|:--:|:--:|:--:|:--:|:--:|:----:|
| home | ✅ | ✅ (`home-fr`) | ✅ (`home-de`) | ✅ (`home-es`) | ✅ (`home-ar`) | ✅ (`home-pt-br`) |
| about | ✅ | ✅ | ✅ | ✅ | ✅ (`عن-سي-تي-سي-للبحث-العلمي`) | ✅ |
| team | ✅ | ✅ | ✅ | ✅ | ✅ (`فريقنا`) | ✅ |
| contact | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| services | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| all-courses | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| events | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ **All 7 page types exist in all 6 locales** — 42 pages total.  
✅ **Arabic uses Unicode slugs** (e.g., `فريقنا`, `عن-سي-تي-سي-للبحث-العلمي`).

---

## 3. Title Translation Status

### Fully Translated ✅

| Slug | Locales with proper translation |
|------|-------------------------------|
| about | **All 6**: English "About Fusion LMS", Arabic "عن سي تي سي للبحث العلمي", German "Über Fusion LMS", Spanish "Sobre Fusion LMS", French "À propos de Fusion LMS", Portuguese "Sobre a Fusion LMS" |
| team | **All 6**: English "Our Team", Arabic "فريقنا", German "Unser Team", Spanish "Nuestro Equipo", French "Notre équipe", Portuguese "Nossa Equipe" |
| contact | **All 6** |
| services | **All 6** |
| all-courses | **All 6** |
| events | **All 6** |

### Untranslated Titles ❌

**Critical:** The **homepage title** for 4 non-English locales falls back to English:

| Page | Locale | Title | Status |
|------|--------|-------|--------|
| home | `en` | "Home Page" | ✅ Correct |
| home | `ar` | "الصفحة الرئيسية" | ✅ Correct |
| home | `de` | **"Home Page"** | ❌ Should be German (e.g., "Startseite") |
| home | `es` | **"Home Page"** | ❌ Should be Spanish (e.g., "Página de inicio") |
| home | `fr` | **"Home Page"** | ❌ Should be French (e.g., "Page d'accueil") |
| home | `pt-br` | **"Home Page"** | ❌ Should be Portuguese (e.g., "Página inicial") |

---

## 4. Search Description Translation Status

✅ **Fully translated for all 6 locales** for every page. Examples:

| Locale | Homepage Search Description |
|--------|---------------------------|
| en | "Fusion LMS empowers medical professionals..." |
| ar | "تمكّن Fusion LMS الأطباء والباحثين من تس..." |
| de | "Fusion LMS befähigt medizinisches Fachpe..." |
| es | "Fusion LMS capacita a profesionales de l..." |
| fr | "Fusion LMS donne aux professionnels de s..." |
| pt-br | "A Fusion LMS capacita profissionais de s..." |

---

## 5. Hero Section Content (pages.homepage model)

All 6 homepage entries have **empty hero content**:

| Field | All locales |
|-------|------------|
| `hero_heading` | ❌ Empty (field doesn't exist in this model version) |
| `hero_subheading` | ❌ Empty |
| `head` | ✅ Present but minimal |
| `summary` | ✅ Present but minimal |
| `CTA` | ✅ Present but minimal |

The `pages.homepage` model (PK=3,8,13,18,23,28) uses these fields instead:
- `show_page_at_footer`, `form_background_color`, `form_text_color`, `form_button_color`, `form_button_text_color`, `contact_form`, `form_title`, `form_intro`, `button_text`, `success_message`, `error_message`, `head`, `summary`, `CTA`

The `hero_heading` / `hero_subheading` fields appear to have been **removed or renamed** in a model migration. The current model uses `head` and `summary` instead.

---

## 6. Course Fixtures — Locale Gap ❌

**All 8 courses are English-only:**

| PK | Title | Language | Featured |
|----|-------|----------|----------|
| 1 | Python Basics | `en` | ✅ |
| 2 | Django Web Development | `en` | ✅ |
| 3 | React.js Fundamentals | `en` | ✅ |
| 4 | Advanced Python | `en` | ❌ |
| 5 | Data Science with Python | `en` | ✅ |
| 6 | JavaScript ES6+ | `en` | ✅ |
| 7 | Full-Stack Web Development | `en` | ✅ |
| 8 | Mobile App Development with Flutter | `en` | ❌ |

The `language` field is `"en"` for all — **no translations** for fr, de, es, ar, or pt-br exist. Courses are not Wagtail-Translatable models (they don't use the locale tree), so translating them would require per-locale duplicate fixtures or a separate i18n approach.

---

## 7. Event Fixtures — Locale Gap ❌

**All 5 events are English-only** with no locale field at all:

| PK | Title | Type |
|----|-------|------|
| a1b2c3d4... | AI in Medical Writing Workshop | (empty) |
| b2c3d4e5... | Data-Driven Clinical Research Seminar | (empty) |
| c3d4e5f6... | Annual Medical AI Conference 2026 | (empty) |
| d4e5f6a7... | Peer Review Best Practices Webinar | (empty) |
| e5f6a7b8... | Medical Writers Meetup | (empty) |

The `type` field is also empty — likely a schema change mismatch in the fixture.

---

## 8. Specialization & Tags

From the fixture files:
- `specializations.json`: 5 specializations (Web Development, Data Science, etc.) — English only
- `course_tags.json`: 12 tags — English only

---

## 9. Summary of Gaps Found

| # | Gap | Impact | Severity |
|---|-----|--------|----------|
| 1 | **4 of 6 homepage titles fall back to English** | Homepage shows "Home Page" in German, French, Spanish, Portuguese | 🔴 High — User-facing |
| 2 | **Hero heading/subheading fields empty** | All 6 homepage hero sections have no heading content | 🔴 High — User-facing |
| 3 | **Course fixtures: English only** | Courses page shows only English course names for all locales | 🟡 Medium |
| 4 | **Event fixtures: English only + no type** | Events page shows only English titles; `type` field empty | 🟡 Medium |
| 5 | **Specializations & tags: English only** | Filter options display in English for all locales | 🟢 Low |
| 6 | **Search descriptions: fully translated** | ✅ No issue — actually a strength | ✅ |
| 7 | **About/team/contact/services/events/courses pages: all translated** | ✅ All non-homepage titles and descriptions are translated | ✅ |

---

## 10. Recommended Fixes

### P0: Fix Homepage Titles for de/es/fr/pt-br

In `dump-data.json`, update the `title` field for these 4 pages:

```json
// PK=13 (slug=home-de): "Home Page" → "Startseite"
// PK=18 (slug=home-es): "Home Page" → "Página de inicio"
// PK=23 (slug=home-fr): "Home Page" → "Page d'accueil"
// PK=28 (slug=home-pt-br): "Home Page" → "Página inicial"
```

### P1: Add Hero Section Content

The home pages need `head` and `summary` fields populated. Current values are "Build Skills" / descriptive text with no locale variation. Each locale should have its own localized version.

### P2: Course Translations

Since the Course model has a `language` field but isn't Wagtail-translatable, add duplicate course entries for each locale with translated titles and set `language` appropriately.

### P2: Event Fixture Fix

The event fixtures have a UUID PK format but the `type` field is empty. These need to be either:
- Fixed with proper `type` values (workshop, seminar, conference, webinar, meetup)
- Or re-exported from the actual Wagtail model to match the current schema

---

## 11. Audit Data Source

All data was extracted programmatically from:
- `backend/assets/fixtures/dump-data.json` (178 entries, 12 model types)
- `backend/apps/pages/lms/fixtures/courses.json` (8 courses)
- `backend/apps/pages/lms/fixtures/events.json` (5 events)
- `backend/apps/pages/lms/fixtures/specializations.json` (5 specs)
- `backend/apps/pages/lms/fixtures/course_tags.json` (12 tags)
