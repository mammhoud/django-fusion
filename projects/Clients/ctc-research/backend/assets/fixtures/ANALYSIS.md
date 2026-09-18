# 📊 Fixtures Usage Analysis

**Path:** `projects/assets/fixtures/`
**Status:** ✅ Active — used by all projects via `FIXTURE_DIRS`

---

## Overview

Database fixtures for seeding application data. Configured in `projects/configs/base/assets.py` via `FIXTURE_DIRS`.

---

## Directory Structure

```
fixtures/
├── events.json                         # Sample event data for events app
├── README.md                           # Fixture documentation
├── auth/                               # Auth-related fixtures
│   ├── group_dummy.json                # Dummy groups
│   └── user_dummy.json                 # Dummy users
├── by-model/                           # Fixtures organized by Django app model
│   ├── README.md                       # By-model fixture documentation
│   ├── INDEX.json                      # Fixture index
│   ├── auth/                           # Auth model fixtures
│   │   ├── auth-group.json
│   │   ├── auth-permission.json
│   │   └── auth-user.json
│   ├── handlers/                       # Handler model fixtures
│   │   └── handlers-organization.json
│   ├── modules/                        # Module model fixtures
│   │   ├── modules-activitytype.json
│   │   ├── modules-derivedstatus.json
│   │   └── modules-statuschoice.json
│   └── wagtailcore/                    # Wagtail core model fixtures
│       ├── lms-coursespage.json
│       ├── pages-aboutpage.json
│       ├── pages-contactpage.json
│       ├── pages-homepage.json
│       ├── pages-teampage.json
│       ├── wagtailcore-collection.json
│       ├── wagtailcore-groupapprovaltask.json
│       ├── wagtailcore-groupcollectionpermission.json
│       ├── wagtailcore-grouppagepermission.json
│       ├── wagtailcore-locale.json
│       ├── wagtailcore-modellogentry.json
│       ├── wagtailcore-page.json
│       ├── wagtailcore-pagelogentry.json
│       └── wagtailcore-pagesubscription.json
├── cleaned/                            # Cleaned/minimized fixture dumps
│   ├── essential-data.json
│   └── filtered-dump-data.json
├── original/                           # Original unmodified fixture dumps
│   ├── fusion-cms-data.json
│   └── wagtail_pages_dump.json
├── production/                         # Production-ready fixtures
│   ├── cleaned-dump-data.json
│   └── just-locales.json
├── seed/                               # Seed data for initial setup
│   └── homepage_content.json
├── sites/                              # Site-specific fixtures
│   └── site_dummy.json
├── test/                               # Test fixtures
│   ├── core-data.json
│   ├── initial_choices.json
│   ├── locales.json
│   ├── pages.json
│   └── users.json
```

---

## Usage by Project

| Project | Uses Fixtures? | Notes |
|---------|---------------|-------|
| **lms** | ✅ Yes | Via `loaddata` commands and `FIXTURE_DIRS` |
| **cms-fusion** | ✅ Yes | Tests and seed data loading |
| **precis-lms** | ✅ Yes | Tests and seed data loading |
| **portfolio** | ✅ Yes | Via `FIXTURE_DIRS` |
| **cypercloud** | ✅ Yes | Via `FIXTURE_DIRS` |
| **fusion-cms** | ✅ Yes | Via `FIXTURE_DIRS` |
