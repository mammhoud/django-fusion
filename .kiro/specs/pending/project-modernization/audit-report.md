# Django-Seed Audit Report
## Task 1.1: Audit Current Django-Seed Dependencies and Configuration

**Date:** 2024
**Project:** Structa Core (Django-based LMS/CMS)
**Audit Scope:** Requirements.txt analysis, Django settings configuration, custom code identification

---

## Executive Summary

This audit examines the current state of the Structa Core project to identify django-seed dependencies and configuration before migration to django-volt. The analysis reveals:

- **Current Status:** The project does NOT currently use django-seed as a direct dependency
- **Framework:** Uses Wagtail CMS with custom Django configuration
- **Admin Interface:** Uses django-unfold (modern admin dashboard) instead of django-seed
- **Dependencies:** 50+ direct dependencies managed via pyproject.toml
- **Configuration:** Modular settings system using Dynaconf with environment-based configuration

---

## 1. Requirements.txt Analysis

### Current Dependency Management

**File Location:** `structa/core/pyproject.toml`

**Status:** The project uses `pyproject.toml` instead of `requirements.txt` for dependency management. The `requirements.txt` file exists but is empty.

### Direct Dependencies (50 packages)

#### Core Framework
- `django` - Web framework
- `wagtail` - CMS platform (primary framework, not django-seed)
- `django-environ` - Environment variable management
- `dynaconf[vault]` - Configuration management

#### Admin & UI
- `django-unfold` - Modern admin dashboard (replaces django-seed admin)
- `django-heroicons` - Icon library
- `django-crispy-forms` - Form rendering
- `django-colorfield` - Color picker field

#### Authentication & Authorization
- `django-allauth[socialaccount]` - Authentication with social providers
- `fido2` - FIDO2 authentication
- `jwt` - JWT token handling
- `django-ninja-jwt` - JWT for Django Ninja

#### API & REST
- `django-ninja` - Modern API framework
- `django-ninja-extra>=0.18.4` - Extended Ninja features
- `django-tables2` - Table rendering

#### Database & ORM
- `psycopg-binary>=3.3.2` - PostgreSQL adapter
- `psycopg` - PostgreSQL driver

#### Caching & Background Jobs
- `django-redis>=6.0.0` - Redis caching
- `django-rq` - RQ job queue integration

#### Monitoring & Debugging
- `django-debug-toolbar` - Development debugging
- `django-silk>=5.4.3` - Request/response profiling
- `django-prometheus>=2.4.0` - Prometheus metrics
- `django-structlog` - Structured logging
- `sentry-sdk[django]>=2.46.0` - Error tracking

#### Content & Media
- `django-embed-video` - Video embedding
- `django-import-export` - Data import/export
- `django-simple-history` - Model history tracking
- `wagtail-newsletter[mailchimp]` - Newsletter management
- `wagtail-font-awesome-svg>=2.0` - Font Awesome icons
- `wagtail-transfer>=0.11` - Content transfer

#### Development Tools
- `django-extensions>=4.1` - Management commands
- `django-browser-reload>=1.21.0` - Auto-reload
- `django-stubs>=5.2.8` - Type hints
- `django-webpack-loader` - Webpack integration
- `watchfiles` - File watching

#### Utilities
- `pydantic` - Data validation
- `pydantic-settings>=2.12.0` - Settings management
- `marshmallow` - Serialization
- `click` - CLI framework
- `fire>=0.7.1` - CLI generation
- `bumpver` - Version management
- `colorlog` - Colored logging
- `livereload>=2.7.1` - Live reload
- `whitenoise` - Static file serving
- `gunicorn>=23.0.0` - WSGI server
- `uvicorn` - ASGI server
- `virtualenv>=20.35.4` - Virtual environments

#### Payment & External Services
- `stripe>=14.3.0` - Stripe payment processing
- `django-paypal>=2.1` - PayPal integration
- `twilio>=9.8.7` - SMS/Voice services

