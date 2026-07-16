# VResume

Canonical path: `core/VResume/`

## Overview

VResume site (vresume.structa.cloud). Module: CMS.

## Key settings

```python
# core/VResume/settings.py
SITE_ID = 3
ROOT_URLCONF = "VResume.urls"
```

## Local apps

- `plugins.accounts`
- `plugins.profile`
- `plugins.blog`
- `www.pages.*`
- `www.core.*`

## Auth adapter

`core/VResume/plugins/accounts/adapters.py`

Uses `RegistrationAdapter` and `AuthHTMXSocialAccountAdapter`.

## Components

Common fragments:

| Fragment | Template |
|---|---|
| `home.main` | `core/VResume/www/pages/templates/home/main.html` |
| `about.main` | `core/VResume/www/pages/templates/about/main.html` |
| `resume.main` | `core/VResume/www/pages/templates/resume/main.html` |
| `portfolio.main` | `core/VResume/www/pages/templates/portfolio/main.html` |
| `blog.main` | `core/VResume/www/pages/templates/blog/main.html` |
| `connect.main` | `core/VResume/www/pages/templates/connect/main.html` |

## Commands

```bash
cd core
make check WEBSITE=vresume
make docker-up WEBSITE=vresume
```
