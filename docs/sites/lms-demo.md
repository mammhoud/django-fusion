# LMS Demo

Canonical path: `core/lms-demo/`

## Overview

LMS Demo site (structa.cloud). Module: LMS.

## Key settings

```python
# core/lms-demo/settings.py
SITE_ID = 2
ROOT_URLCONF = "lms_demo.urls"
```

## Local apps

- `plugins.accounts`
- `plugins.profile`
- `plugins.blog`
- `plugins.lms`
- `plugins.products`
- `www.apps.*`
- `www.core.*`

## Auth adapter

`core/lms-demo/plugins/accounts/adapters.py`

Uses `RegistrationAdapter` and `AuthHTMXSocialAccountAdapter`.

## Components

Common fragments:

| Fragment | Template |
|---|---|
| `home.main` | `core/lms-demo/templates/home/main.html` |
| `about.main` | `core/lms-demo/templates/about/main.html` |
| `courses.main` | `core/lms-demo/plugins/lms/models/courses/index.py` |
| `profile.dashboard` | `core/lms-demo/plugins/profile/views/dashboard.py` |

## Commands

```bash
cd core
make check WEBSITE=lms-demo
make docker-up WEBSITE=lms-demo
```
