# 🔧 Settings Reference

> Exhaustive settings reference for all Structa Cloud Django projects. Covers shared base, site-level, and environment-specific configuration.

---

## Settings Architecture

```
┌──────────────────────────────────────┐
│  projects/configs/base/              │  ← Shared across ALL sites
│  ├── settings.py    (INSTALLED_APPS) │
│  ├── databases.py   (DB config)      │
│  ├── security.py    (CSRF, CORS)     │
│  ├── templates.py   (TEMPLATES_DIRS) │
│  └── logging.py     (Log config)     │
└──────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────┐
│  projects/configs/settings/ENV/      │  ← Environment profiles
│  ├── _development.yml  (DEBUG=True)  │
│  ├── _production.yml   (DEBUG=False) │
│  ├── database.yml      (DB URLs)     │
│  └── security.yml      (SSL, CORS)   │
└──────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────┐
│  projects/<site>/configs/            │  ← Per-site overrides
│  ├── settings.yml         (Dynaconf) │
│  ├── settings.development.yml        │
│  └── settings.production.yml         │
└──────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────┐
│  .env file                           │  ← Secrets & tokens
│  (git-ignored, per-environment)      │
└──────────────────────────────────────┘
```

---

## Shared Base Settings

### `projects/configs/base/settings.py`

```python
# Core Django
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Installed Apps (shared across all sites)
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "django_fusion",
    # Project apps (conditionally loaded)
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_fusion.core.middlewares.SiteMiddleware",
]
```

### `projects/configs/base/databases.py`

```python
import os
from dynaconf import settings as dyna_settings

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(os.path.dirname(__file__), "../../db.sqlite3"),
    }
}

# PostgreSQL override via Dynaconf
db_name = dyna_settings.get("DB_NAME", os.getenv("DB_NAME"))
db_user = dyna_settings.get("DB_USER", os.getenv("DB_USER", "postgres"))
db_password = dyna_settings.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))
db_host = dyna_settings.get("DB_HOST", os.getenv("DB_HOST", "localhost"))
db_port = dyna_settings.get("DB_PORT", os.getenv("DB_PORT", "5432"))

if db_name:
    DATABASES["default"].update({
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": db_user,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
    })
```