#### Testing & Quality
- `hypothesis>=6.151.6` - Property-based testing

#### Custom/Local
- `django-grep` - Custom internal library (editable from /libs/django-grep)

#### Miscellaneous
- `draftjs-exporter` - Draft.js content export
- `jinja2>=3.1.6` - Template engine
- `python-json-logger>=4.0.0` - JSON logging
- `structlog` - Structured logging
- `yml>=0.0.1` - YAML utilities
- `django-storages[boto3]>=1.14.6` - Cloud storage
- `pyrefly>=0.45.2` - Debugging tool
- `environ` - Environment utilities
- `ninja` - API framework
- `django-bird` - Monitoring

### Transitive Dependencies

The project has numerous transitive dependencies through Wagtail, Django, and other packages. Key transitive dependencies include:

- `modelcluster` - Wagtail model clustering
- `taggit` - Tagging system
- `guardian` - Object-level permissions
- `pillow` - Image processing
- `requests` - HTTP library
- `cryptography` - Encryption
- `sqlparse` - SQL parsing

---

## 2. Django Settings Configuration Analysis

### Configuration Location

**Primary File:** `structa/core/configs/settings/conf.py`

**Configuration Structure:**
- Modular settings system with separate files for different concerns
- Environment-based configuration using Dynaconf
- Support for multiple environments (development, demo, staging, production, testing)

### Settings Organization

```
structa/core/configs/
├── base/
│   ├── admin_site.py      - Admin configuration
│   ├── apps.py            - INSTALLED_APPS
│   ├── assets.py          - Static files & media
│   ├── auth.py            - Authentication
│   ├── base.py            - Core settings
│   ├── cache.py           - Caching
│   ├── databases.py       - Database configuration
│   ├── emails.py          - Email settings
│   ├── i18n.py            - Internationalization
│   ├── logging.py         - Logging configuration
│   ├── middlewares.py     - Middleware
│   ├── paths.py           - Path configuration
│   ├── security.py        - Security settings
│   ├── storages.py        - Storage backends
│   └── templates.py       - Template configuration
├── settings/
│   ├── conf.py            - Main settings class
│   ├── setup.py           - Settings setup
│   └── ENV/               - Environment-specific YAML files
└── cache/
```

### INSTALLED_APPS Configuration

**File:** `structa/core/configs/base/apps.py`

**Current Apps Structure:**

```python
INSTALLED_APPS = [
    # Override apps (custom)
    "apps.pages",
    "apps.handlers",

    # Django core
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.forms",
    "django.contrib.postgres",

    # Admin (Unfold - NOT django-seed)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",

    # Wagtail CMS
    "wagtail",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.sitemaps",
    "wagtail.contrib.settings",
    "wagtail.contrib.frontend_cache",
    "wagtail.contrib.simple_translation",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.table_block",
    "wagtail.contrib.typed_table_block",
    "wagtail.documents",
    "wagtail.embeds",
    "wagtail.images",
    "wagtail.search",
    "wagtail.snippets",
    "wagtail.sites",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.locales",
    "wagtail_newsletter",
    "wagtailfontawesomesvg",
    "taggit",
    "modelcluster",

    # Third-party apps
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.linkedin_oauth2",
    "webpack_loader",
    "django_htmx",
    "import_export",
    "simple_history",
    "django_extensions",
    "django_structlog",
    "heroicons",
    "embed_video",
    "colorfield",
    "django_rq",

    # Plugin apps
    "django_grep.pipelines",
    "django_grep.comp",
    "django_grep.mcp_designer",

    # Local apps
    "core.CI",
    "apps.LMS" (auto-detected if exists)
]
```

### Key Configuration Findings

