# 06 — Clone a Django Site

> **Time:** ~15 min | **Skill:** Intermediate  
> Clone an existing site (LMS, CTC Research, Portfolio) as a template for a new project.

---

## Overview

The Structa Cloud monorepo is designed for multi-tenancy — create a new Django site by cloning an existing one. LMS is the recommended template (most feature-complete).

For the full reference, see the [LMS Clone Guide](../projects/lms/clone-guide.md).

---

## Quick Steps

### 1. Copy & Rename

```bash
cd projects
cp -r lms my-new-site
```

### 2. Register the Site

Add to `projects/configs/settings/ENV/sites.yml`:

```yaml
sites:
  my-new-site:
    domain: mysite.structa.cloud
    db_name: db_mysite
    port: 5074
```

### 3. Create Database

```sql
CREATE DATABASE db_mysite;
```

### 4. Add to `.env`

```bash
DB_NAME_MYSITE=db_mysite
MYSITE_HOST=mysite.structa.cloud
```

### 5. Add Docker Service

Copy the site service block in `docker-compose.applications.yml`, update `PROJECT_PATH`, port, `container_name`, labels, and `volumes`.

### 6. Customize

- Replace templates in `my-new-site/templates/`
- Remove unused plugins from `my-new-site/plugins/`
- Update `settings.py` with new `SITE_ID`

### 7. Deploy

```bash
make deploy-app
make probe-health
```

---

## Site Comparison: Which to Clone?

| Source Site | Best For | Has |
|-------------|----------|-----|
| **LMS** | Course platforms, membership sites | Auth, courses, payments, blog, profiles, Wagtail CMS |
| **CTC Research** | Consulting, training, research | Auth, blog, LMS lite, services, newsletter, events |
| **Portfolio** | Resume builders, portfolio sites | Auth, resume builder, portfolio, PDF export, blog |

---

## Related

| Resource | Path |
|----------|------|
| LMS Clone Guide (full detail) | [`projects/lms/clone-guide.md`](../projects/lms/clone-guide.md) |
| Deployment | [`04-deploy.md`](04-deploy.md) |
| Backend env setup | [`../back-env/`](../back-env/) |
| Customization guide | [`../customization/`](../customization/) |