### `projects/configs/base/templates.py`

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # 1. Site root templates (highest priority)
            os.path.join(SITE_ROOT, "templates"),
            # 2. Site asset templates
            os.path.join(SITE_ROOT, "assets", "templates"),
            # 3. Shared workspace templates
            os.path.join(WORKSPACE_ROOT, "assets", "templates"),
            # 4. Shared layout templates
            os.path.join(WORKSPACE_ROOT, "assets", "templates", "layout"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

### `projects/configs/base/security.py`

```python
# CSRF
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# CORS
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# Sessions
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# SSL
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

---

## Environment Profiles

### `projects/configs/settings/ENV/database.yml`

```yaml
development:
  DB_NAME: ""
  # Uses SQLite

demo:
  DB_NAME: "db_structa_demo"
  DB_HOST: "postgres"

production:
  DB_NAME: "@env DB_NAME"
  DB_HOST: "postgres"
  DB_PORT: 5432
  DB_USER: "@env DB_USER"
  DB_PASSWORD: "@env DB_PASSWORD"

staging:
  DB_NAME: "db_structa_staging"
  DB_HOST: "postgres"

testing:
  DB_NAME: ""  # SQLite for tests
```

### `projects/configs/settings/ENV/_development.yml`

```yaml
development:
  DEBUG: true
  EMAIL_STRATEGY: "console"
  SECRET_KEY: "dev-secret-key-not-for-production"
```

### `projects/configs/settings/ENV/_production.yml`

```yaml
production:
  DEBUG: false
  EMAIL_STRATEGY: "smtp"
```

### `projects/configs/settings/ENV/security.yml`

```yaml
production:
  SECURE_SSL_REDIRECT: true
  SESSION_COOKIE_SECURE: true
  CSRF_COOKIE_SECURE: true
```

---

## Per-Site Settings

### LMS (`projects/lms/configs/settings.yml`)

```yaml
default:
  SITE_ID: 2
  SITE_NAME: "Structa LMS"
  DB_NAME: "@env DB_NAME_LMS"
  ALLOWED_HOSTS:
    - "lms.structa.cloud"
    - "localhost"
    - "127.0.0.1"
  SITE_DOMAIN: "lms.structa.cloud"
```

### Portfolio (`projects/portfolio/configs/settings.yml`)

```yaml
default:
  SITE_ID: 3
  SITE_NAME: "VResume"
  DB_NAME: "@env DB_NAME_VRESUME"
  ALLOWED_HOSTS:
    - "vresume.structa.cloud"
    - "localhost"
    - "127.0.0.1"
  SITE_DOMAIN: "vresume.structa.cloud"
```

### Cypercloud (`projects/cypercloud/configs/settings.yml`)

```yaml
default:
  SITE_ID: 4
  SITE_NAME: "Cypercloud"
  DB_NAME: "@env DB_NAME_CYPERCLOUD"
  ALLOWED_HOSTS:
    - "cypercloud.structa.cloud"
    - "localhost"
    - "127.0.0.1"
  SITE_DOMAIN: "cypercloud.structa.cloud"
  # AI settings
  OLLAMA_HOST: "@env OLLAMA_HOST"
  OPENAI_API_KEY: "@env OPENAI_API_KEY"
  ANTHROPIC_API_KEY: "@env ANTHROPIC_API_KEY"
  GEMINI_API_KEY: "@env GEMINI_API_KEY"
```

### CTC Research (`projects/precis-ctc/configs/settings.yml`)

```yaml
default:
  SITE_ID: 1
  SITE_NAME: "CTC Research"
  DB_NAME: "@env DB_NAME_CTC"
  ALLOWED_HOSTS:
    - "ctc-research.com"
    - "www.ctc-research.com"
    - "localhost"
    - "127.0.0.1"
  SITE_DOMAIN: "ctc-research.com"
```

---

## Env Var Reference (Root `.env`)

```bash
# Postgres (shared cluster)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres

# Per-site DB names
DB_NAME_CTC=db_ctc
DB_NAME_LMS=db_lms
DB_NAME_VRESUME=db_vresume
DB_NAME_CYPERCLOUD=db_cypercloud

# AI backends
OLLAMA_HOST=http://ollama:11434
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Traefik / Cloudflare
CF_DNS_API_TOKEN=<cloudflare-api-token>

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@structa.cloud
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=true

# GitHub
github=ghp_...   # or GITHUB_TOKEN=...
```

---

## Site ID Assignment

| ID | Site | Container(s) | Port |
|----|------|-------------|------|
| 1 | CTC Research | `precis-ctc-website` | 5070 |
| 2 | Precis Main (LMS + landing) | `precis-main-backend` + `precis-main-frontend` | 8074 / 3000 |
| 3 | Portfolio compatibility service | `vresume-website` | 5072 |
| 4 | Syntara compatibility service | `syntara-backend` | project-defined |

`lms.structa.cloud` is a compatibility host for Precis Main; there is no
separate `lms-website` deployment target.

---

## WWW Sentinel Site (`projects/www/settings.py`)

```python
# Minimal settings to make Django run for shared code
# This site is NOT deployed — it exists to validate that
# projects/www/ code is importable and well-formed.

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "sentinel-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "www.urls"
WSGI_APPLICATION = None

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
    }
]
```

---

## Adding a New Site — Checklist

1. [ ] Create `projects/<site>/configs/settings.yml` with SITE_ID + DB_NAME
2. [ ] Add `DB_NAME_<SITE>` to root `.env`
3. [ ] Add `settings.development.yml` and `settings.production.yml`
4. [ ] Register in `projects/configs/settings/` if needed
5. [ ] Add WEBSITE alias in `projects/Makefile`
6. [ ] Add Traefik router in `application/proxy/configs/traefik/dynamic/`
7. [ ] Add Docker Compose override in `projects/compose/docker-compose.applications.yml`
8. [ ] Add to `.dockerignore` patterns
9. [ ] Run `make migrate WEBSITE=<site>` and `make collectstatic WEBSITE=<site>`

---

## Related

| Topic | Path |
|-------|------|
| Back-env overview | [`README.md`](README.md) |
| Per-project config | [`../projects/`](../projects/) |
| Infrastructure | [`../infrastructure/`](../infrastructure/) |
| Deployment | [`../publish/docker-deploy.md`](../publish/docker-deploy.md) |