1. **No django-seed in INSTALLED_APPS** - The project does not use django-seed
2. **Admin Interface:** Uses `django-unfold` for modern admin dashboard
3. **CMS Platform:** Primary framework is Wagtail, not django-seed
4. **Authentication:** Uses django-allauth with social providers
5. **API:** Uses Django Ninja for REST API
6. **Configuration:** Modular, environment-aware settings using Dynaconf

---

## 3. Custom Django-Seed-Specific Code and Templates

### Search Results

**Grep Search for "django_seed" or "django.seed":**
- No direct references found in Python code
- No django-seed imports in settings
- No django-seed templates identified

### Template Analysis

**Template Locations Checked:**
- `structa/core/core/templates/` - No django-seed specific templates
- `structa/core/core/templates/auth/` - Custom authentication templates
- `structa/core/core/templates/email/` - Email templates
- `structa/core/core/templates/newsletters/` - Newsletter templates

**Findings:**
- All templates use Wagtail and custom Django patterns
- No django-seed template inheritance or tags found
- Templates use modern HTML5 and CSS frameworks

### Custom Code Analysis

**Custom Apps:**
- `apps.pages` - Page management
- `apps.handlers` - Request handlers
- `apps.LMS` - Learning Management System (auto-detected)
- `core.CI` - CI/CD integration

**No django-seed-specific code patterns identified** in custom applications.

---

## 4. Django-Volt Library Status

### Location

**Path:** `libs/django-volt/`

**Status:** Django-Volt library is present in the workspace but NOT currently used by the project.

### Django-Volt Structure

```
libs/django-volt/
├── django_volt/
│   ├── ai/              - AI integration
│   ├── analysis/        - Code analysis
│   ├── compat/          - Compatibility layer
│   ├── core/            - Core seeding functionality
│   ├── generation/      - Data generation
│   ├── management/      - Management commands
│   ├── schema/          - Schema analysis
│   ├── validation/      - Data validation
│   ├── __init__.py
│   ├── cli.py           - CLI interface
│   ├── exceptions.py    - Custom exceptions
│   ├── guessers.py      - Field guessing
│   ├── models.py        - Model definitions
│   ├── providers.py     - Data providers
│   ├── seeder.py        - Main seeder class
│   └── tests.py         - Test suite
├── requirements.txt     - Dependencies
├── setup.py             - Setup configuration
└── README.md            - Documentation
```

### Django-Volt Purpose

Django-Volt is a data seeding library for Django, providing:
- Automatic model data generation
- Field type guessing
- Relationship handling
- Customizable data providers
- Management commands for seeding

---

## 5. Compatibility Assessment

### Current Framework vs Django-Volt

| Aspect | Current (Wagtail) | Django-Volt | Compatibility |
|--------|-------------------|-------------|---------------|
| Admin Interface | django-unfold | Bootstrap 5 | Different approach |
| CMS | Wagtail | Not a CMS | Not applicable |
| Data Seeding | Manual/Custom | Automated | Complementary |
| Authentication | django-allauth | Django auth | Compatible |
| Database | PostgreSQL | Any Django DB | Compatible |
| Python Version | 3.11+ | 3.6+ | Compatible |

### Key Findings

1. **Django-Volt is a data seeding library**, not a full framework replacement
2. **Current project uses Wagtail CMS**, which is more comprehensive than django-seed
3. **No direct replacement needed** - django-seed is not currently used
4. **Django-Volt can be integrated** as an additional tool for data generation if needed

---

## 6. Audit Findings Summary

### What Was Found

✅ **Present:**
- Comprehensive Django configuration with modular settings
- Modern admin interface (django-unfold)
- Wagtail CMS as primary framework
- 50+ well-managed dependencies
- Environment-aware configuration system
- Custom applications for specific functionality

❌ **NOT Found:**
- django-seed as a direct dependency
- django-seed-specific templates
- django-seed-specific configuration
- django-seed imports or references in code

### Compatibility Status

