# 🧬 LMS — Clone Guide: Create a New Django Site from LMS Template

> Use the LMS site as a template to bootstrap a new Django site within the Structa Cloud monorepo.

---

## Overview

LMS is the most feature-complete Django site in the monorepo — with auth, courses, payments, blog, profiles, and Wagtail CMS. It's the ideal starting point for creating a new site with similar capabilities.

This guide walks through cloning LMS into a new site called `my-site`.

---

## Step 1: Copy the Site Directory

```bash
cd projects
cp -r lms my-site
```

---

## Step 2: Rename Internal References

Search and replace `lms` → `my-site` (case-sensitive, whole-word) in:

| File | What to change |
|------|---------------|
| `my-site/settings.py` | Site-specific settings paths |
| `my-site/server.py` | ASGI/WSGI entry point |
| `my-site/manage.py` | `DJANGO_SETTINGS_MODULE` |
| `my-site/Makefile` | Any site-name references |
| `my-site/plugins/*/apps.py` | AppConfig names if referencing `lms` |

```bash
# Quick find for LMS references
rg -l 'lms' my-site/ --type py
rg -l 'lms-demo' my-site/ --type py
```

---

## Step 3: Register the New Site

### Add to `sites.yml`

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  my-site:
    domain: my-site.structa.cloud
    db_name: db_mysite
    port: 5074
    path: my-site
```

### Add to `.env`

```bash
DB_NAME_MYSITE=db_mysite
MYSITE_HOST=my-site.structa.cloud
```

### Create the PostgreSQL Database

```sql
CREATE DATABASE db_mysite;
GRANT ALL PRIVILEGES ON DATABASE db_mysite TO postgres;
```

---

## Step 4: Update Docker Configuration

### Add to `.dockerignore`

```
# ── my-site ────────────────────────────────────────────────
projects/my-site/db.sqlite3
projects/my-site/staticfiles/
projects/my-site/assets/bundles/
```

### Add Docker Compose Service

Copy the LMS service definition from `applications/compose/docker-compose.applications.yml`:

```yaml
my-site-web:
  build:
    context: ../..
    dockerfile: projects/compose/Dockerfile
    args:
      PROJECT_PATH: my-site
  container_name: my-site-website
  environment:
    - WEBSITE=my-site
    - DB_NAME=${DB_NAME_MYSITE}
  networks:
    - common
  expose:
    - "5074"
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.my-site.rule=Host(`my-site.structa.cloud`)"
```

---

## Step 5: Customize the Site

### What to Change

| Layer | Files | Notes |
|-------|-------|-------|
| **Templates** | `my-site/templates/` | Replace LMS-specific templates with your site's branding |
| **Plugins** | `my-site/plugins/` | Remove courses/certifications if not needed; add custom plugins |
| **Static assets** | `my-site/assets/static/` | Replace logos, CSS variables, images |
| **Settings** | `my-site/settings.py` | Update `SITE_ID`, `SITE_NAME`, `ALLOWED_HOSTS` |
| **URLs** | `my-site/urls.py` | Map new page routes |
| **Auth** | `my-site/plugins/accounts/adapters.py` | Customize auth flow if needed |

### What to Keep

| Layer | Files | Notes |
|-------|-------|-------|
| **django-fusion** | Component system | Works identically across all sites |
| **Auth (allauth)** | Accounts plugin | Shared auth infrastructure |
| **Worker tasks** | `projects/www/worker/` | Email, content tasks are site-agnostic |
| **Shared templates** | `projects/assets/templates/` | Cross-site UI components |

---

## Step 6: Run Migrations

```bash
cd projects
make migrate WEBSITE=my-site
```

---

## Step 7: Test Locally

```bash
cd projects/my-site
make dev                    # Django dev server on :5074
make check                  # Django system checks
make test                   # Run test suite
```

---

## Step 8: Deploy

```bash
# From repo root
make deploy-app              # Builds + starts all site containers
make probe-health            # Verify /health/ endpoint
```

---

## Checklist

- [ ] Site directory copied from LMS
- [ ] Internal references renamed (`lms` → `my-site`)
- [ ] Registered in `sites.yml` with unique port and db_name
- [ ] `.env` updated with `DB_NAME_MYSITE` and `MYSITE_HOST`
- [ ] PostgreSQL database created
- [ ] `.dockerignore` updated
- [ ] Docker Compose service added
- [ ] Templates and branding customized
- [ ] Plugins pruned/added as needed
- [ ] Migrations run successfully
- [ ] Dev server starts on assigned port
- [ ] Deploy target works

---

## Related

| Resource | Path |
|----------|------|
| LMS site docs | [`README.md`](README.md) |
| LMS configuration | [`configuration.md`](configuration.md) |
| Deployment guide | [`../../guides/04-deploy.md`](../../guides/04-deploy.md) |
| Backend env setup | [`../../back-env/`](../../back-env/) |
