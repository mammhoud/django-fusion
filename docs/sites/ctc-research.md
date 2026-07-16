# CTC Research

Canonical path: `core/ctc-research/`

## Overview

CTC Research site. Module: CMS.

## Key settings

```python
# core/ctc-research/settings.py
SITE_ID = 1
ROOT_URLCONF = "ctc_research.urls"
```

## Local apps

- `plugins.accounts`
- `plugins.profile`
- `plugins.blog`
- `plugins.lms`
- `www.apps.*`
- `www.core.*`

## Auth adapter

`core/ctc-research/plugins/accounts/adapters.py`

Uses `RegistrationAdapter` and `AuthHTMXSocialAccountAdapter`.

## Components

Common fragments:

| Fragment | Template |
|---|---|
| `home.main` | `core/ctc-research/templates/home/main.html` |
| `about.main` | `core/ctc-research/templates/about/main.html` |
| `services.index` | `core/ctc-research/www/core/content/models/pages/services.py` |
| `contact.main` | `core/ctc-research/www/core/content/models/pages/contact.py` |

## Commands

```bash
cd core
make check WEBSITE=ctc-research
make docker-up WEBSITE=ctc-research
```
