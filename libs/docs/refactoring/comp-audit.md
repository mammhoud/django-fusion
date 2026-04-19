# comp/ Directory Audit

**Date:** 2025
**Purpose:** Pre-migration audit for Phase 3 — moving comp/ to django-osoul
**Status:** Audit only — no files moved

---

## Summary

| Metric | Value |
|--------|-------|
| Total files in django-grep/comp/ | 124 |
| Total files in django-rseal/comp/ | 124 |
| Files unique to django-grep | 0 |
| Files unique to django-rseal | 0 |
| Files in both (identical content) | 94 |
| Files in both (different content) | 30 |

**Conclusion:** The two comp/ directories have exactly the same file structure. There are no unique files on either side — every file exists in both. 94 files are byte-for-byte identical. 30 files differ only in import paths or minor formatting.

---

## All Components — Location Table

All 124 files exist in both locations. The table below lists the relative paths within comp/:

### Root-level files

| File | In django-grep | In django-rseal | Status |
|------|---------------|-----------------|--------|
| `__init__.py` | ✅ | ✅ | Different |
| `_init.py` | ✅ | ✅ | Different |
| `apps.py` | ✅ | ✅ | Different |
| `conf.py` | ✅ | ✅ | Different |
| `manifest.py` | ✅ | ✅ | Identical |
| `options.py` | ✅ | ✅ | Identical |
| `params.py` | ✅ | ✅ | Identical |
| `staticfiles.py` | ✅ | ✅ | Different |
| `templates.py` | ✅ | ✅ | Different |
| `up.py` | ✅ | ✅ | Different |

### adapters/

| File | In django-grep | In django-rseal | Status |
|------|---------------|-----------------|--------|
| `adapters/__init__.py` | ✅ | ✅ | Identical |
| `adapters/base.py` | ✅ | ✅ | Identical |
| `adapters/main.py` | ✅ | ✅ | Identical |
| `adapters/test.py` | ✅ | ✅ | Identical |

### blocks/

