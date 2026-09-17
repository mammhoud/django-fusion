---
title: Clone Site
description: Clone an existing Django site (LMS, CTC Research) as a template for a new multi-tenant project.
navigation:
  title: Clone Site
  icon: i-lucide-package
object:
  type: "guide"
  id: "guide.clone-site"
attributes:
  source_path: "guides/07-clone-site.md"
  canonical_route: "/docs/en/guides/07-clone-site"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - clone-site
  - multi-tenancy
  - django
  - template
links:
  - label: "Customize"
    to: "/guides/06-customize"
    icon: "i-lucide-palette"
  - label: "Best Practices"
    to: "/guides/08-best-practices"
    icon: "i-lucide-check"
---

# 📦 Clone Site — Multi-Tenant Template

> **Time:** ~15 min | **Skill:** Intermediate
> Clone an existing site (LMS, CTC Research) as a template for a new project.

---

## Overview

The Structa Cloud monorepo is designed for multi-tenancy — create a new Django site by cloning an existing one. LMS is the recommended template (most feature-complete).

---

## Prerequisites

- Working Structa Cloud stack (`make deploy` complete)
- Target domain configured in DNS
- Admin access to PostgreSQL

---

## 1. Choose Your Template

| Template | Use Case | Source |
|----------|----------|--------|
| **LMS (precis-main)** | Courses, catalog, enrollment, progress | `projects/structa.cloud/` |
| **CTC Research** | Medical research center, publications | `projects/precis/precis-ctc/` |

> 💡 **Tip:** LMS is the most feature-complete. Start with it unless you need CTC's publication workflow.

---

## 2. Clone the Project Structure

```bash
# From repo root
cd projects/precis

# Clone precis-main to new project (e.g., precis-client)
cp -r precis-main precis-client
```

---

## 3. Update Configuration

### 3.1 Project Identity

Edit `precis-client/configs/site.yml`:

```yaml
SITE:
  name: "precis-client"
  aliases: ["client-site"]
  primary_domain: "client.example.com"
  domains: ["client.example.com", "www.client.example.com"]
  allowed_hosts: ["client.example.com", "www.client.example.com", "localhost"]
  default_email: "Client Site <noreply@client.example.com>"
  module: "CMS"
  wagtail_site_name: "Client Site"
```

### 3.2 Admin & Security

Edit `precis-client/configs/admin.yml`:

```yaml
ADMIN:
  panel_path: "/admin/"
  django_admin_path: "/django-admin/"
  wagtailadmin_base_url: "https://client.example.com"
  csrf_trusted_origins:
    - "https://client.example.com"
  cors_allowed_origins:
    - "https://client.example.com"
```

### 3.3 Static & Media

Edit `precis-client/configs/defaults.yml` (STATIC section):

```yaml
STATIC:
  deploy:
    static_volume: "precis-client-static"
    media_volume: "precis-client-media"
    static_url: "/static/"
    media_url: "/media/"
```

---

## 4. Database & Environment

### 4.1 Create Database

```bash
# Add to .env
DB_NAME_CLIENT=db_client
DB_USER_CLIENT=client_user
DB_PASS_CLIENT=secure-password

# Create in PostgreSQL
docker exec postgres psql -U admin -c "CREATE DATABASE db_client;"
docker exec postgres psql -U admin -c "CREATE USER client_user WITH PASSWORD 'secure-password';"
docker exec postgres psql -U admin -c "GRANT ALL PRIVILEGES ON DATABASE db_client TO client_user;"
```

### 4.2 Environment Variables

Add to `.env`:

```bash
# Database
DB_NAME_CLIENT=db_client
DB_USER_CLIENT=client_user
DB_PASSWORD_CLIENT=secure-password

# Site
CLIENT_PRIMARY_DOMAIN=client.example.com
CLIENT_ALLOWED_HOSTS=client.example.com,www.client.example.com
```

---

## 5. Deploy the New Site

```bash
# Build frontend
cd projects/precis/precis-client/frontend
npm install && npm run build

# Backend migrations
cd ../backend
uv run python manage.py migrate --settings=settings.production

# Collect static
uv run python manage.py collectstatic --noinput --settings=settings.production

# Create superuser
uv run python manage.py createsuperuser --settings=settings.production
```

---

## 6. Update Proxy (Traefik)

Add to `application/proxy/configs/traefik/dynamic/sites.yml`:

```yaml
http:
  routers:
    client-site:
      rule: "Host(`client.example.com`)"
      service: client-site
      tls:
        certResolver: letsencrypt-http
  services:
    client-site:
      loadBalancer:
        servers:
          - url: "http://precis-client-backend:8000"
```

Then reload:
```bash
cd application/proxy && make reload
```

---

## 6. Verify

```bash
# Health check
curl -s https://client.example.com/health

# Check Wagtail admin
open https://client.example.com/admin/
```

---

## 7. Post-Clone Checklist

- [ ] DNS A/AAAA records point to server
- [ ] SSL certificate issued (check `make probe-health`)
- [ ] Wagtail admin accessible
- [ ] Frontend loads without console errors
- [ ] API endpoints respond (`/api/`, `/apis/`)
- [ ] Static/media files served correctly
- [ ] Search indexing works
- [ ] Email sending configured (SMTP in `.env`)

---

## ## Remarks & Notes

- **Naming:** Use kebab-case for project dir (`precis-client`), PascalCase for Django app (`ClientSite`).
- **Isolation:** Each site gets its own database, static/media volumes, and Traefik router.
- **Updates:** Template updates don't auto-propagate — merge manually or use a template repo.
- **Rollback:** Keep the original template untouched; new site is independent.

---

→ [Back to Guides](README.md) | [Customize](06-customize.md) | [Best Practices](08-best-practices.md)

<!-- AI-generated: review needed -->