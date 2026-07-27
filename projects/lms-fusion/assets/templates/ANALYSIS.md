# 📊 Templates Usage Analysis

**Path:** `projects/assets/templates/`
**Status:** ✅ Active — used by all projects via `TEMPLATES_DIRS`

---

## Overview

Shared Django/Wagtail templates used across all Structa Cloud projects. Configured in `projects/configs/base/templates.py` via `BASE_DIR.parent / "assets" / "templates"`.

---

## Directory Usage

| Directory / File | Used By | Notes |
|-----------------|---------|-------|
| `base.html` | **All projects** | Root layout — extended by all sites. Can be overridden per-site. |
| `base_auth.html` | **All projects** | Auth layout wrapper. |
| `base_email.html` | **All projects** | Email base template. |
| `base_profile.html` | **All projects** | Profile page layout. |
| `index.html` | **All projects** | Homepage template. |
| `robots.txt` | **All projects** | Robots exclusion rules. |

### Auth Templates

| File | Used By | Notes |
|------|---------|-------|
| `auth/` | **All projects** | Auth page templates (login, register, password reset, etc.) |
| `registration/` | **All projects** | Registration form fragments |
| `socialaccount/` | **All projects** | Social account templates |
| `account/` | **All projects** | allauth override templates |
| `usersessions/` | **All projects** | Active sessions list |

### Layout Templates

| File | Used By | Notes |
|------|---------|-------|
| `layout/auth/` | **All projects** | Auth page skeleton |
| `layout/landing/` | **All projects** | Landing page structure (skeleton, footer, meta) |
| `layout/learning/` | **All projects** | Learning module layout (skeleton, navigation, header, meta) |
| `layout/apps/` | **All projects** | App-level layout (meta, profile) |
| `layout/profile/` | **All projects** | Profile page layout (skeleton, meta, enrollment, payment) |
| `layout/forms/` | **All projects** | Form layout (skeleton, field) |
| `layout/navigation/` | **All projects** | Navigation components (side_nav, top_nav) |
| `layout/headers/` | **All projects** | Header breadcrumbs |

### Component Templates

| File | Used By | Notes |
|------|---------|-------|
| `components/chat/` | **All projects** | Chat bubble component |
| `components/cookies/` | **All projects** | Cookie consent, policy, privacy components |
| `components/form/` | **All projects** | Form rendering (form, form_field, form_block, form_simple) |
| `components/modal/` | **All projects** | Modal dialog components |
| `components/pagination/` | **All projects** | Pagination (numbers, htmx_pagination, infinite, load_more) |

### Block Templates

| File | Used By | Notes |
|------|---------|-------|
| `blocks/media/` | **All projects** | Media blocks (image, video, gallery, image_lite, video_lite, etc.) |
| `blocks/content/` | **All projects** | Content blocks (paragraph, heading, button, cta, block_quote, table, embed, badge, typed_table) |
| `blocks/pages/` | **All projects** | Page blocks (event_schedule_item, event_speaker, enhanced_team_member, enhanced_about_section) |
| `blocks/contact/` | **All projects** | Contact blocks (business_hours, map, contact_profile, site_contact_settings) |
| `blocks/partials/` | **All projects** | Partial blocks (enhanced_table) |

### Plugin Templates

| File | Used By | Notes |
|------|---------|-------|
| `plugins/certifications/` | **All projects** | Certificate display templates |
| `plugins/errors/` | **All projects** | Error pages (400, 401, 403, 404, 429, 500, 502, 503, 504, nxx) |
| `plugins/search/` | **All projects** | Search bar |
| `plugins/privacy/` | **All projects** | Privacy/consent templates |
| `plugins/base/` | **All projects** | Base fragments (loader, error, confirm, fragment, validation) |
| `plugins/tables/` | **All projects** | Table rendering |
| `plugins/newsletter/` | **All projects** | Newsletter subscribe/preview templates |
| `plugins/notifications/` | **All projects** | Notification display templates |
| `plugins/courses/` | **All projects** | Course catalog and filter templates |

### Other Templates

| File | Used By | Notes |
|------|---------|-------|
| `emails/` | **All projects** | Email templates (welcome, enrollment, password_reset, invitation, contact, newsletter, test, etc.) |
| `events/` | **All projects** | Event listing and detail templates |
| `wagtailadmin/` | **All projects** | Wagtail admin overrides (login, base, nav, header, panels) |
| `wagtailcore/` | **All projects** | Page base template |
| `ui/` | **All projects** | UI base wrappers (base_page, base_auth) |
| `partials/` | **All projects** | Reusable partials (header_links, logo, auth_buttons, meta, language_selector, announcement_banner, etc.) |
| `generic/` | **All projects** | Generic CRUD templates (_confirm_delete, _detail, _form, _list, button) |
| `content/` | **All projects** | Content components (media/gallery, page_title) |