| File | In django-grep | In django-rseal | Status |
|------|---------------|-----------------|--------|
| `blocks/__init__.py` | ✅ | ✅ | Identical |
| `blocks/base.py` | ✅ | ✅ | Identical |
| `blocks/mixins.py` | ✅ | ✅ | Identical |
| `blocks/streamBlocks.py` | ✅ | ✅ | Identical |
| `blocks/contact/__init__.py` | ✅ | ✅ | Identical |
| `blocks/contact/business_hours_block.html` | ✅ | ✅ | Identical |
| `blocks/contact/contact_profile.html` | ✅ | ✅ | Identical |
| `blocks/contact/contactCard.py` | ✅ | ✅ | Different |
| `blocks/contact/contactMethods.py` | ✅ | ✅ | Identical |
| `blocks/contact/form.py` | ✅ | ✅ | Identical |
| `blocks/contact/hours.py` | ✅ | ✅ | Identical |
| `blocks/contact/map_block.html` | ✅ | ✅ | Identical |
| `blocks/contact/map.py` | ✅ | ✅ | Identical |
| `blocks/contact/site_contact_settings.html` | ✅ | ✅ | Identical |
| `blocks/contact/socialLinks.py` | ✅ | ✅ | Identical |
| `blocks/contact/streamBlocks.py` | ✅ | ✅ | Identical |
| `blocks/contact/websiteLinks.py` | ✅ | ✅ | Different |
| `blocks/content/__init__.py` | ✅ | ✅ | Identical |
| `blocks/content/badge_block.html` | ✅ | ✅ | Identical |
| `blocks/content/block_quote.html` | ✅ | ✅ | Identical |
| `blocks/content/button_block.html` | ✅ | ✅ | Identical |
| `blocks/content/cta_block.html` | ✅ | ✅ | Identical |
| `blocks/content/cta.py` | ✅ | ✅ | Different |
| `blocks/content/embed_block.html` | ✅ | ✅ | Identical |
| `blocks/content/heading_block.html` | ✅ | ✅ | Identical |
| `blocks/content/heading.py` | ✅ | ✅ | Identical |
| `blocks/content/image_block.html` | ✅ | ✅ | Identical |
| `blocks/content/objectives.py` | ✅ | ✅ | Identical |
| `blocks/content/overview.py` | ✅ | ✅ | Different |
| `blocks/content/paragraph_block.html` | ✅ | ✅ | Identical |
| `blocks/content/paragraph.py` | ✅ | ✅ | Identical |
| `blocks/content/quote.py` | ✅ | ✅ | Identical |
| `blocks/content/table_block.html` | ✅ | ✅ | Identical |
| `blocks/content/title.py` | ✅ | ✅ | Identical |
| `blocks/content/typed_table.html` | ✅ | ✅ | Identical |
| `blocks/media/__init__.py` | ✅ | ✅ | Identical |
| `blocks/media/document.py` | ✅ | ✅ | Identical |
| `blocks/media/embed.py` | ✅ | ✅ | Identical |
| `blocks/media/gallery_item.html` | ✅ | ✅ | Identical |
| `blocks/media/gallery.html` | ✅ | ✅ | Identical |
| `blocks/media/gallery.py` | ✅ | ✅ | Different |
| `blocks/media/html.py` | ✅ | ✅ | Identical |
| `blocks/media/image_gallery.html` | ✅ | ✅ | Identical |
| `blocks/media/image_lite.html` | ✅ | ✅ | Identical |
| `blocks/media/image.html` | ✅ | ✅ | Identical |
| `blocks/media/image.py` | ✅ | ✅ | Different |
| `blocks/media/video_lite.html` | ✅ | ✅ | Identical |
| `blocks/media/video.html` | ✅ | ✅ | Identical |
| `blocks/media/video.py` | ✅ | ✅ | Different |
| `blocks/pages/__init__.py` | ✅ | ✅ | Identical |
| `blocks/pages/about.py` | ✅ | ✅ | Different |
| `blocks/pages/enhanced_about_section.html` | ✅ | ✅ | Identical |
| `blocks/pages/enhanced_team_member.html` | ✅ | ✅ | Identical |
| `blocks/pages/event_schedule_item.html` | ✅ | ✅ | Identical |
| `blocks/pages/event_speaker.html` | ✅ | ✅ | Identical |
| `blocks/pages/event.py` | ✅ | ✅ | Different |
| `blocks/pages/project.py` | ✅ | ✅ | Identical |
| `blocks/pages/services.py` | ✅ | ✅ | Identical |
| `blocks/pages/team.py` | ✅ | ✅ | Different |
| `blocks/pages/testimonial.py` | ✅ | ✅ | Identical |
| `blocks/partials/__init__.py` | ✅ | ✅ | Identical |
| `blocks/partials/button.py` | ✅ | ✅ | Identical |
| `blocks/partials/certification.py` | ✅ | ✅ | Identical |
| `blocks/partials/enhanced_table.html` | ✅ | ✅ | Identical |
| `blocks/partials/faq.py` | ✅ | ✅ | Identical |
| `blocks/partials/hero.py` | ✅ | ✅ | Identical |
| `blocks/partials/section.py` | ✅ | ✅ | Different |
| `blocks/partials/tables.py` | ✅ | ✅ | Different |
| `blocks/profile/__init__.py` | ✅ | ✅ | Identical |
| `blocks/profile/details.py` | ✅ | ✅ | Identical |
| `blocks/profile/info.py` | ✅ | ✅ | Identical |
| `blocks/profile/streamBlocks.py` | ✅ | ✅ | Different |
| `management/__init__.py` | ✅ | ✅ | Identical |
| `management/commands/__init__.py` | ✅ | ✅ | Identical |
| `management/commands/generate_asset_manifest.py` | ✅ | ✅ | Different |
| `plugins/__init__.py` | ✅ | ✅ | Identical |
| `plugins/hookspecs.py` | ✅ | ✅ | Different |
| `plugins/manager.py` | ✅ | ✅ | Different |
| `site/__init__.py` | ✅ | ✅ | Identical |
| `site/context.py` | ✅ | ✅ | Different |
| `site/notifications.py` | ✅ | ✅ | Different |
| `site/pageHandler.py` | ✅ | ✅ | Identical |
| `site/paginators.py` | ✅ | ✅ | Identical |
| `site/plugins.py` | ✅ | ✅ | Identical |
| `site/response.py` | ✅ | ✅ | Identical |
| `templatetags/__init__.py` | ✅ | ✅ | Identical |
| `templatetags/_typing.py` | ✅ | ✅ | Identical |
| `templatetags/apps.py` | ✅ | ✅ | Different |
| `templatetags/comp_tags.py` | ✅ | ✅ | Identical |
| `templatetags/components.py` | ✅ | ✅ | Identical |
| `templatetags/contentType.py` | ✅ | ✅ | Identical |
| `templatetags/embedBlocks.py` | ✅ | ✅ | Different |
| `templatetags/userRole.py` | ✅ | ✅ | Identical |
| `templatetags/components/__init__.py` | ✅ | ✅ | Identical |
| `templatetags/components/breadcrumbs.py` | ✅ | ✅ | Different |
| `templatetags/components/calender.py` | ✅ | ✅ | Identical |
| `templatetags/components/card.py` | ✅ | ✅ | Identical |
| `templatetags/components/field.py` | ✅ | ✅ | Identical |
| `templatetags/components/gallary.py` | ✅ | ✅ | Identical |
| `templatetags/components/menu.py` | ✅ | ✅ | Identical |
| `templatetags/components/modal.py` | ✅ | ✅ | Identical |
| `templatetags/components/notification.py` | ✅ | ✅ | Identical |
| `templatetags/components/price.py` | ✅ | ✅ | Identical |
| `templatetags/components/table.py` | ✅ | ✅ | Identical |
| `templatetags/tags/__init__.py` | ✅ | ✅ | Identical |
| `templatetags/tags/asset.py` | ✅ | ✅ | Different |
| `templatetags/tags/block.py` | ✅ | ✅ | Different |
| `templatetags/tags/prop.py` | ✅ | ✅ | Identical |
| `templatetags/tags/slot.py` | ✅ | ✅ | Identical |
| `templatetags/tags/var.py` | ✅ | ✅ | Identical |