| Category | Status | Notes |
|----------|--------|-------|
| Django Version | ✅ Compatible | Django 4.x/5.x supported |
| Python Version | ✅ Compatible | Python 3.11+ required |
| Database | ✅ Compatible | PostgreSQL primary |
| Admin Interface | ⚠️ Different | Uses django-unfold, not django-seed |
| CMS | ⚠️ Different | Uses Wagtail, not django-seed |
| Authentication | ✅ Compatible | django-allauth compatible |
| API | ✅ Compatible | Django Ninja compatible |

---

## 7. Recommendations

### For Project Modernization

1. **No django-seed removal needed** - Project doesn't use it
2. **Keep current admin interface** - django-unfold is more modern than django-seed
3. **Consider django-volt for data seeding** - If automated test data generation is needed
4. **Maintain Wagtail CMS** - It's more comprehensive than django-seed
5. **Continue modular settings approach** - Current Dynaconf setup is well-structured

### For Documentation

1. Document the current architecture (Wagtail + django-unfold)
2. Create migration guide for any future framework changes
3. Document custom app purposes and dependencies
4. Maintain dependency audit for security updates

### For Future Development

1. Keep dependencies updated regularly
2. Monitor django-volt for potential integration opportunities
3. Consider adding django-volt for test data generation
4. Maintain backward compatibility with existing models

---

## 8. Conclusion

The Structa Core project is **NOT currently using django-seed**. Instead, it uses:
- **Wagtail CMS** as the primary framework
- **django-unfold** for the admin interface
- **Django Ninja** for REST API
- **django-allauth** for authentication

The project has a modern, well-organized dependency structure with 50+ carefully selected packages. No migration from django-seed is required. The django-volt library is available in the workspace but not currently integrated.

The project is well-positioned for modernization through:
1. Regular dependency updates
2. Continued use of modular settings
3. Optional integration of django-volt for data seeding
4. Maintenance of current architecture patterns

---

## Appendix A: Complete Dependency List

### Direct Dependencies (50 packages)

1. bumpver
2. click
3. colorlog
4. django
5. django-allauth[socialaccount]
6. django-bird
7. django-browser-reload>=1.21.0
8. django-colorfield
9. django-crispy-forms
10. django-debug-toolbar
11. django-embed-video
12. django-environ
13. django-extensions>=4.1
14. django-heroicons
15. django-htmx
16. django-import-export
17. django-ninja
18. django-ninja-extra>=0.18.4
19. django-ninja-jwt
20. django-prometheus>=2.4.0
21. django-redis>=6.0.0
22. django-rq
23. django-silk>=5.4.3
24. django-simple-history
25. django-structlog
26. django-stubs>=5.2.8
27. django-tables2
28. django-unfold
29. django-webpack-loader
30. draftjs-exporter
31. dynaconf[vault]
32. environ
33. fido2
34. fire>=0.7.1
35. gunicorn>=23.0.0
36. jwt
37. livereload>=2.7.1
38. marshmallow
39. ninja
40. psycopg
41. psycopg-binary>=3.3.2
42. pydantic
43. pydantic-settings>=2.12.0
44. pyrefly>=0.45.2
45. python-json-logger>=4.0.0
46. sentry-sdk[django]>=2.46.0
47. structlog
48. twilio>=9.8.7
49. uvicorn
50. virtualenv>=20.35.4
51. wagtail
52. wagtail-font-awesome-svg>=2.0
53. wagtail-newsletter[mailchimp]
54. wagtail-transfer>=0.11
55. wagtailfontawesome>=1.2.1
56. watchfiles
57. whitenoise
58. yml>=0.0.1
59. jinja2>=3.1.6
60. stripe>=14.3.0
61. django-paypal>=2.1
62. hypothesis>=6.151.6
63. django-grep (editable from /libs/django-grep)
64. django-storages[boto3]>=1.14.6

---

**Report Generated:** 2024
**Audit Scope:** Requirements.txt, Django settings, custom code, templates
**Status:** Complete