---

## Duplicate Analysis — The 30 Different Files

All 30 "different" files have the **same line count** (or differ by 1–2 lines) and the **same logic**. The differences fall into three categories:

### Category A: Import path divergence (django_grep.* vs django_rseal.*)

These files are functionally identical but reference their own package's namespace. The rseal version is the canonical one since comp/ is moving to osoul (which will have its own namespace).

| File | grep imports | rseal imports | Notes |
|------|-------------|---------------|-------|
| `conf.py` | `django_grep.contrib.utils` | `django_rseal.contrib.utils` | Same logic |
| `_init.py` | `django_grep.comp.conf` | `django_rseal.comp.conf` | Same logic |
| `staticfiles.py` | `django_grep.comp.conf`, `django_grep.contrib` | `django_rseal.comp.conf`, `django_rseal.contrib` | Same logic |
| `templates.py` | `django_grep.comp.conf`, `django_grep.contrib` | `django_rseal.comp.conf`, `django_rseal.contrib` | Same logic |
| `management/commands/generate_asset_manifest.py` | `django_grep.comp.manifest` | `django_rseal.comp.manifest` | Same logic |
| `site/context.py` | `django_grep.contrib.context` | `django_rseal.contrib.context` | Same logic |
| `templatetags/tags/asset.py` | `django_grep.comp.manifest` | `django_rseal.comp.manifest` | Same logic |
| `templatetags/apps.py` | `django_rseal.routes.base` | `django_rseal.pipelines.routes.base` | rseal has updated path |
| `templatetags/components/breadcrumbs.py` | `django_rseal.routes.base` | `django_rseal.pipelines.routes.base` | rseal has updated path |

### Category B: Minor formatting / import ordering differences (same logic)

These files have identical logic but differ in import ordering, whitespace, or minor style:

| File | Difference | Winner |
|------|-----------|--------|
| `apps.py` | Import ordering | Equal (same logic) |
| `blocks/contact/contactCard.py` | Minor formatting | Equal |
| `blocks/contact/websiteLinks.py` | Minor formatting | Equal |
| `blocks/content/cta.py` | Minor formatting | Equal |
| `blocks/content/overview.py` | Minor formatting | Equal |
| `blocks/media/gallery.py` | Minor formatting | Equal |
| `blocks/media/image.py` | Minor formatting | Equal |
| `blocks/media/video.py` | Minor formatting | Equal |
| `blocks/pages/about.py` | Minor formatting | Equal |
| `blocks/pages/event.py` | Minor formatting | Equal |
| `blocks/pages/team.py` | Minor formatting | Equal |
| `blocks/partials/section.py` | Minor formatting | Equal |
| `blocks/partials/tables.py` | Minor formatting | Equal |
| `blocks/profile/streamBlocks.py` | Minor formatting | Equal |
| `plugins/hookspecs.py` | Minor formatting | Equal |
| `plugins/manager.py` | Minor formatting | Equal |
| `site/notifications.py` | Minor formatting | Equal |
| `templatetags/embedBlocks.py` | Minor formatting | Equal |
| `templatetags/tags/block.py` | Minor formatting | Equal |

### Category C: Special cases

| File | grep version | rseal version | Notes |
|------|-------------|---------------|-------|
| `__init__.py` | Deprecation shim: `from django_rseal.comp import *` with DeprecationWarning | `from pluggy import HookimplMarker; hookimpl = HookimplMarker(...)` | **rseal version is canonical** — grep's is just a compatibility shim |
| `up.py` | Has `# ruff: noqa: E402` header comment | No noqa comment | Equal logic; grep has extra noqa comment |

---

## Merge Strategy

Since there are **no unique files** on either side, the migration is straightforward:

### Decision: Use rseal version as the base for all files

**Rationale:**
1. `django-rseal` is the current canonical home of comp/ (grep's `__init__.py` already re-exports from rseal)
2. rseal's import paths (`django_rseal.pipelines.routes.base`) are more up-to-date than grep's (`django_rseal.routes.base`)
3. rseal's `__init__.py` has the real implementation; grep's is just a deprecation shim

### Per-file merge strategy

| File | Strategy | Action |
|------|----------|--------|
| `__init__.py` | Use rseal version | rseal has real implementation; grep has shim |
| `_init.py` | Use rseal version, update imports | Change `django_rseal.comp.conf` → `django_osoul.comp.conf` |
| `apps.py` | Use rseal version | Equal logic |
| `conf.py` | Use rseal version, update imports | Change `django_rseal.contrib.utils` → `django_osoul.contrib.utils` |
| `manifest.py` | Either (identical) | No import changes needed |
| `options.py` | Either (identical) | No import changes needed |
| `params.py` | Either (identical) | No import changes needed |
| `staticfiles.py` | Use rseal version, update imports | Change `django_rseal.comp.*` → `django_osoul.comp.*`, `django_rseal.contrib` → `django_osoul.contrib` |
| `templates.py` | Use rseal version, update imports | Same as staticfiles.py |
| `up.py` | Use rseal version | Equal logic; drop noqa comment |
| All `blocks/**` | Either (identical or equal logic) | No internal package imports to update |
| `management/commands/generate_asset_manifest.py` | Use rseal version, update imports | Change `django_rseal.comp.manifest` → `django_osoul.comp.manifest` |
| `plugins/hookspecs.py` | Either (equal logic) | No package imports |
| `plugins/manager.py` | Either (equal logic) | No package imports |
| `site/context.py` | Use rseal version, update imports | Change `django_rseal.contrib.context` → `django_osoul.contrib.context` |
| `site/notifications.py` | Either (equal logic) | No package imports |
| `site/pageHandler.py` | Either (identical) | No package imports |
| `site/paginators.py` | Either (identical) | No package imports |
| `site/plugins.py` | Either (identical) | No package imports |
| `site/response.py` | Either (identical) | No package imports |
| `templatetags/apps.py` | Use rseal version | rseal has updated `pipelines.routes.base` path |
| `templatetags/components/breadcrumbs.py` | Use rseal version | rseal has updated `pipelines.routes.base` path |
| `templatetags/tags/asset.py` | Use rseal version, update imports | Change `django_rseal.comp.manifest` → `django_osoul.comp.manifest` |
| `templatetags/tags/block.py` | Either (equal logic) | No package imports |
| All other `templatetags/**` | Either (identical) | No package imports |

---

## Imports That Will Need Updating After Migration

When comp/ moves to `django_osoul`, the following import patterns must be updated across the entire codebase:

### 1. Internal comp/ self-references (within comp/ files themselves)

These will be updated as part of the move:

| Old import | New import |
|-----------|-----------|
| `django_rseal.comp.conf` | `django_osoul.comp.conf` |
| `django_rseal.comp.manifest` | `django_osoul.comp.manifest` |
| `django_rseal.comp._init` | `django_osoul.comp._init` |
| `django_grep.comp.conf` | `django_osoul.comp.conf` |
| `django_grep.comp.manifest` | `django_osoul.comp.manifest` |
| `django_grep.comp._init` | `django_osoul.comp._init` |

### 2. External dependencies within comp/ (comp/ depends on contrib/)

These files inside comp/ import from `contrib/` — after migration, `contrib/` must also be in django-osoul or the imports updated:

| File | Imports from |
|------|-------------|
| `conf.py` | `django_rseal.contrib.utils` |
| `site/context.py` | `django_rseal.contrib.context` |
| `staticfiles.py` | `django_rseal.contrib` |
| `templates.py` | `django_rseal.contrib` |

**Action needed:** Verify `contrib/` is in django-osoul before moving comp/, or update these imports to point to wherever contrib/ ends up.

### 3. Files outside comp/ that import from comp/ (consumers)

These files in django-rseal's pipelines/ will need their imports updated from `django_rseal.comp.*` to `django_osoul.comp.*`:

| File | Imports |
|------|---------|
| `django-rseal/src/django_rseal/routes/model.py` | `django_rseal.comp.views.generic` |
| `django-rseal/src/django_rseal/pipelines/middlewares/site.py` | `django_rseal.comp.adapters`, `django_rseal.comp.site`, `django_rseal.comp.up` |
| `django-rseal/src/django_rseal/pipelines/routes/newsletter/subscription.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/search.py` | `django_rseal.comp.views.includes` |
| `django-rseal/src/django_rseal/pipelines/site/notifications.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/auth/login.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/auth/verification_link.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/auth/forget_password.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/auth/privacy.py` | `django_rseal.comp.site.pageHandler` |
| `django-rseal/src/django_rseal/pipelines/site/auth/mixins.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/auth/register.py` | `django_rseal.comp.site` |
| `django-rseal/src/django_rseal/pipelines/site/generic/__init__.py` | `django_rseal.comp.views.generic.*`, `django_rseal.comp.views.search` |
| `django-rseal/src/django_rseal/pipelines/site/generic/base.py` | `django_rseal.comp.forms.layout` |
| `django-rseal/src/django_rseal/pipelines/site/generic/create.py` | `django_rseal.comp.forms` |
| `django-rseal/src/django_rseal/pipelines/site/generic/update.py` | `django_rseal.comp.forms` |
| `django-rseal/src/django_rseal/pipelines/models/banner.py` | `django_rseal.comp.blocks.contact.socialLinks` |
| `django-rseal/src/django_rseal/pipelines/models/users/users.py` | `django_rseal.comp.blocks` |
| `django-rseal/src/django_rseal/pipelines/models/contacts/base.py` | `django_rseal.comp.blocks` |
| `django-rseal/src/django_rseal/pipelines/models/settings/settings.py` | `django_rseal.comp.blocks`, `django_rseal.comp.blocks.contact.*` |
| `django-rseal/src/django_rseal/pipelines/models/settings/newsletter.py` | `django_rseal.comp.blocks` |
| `django-rseal/src/django_rseal/pipelines/backends/__init__.py` | `django_rseal.comp.payloads.adapters.social` |

**Note:** Some of these imports reference modules not found in the current comp/ scan (e.g., `comp.views`, `comp.forms`, `comp.payloads`). These may be in a different location or not yet migrated.

### 4. templatetags/apps.py and breadcrumbs.py — Viewset import

Both files import `Viewset` from a routes module. After migration, this import path needs to be resolved:

| Current (grep) | Current (rseal) | After migration |
|---------------|-----------------|-----------------|
| `django_rseal.routes.base` | `django_rseal.pipelines.routes.base` | Keep `django_rseal.pipelines.routes.base` (rseal owns routes) |

This import should **stay pointing to django_rseal** even after comp/ moves to django_osoul, since `Viewset` is a routing concept that belongs in rseal.

---

## Pre-Migration Checklist

Before executing task 4.2 (the actual move), verify:

- [ ] `django_osoul` package exists at `libs/django-osoul/src/django_osoul/`
- [ ] `django_osoul.contrib` module exists (comp/ depends on it via `conf.py`, `staticfiles.py`, `templates.py`, `site/context.py`)
- [ ] `django_osoul` is listed as a dependency in django-rseal's `pyproject.toml`
- [ ] `django_osoul` is listed as a dependency in django-grep's `pyproject.toml`
- [ ] The `Viewset` class in `django_rseal.pipelines.routes.base` is accessible (used by templatetags)
- [ ] All 21 consumer files in django-rseal/pipelines/ are identified for import updates

---

## Notes

- The grep `comp/__init__.py` is already a deprecation shim that re-exports from `django_rseal.comp`. This confirms rseal is the authoritative source.
- The two directories are effectively mirrors of each other — the grep copy was likely created as a transitional duplicate and never diverged meaningfully.
- After migration, both `django_grep.comp` and `django_rseal.comp` should become thin compatibility shims pointing to `django_osoul.comp`, similar to what grep's `__init__.py` already does.
